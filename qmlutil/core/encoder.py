from qmlutil.core.wrapper import QWrapper as QuantumCircuit


class Encoder:
    def encode(self, qc: QuantumCircuit, vector):
        return qc


class TensorEncoder(Encoder):
    def encode(self, qc: QuantumCircuit, vector):
        for i, v in enumerate(vector):
            qc.rz(v, i)
        return qc
