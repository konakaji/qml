from qml.core.pqc import PQC
from qwrapper.obs import Hamiltonian
from math import pi
import numpy as np


class Energy:
    def __init__(self, observable: Hamiltonian, nqubit, pqc: PQC):
        self.observable = observable
        self.nqubit = nqubit
        self.pqc = pqc

    def update(self, params):
        self.pqc.update(params)

    def params(self):
        return self.pqc.thetas

    def value(self, initializer, nshot, params=None):
        qc = initializer.initialize()
        self.pqc.add(qc, params)
        return self.observable.get_value(qc, nshot)

    def gradient(self, initializer, nshot):
        grads = []
        for j in range(self.pqc.param_count()):
            qc = initializer.initialize()
            self.pqc.add_with_shift(qc, target_index=j, angle=pi / 2)
            plus = self.observable.get_value(qc, nshot)

            qc = initializer.initialize()
            self.pqc.add_with_shift(qc, target_index=j, angle=-pi / 2)
            minus = self.observable.get_value(qc, nshot)
            grads.append(plus - minus)
        return np.array(grads)
