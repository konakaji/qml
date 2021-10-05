from qmlutil.core.encoder import Encoder
from qmlutil.core.observable import Observable
from qmlutil.core.pqc import HEA
from qmlutil.core.wrapper import QiskitCircuit, QulacsCircuit
from qmlutil.core.const import Impl
from math import pi


class FBase:
    def circuit(self, vector):
        pass

    def params(self):
        pass

    def value(self, vector):
        pass

    def gradient_vector(self, vector):
        pass

    def update(self, params):
        pass


class F(FBase):
    def __init__(self, encoder: Encoder, observable: Observable, nqubit, l_count, pqc_l_count, impl=Impl.QISKIT):
        self.encoder = encoder
        self.observable = observable
        self.nqubit = nqubit
        self.l_count = l_count
        self.pqc_l_count = pqc_l_count
        self.pqcs = []
        self.impl = impl
        self.reset()

    def reset(self):
        pqcs = []
        for i in range(self.l_count + 1):
            pqcs.append(HEA(self.nqubit, self.pqc_l_count))
        self.pqcs = pqcs

    def circuit(self, vector):
        return self._circuit_with_shift(vector)

    def params(self):
        results = []
        for pqc in self.pqcs:
            results.extend(pqc.thetas)
        return results

    def value(self, vector):
        return self._value_with_shift(vector)

    def gradient_vector(self, vector):
        results = []
        for l_index in range(self.l_count + 1):
            p_count = self.nqubit * self.pqc_l_count
            for p_index in range(p_count):
                results.append(self._gradient(vector, l_index, p_index))
        return results

    def update(self, params):
        for l_index in range(self.l_count + 1):
            start = l_index * self.nqubit * self.pqc_l_count
            end = (l_index + 1) * self.nqubit * self.pqc_l_count
            self.pqcs[l_index].update(params[start:end])

    def _gradient(self, vector, l_index, p_index):
        return self._value_with_shift(vector, l_index, p_index, angle=pi / 2) \
               - self._value_with_shift(vector, l_index, p_index, angle=-pi / 2)

    def _circuit_with_shift(self, vector, l_index=None, p_index=0, angle=0.0):
        if self.impl == Impl.QISKIT:
            qc = QiskitCircuit(self.nqubit)
        else:
            qc = QulacsCircuit(self.nqubit)
        for i in range(self.l_count):
            if i == l_index:
                self.pqcs[i].add_with_shift(qc, p_index, angle)
            else:
                self.pqcs[i].add(qc)
            self.encoder.encode(qc, vector)
            qc.barrier()
        if self.l_count == l_index:
            self.pqcs[self.l_count].add_with_shift(qc, p_index, angle)
        else:
            self.pqcs[self.l_count].add(qc)
        return qc

    def _value_with_shift(self, vector, l_index=None, p_index=0, angle=0.0):
        qc = self._circuit_with_shift(vector, l_index, p_index, angle)
        return self.observable.expectation(qc)
