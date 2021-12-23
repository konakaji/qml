from qmlutil.core.encoder import Encoder, DoNothingEncoder
from qmlutil.core.observable import Observable
from qmlutil.core.pqc import HEA
from qmlutil.core.wrapper import QiskitCircuit, QulacsCircuit
from qmlutil.core.const import Impl
from abc import abstractmethod
import numpy as np
import json
from math import pi


class FBase:
    @abstractmethod
    def circuit(self, vector):
        pass

    @abstractmethod
    def params(self):
        pass

    @abstractmethod
    def value(self, vector):
        pass

    @abstractmethod
    def gradient_vector(self, vector):
        pass

    @abstractmethod
    def update(self, params):
        pass

    @abstractmethod
    def dot(self, v1, v2):
        pass


class F(FBase):
    def __init__(self, encoder: Encoder, observable: Observable, nqubit, l_count, pqc_l_count, impl=Impl.QISKIT,
                 nshot=0):
        self.encoder = encoder
        self.observable = observable
        self.nqubit = nqubit
        self.l_count = l_count
        self.pqc_l_count = pqc_l_count
        self.pqcs = []
        self.impl = impl
        self.nshot = nshot
        self.reset()

    def serialize(self):
        map = {}
        map["encoder"] = self.encoder.serialize()
        map["observable"] = self.observable.serialize()
        map["nqubit"] = self.nqubit
        map["l_count"] = self.l_count
        map["pqc_l_count"] = self.pqc_l_count
        map["impl"] = self.impl.name
        map["nshot"] = self.nshot
        pqcs = []
        for pqc in self.pqcs:
            pqcs.append({"rotations": pqc.rotations,
                         "thetas": pqc.thetas,
                         "l_count": pqc.l_count})
        map["pqcs"] = pqcs
        return json.dumps(map, indent=2)

    def dot(self, v1, v2):
        s1 = self.circuit(v1)
        s2 = self.circuit(v2)
        result = 0
        for a1, a2 in zip(s1.get_state_vector(), s2.get_state_vector()):
            result = result + a1.conjugate() * a2
        return result

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
        if self.nshot != 0:
            return self.observable.sample(qc, self.nshot)
        return self.observable.exact(qc)


class Energy(F):
    def __init__(self, observable: Observable, nqubit, pqc_l_count, impl=Impl.QISKIT, nshot=0):
        super().__init__(DoNothingEncoder(), observable, nqubit, 0, pqc_l_count, impl, nshot)

    def value(self, vector=None):
        return super().value([])

    def gradient_vector(self, vector=None):
        return np.array(super().gradient_vector([]))


class Kernel(F):
    def __init__(self, encoder: Encoder, nqubit, impl=Impl.QISKIT):
        super().__init__(encoder, Observable(), nqubit=nqubit, l_count=1, pqc_l_count=0, impl=impl)
