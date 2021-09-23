from math import pi
import random


class PQC:
    def __init__(self, nqubit, l_count):
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

    def add(self, qc):
        self.add_with_shift(qc)

    def update(self, params):
        self.thetas = params

    def add_with_shift(self, qc, target_index=None, angle=0.0):
        for i in range(self.l_count):
            for j in range(self.nqubit):
                index = self.nqubit * i + j
                extra = 0
                if index == target_index:
                    extra = angle
                self.rotate(qc, self.rotations[index], self.thetas[index] + extra, j)
            self.entangle(qc)
            qc.barrier()

    def rotate(self, qc, rotation, theta, target):
        if rotation == 0:
            qc.rx(theta, target)
        elif rotation == 1:
            qc.ry(theta, target)
        elif rotation == 2:
            qc.rz(theta, target)

    def entangle(self, qc):
        pass


class HEA(PQC):
    def entangle(self, qc):
        for i in range(self.nqubit):
            if i % 2 == 0 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        for i in range(self.nqubit):
            if i % 2 == 1 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        return qc
