from qmlutil.core.wrapper import QWrapper as QuantumCircuit
from abc import abstractmethod, ABC


class Encoder(ABC):
    def encode(self, qc: QuantumCircuit, vector):
        return qc

    @abstractmethod
    def serialize(self):
        return "encoder"

    @abstractmethod
    def max_eigenvalues(self, dim):
        return [0] * dim


class TensorEncoder(Encoder):
    def encode(self, qc: QuantumCircuit, vector):
        for i, v in enumerate(vector):
            qc.rz(v, i)
        return qc

    def serialize(self):
        return "tensorz"

    def max_eigenvalues(self, dim):
        return [0.5] * dim


class DoNothingEncoder(Encoder):
    def serialize(self):
        return "doNothing"

    def max_eigenvalues(self, dim):
        return super(DoNothingEncoder, self).max_eigenvalues(dim)


