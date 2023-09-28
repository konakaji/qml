from math import pi
from qwrapper.circuit import QWrapper
from qwrapper.operator import PauliTimeEvolution
from qwrapper.obs import PauliObservable
from abc import ABC, abstractmethod
import random


class PQC(ABC):
    def __init__(self, nqubit):
        self.nqubit = nqubit
        self.thetas = []

    def add(self, qc: QWrapper, params=None):
        self.add_with_shift(qc, params)

    def update(self, params):
        self.thetas = params

    def param_count(self):
        return len(self.thetas)

    @abstractmethod
    def add_with_shift(self, qc: QWrapper, params=None, target_index=None, angle=0.0):
        pass


class TimeEvolutionPQC(PQC):
    def __init__(self, nqubit):
        super().__init__(nqubit)
        self.paulis = []

    def add_time_evolution(self, pauli: PauliObservable, param):
        self.paulis.append(pauli)
        self.thetas.append(param)

    def add_with_shift(self, qc: QWrapper, params=None, target_index=None, angle=0.0):
        if params is None:
            params = self.thetas
        for j in range(len(self.paulis)):
            param = params[j]
            if j == target_index:
                param += angle / 2
            time_evolution = PauliTimeEvolution(self.paulis[j], param)
            time_evolution.add_circuit(qc)


class LayerPQC(PQC):
    def __init__(self, nqubit, l_count):
        super().__init__(nqubit)
        self.nqubit = nqubit
        self.l_count = l_count
        self.rotations = []
        self.thetas = []
        self.reset()

    def reset(self):
        results = []
        thetas = []
        for _ in range(self.nqubit * self.l_count):
            results.append(random.randint(0, 2))
            thetas.append(random.uniform(0, 4 * pi))
        self.rotations = results
        self.thetas = thetas

    def add(self, qc: QWrapper):
        self.add_with_shift(qc)

    def update(self, params):
        self.thetas = params

    def add_with_shift(self, qc: QWrapper, params=None, target_index=None, angle=0.0):
        if params is None:
            params = self.thetas
        for i in range(self.l_count):
            for j in range(self.nqubit):
                index = self.nqubit * i + j
                extra = 0
                if index == target_index:
                    extra = angle
                self.rotate(qc, self.rotations[index], params[index] + extra, j)
            self.entangle(qc, i)
            qc.barrier()

    def rotate(self, qc: QWrapper, rotation, theta, target):
        if rotation == 0:
            qc.rx(theta, target)
        elif rotation == 1:
            qc.ry(theta, target)
        elif rotation == 2:
            qc.rz(theta, target)

    def entangle(self, qc, i):
        pass


class HEA(LayerPQC):
    def entangle(self, qc: QWrapper, l_index):
        for i in range(self.nqubit):
            if i % 2 == 0 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        for i in range(self.nqubit):
            if i % 2 == 1 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        return qc


class ALT(LayerPQC):
    def __init__(self, nqubit, l_count, locality, block_l_count=1):
        super().__init__(nqubit, l_count)
        self.locality = locality
        self.block_l_count = block_l_count

    def entangle(self, qc: QWrapper, l_index):
        if l_index % (2 * self.block_l_count) < self.block_l_count:
            offset = 0
            for i in range(int(self.nqubit / self.locality)):
                self.do_entangle(qc, offset, self.locality)
                offset = offset + self.locality
        else:
            offset = 0
            for i in range(int(self.nqubit / self.locality) + 1):
                if i == 0 or i == int(self.nqubit / self.locality):
                    size = int(self.locality / 2)
                else:
                    size = self.locality
                self.do_entangle(qc, offset, size)
                offset = offset + size

    def do_entangle(self, qc, offset, size):
        for i in range(offset, offset + size):
            if i % 2 == 0 and i < offset + size - 1:
                qc.cnot(i, i + 1)
        for i in range(offset, offset + size):
            if i % 2 == 1 and i < offset + size - 1:
                qc.cnot(i, i + 1)


class TEN(LayerPQC):
    def __init__(self, nqubit, l_count, locality):
        super().__init__(nqubit, l_count)
        self.locality = locality

    def entangle(self, qc: QWrapper, l_index):
        offset = 0
        for i in range(int(self.nqubit / self.locality)):
            self.do_entangle(qc, offset)
            offset = offset + self.locality

    def do_entangle(self, qc, offset):
        for i in range(offset, offset + self.locality):
            if i % 2 == 0 and i < offset + self.locality - 1:
                qc.cnot(i, i + 1)
        for i in range(offset, offset + self.locality):
            if i % 2 == 1 and i < offset + self.locality - 1:
                qc.cnot(i, i + 1)
