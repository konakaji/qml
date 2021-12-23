from qmlutil.core.wrapper import QWrapper as QuantumCircuit
from abc import abstractmethod, ABC


class Encoder(ABC):
    def encode(self, qc: QuantumCircuit, vector):
        return qc

    @abstractmethod
    def serialize(self):
        return "encoder"


class TensorEncoder(Encoder):
    def encode(self, qc: QuantumCircuit, vector):
        for i, v in enumerate(vector):
            qc.rz(v, i)
        return qc

    def serialize(self):
        return "tensorz"


class DoNothingEncoder(Encoder):
    def serialize(self):
        return "doNothing"
