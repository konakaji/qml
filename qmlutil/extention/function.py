from qmlutil.core.function import FBase
from qmlutil.core.observable import Observable
from qmlutil.extention.encoder import VariationalEncoder
from qmlutil.core.pqc import HEA
from qmlutil.core.const import Impl


class WaveLearningF(FBase):
    def __init__(self, encoder: VariationalEncoder, observable: Observable, nqubit, l_count, pqc_l_count,
                 impl=Impl.QISKIT):
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
            pqcs.append(HEA(self.l_count + 1, self.pqc_l_count))
        self.pqcs = pqcs

    def circuit(self, vector):
        super().circuit(vector)

    def params(self):
        super().params()

    def value(self, vector):
        super().value(vector)

    def gradient_vector(self, vector):
        super().gradient_vector(vector)

    def update(self, params):
        super().update(params)
