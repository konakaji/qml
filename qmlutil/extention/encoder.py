from qmlutil.core.wrapper import QWrapper as QuantumCircuit
from qmlutil.core.encoder import Encoder, TensorEncoder
from random import uniform
from math import pi


class VariationalEncoder(Encoder):
    def encode_with_shift(self, qc: QuantumCircuit, vector, target_index=None, angle=0):
        pass


class VariationalTensorEncoder(VariationalEncoder):
    def __init__(self, nqubit):
        self.encoder = TensorEncoder()
        self.nqubit = nqubit
        self.thetas = []
        self.reset()

    def reset(self):
        thetas = []
        for i in range(self.nqubit):
            thetas.append(uniform(0, 2 * pi))
        self.thetas = thetas

    def encode(self, qc: QuantumCircuit, vector):
        self.encode_with_shift(qc, vector)

    def encode_with_shift(self, qc: QuantumCircuit, vector, target_index=None, angle=0):
        vs = []
        for i, v in enumerate(vector):
            theta = self.thetas[i]
            if i == target_index:
                theta = theta + angle
            vs.append(v * theta)
        self.encoder.encode(qc, vs)
        pass

    def update(self, params):
        self.thetas = params
