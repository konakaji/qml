from qiskit import QuantumCircuit
from qiskit import Aer
from qiskit import execute
from qulacs import QuantumState


class Const:
    simulator = Aer.get_backend('qasm_simulator')
    s_simulator = Aer.get_backend('statevector_simulator')


class QWrapper:
    def h(self, index):
        pass

    def rx(self, theta, index):
        pass

    def ry(self, theta, index):
        pass

    def rz(self, theta, index):
        pass

    def measure_all(self):
        pass

    def barrier(self):
        pass

    def draw(self):
        pass

    def get_counts(self, nshot):
        pass

    def get_state_vector(self):
        pass


class QulacsCircuit(QWrapper):
    def __init__(self, nqubit):
        self.qc = QuantumState(nqubit)

    def h(self, index):
        super().h(index)

    def rx(self, theta, index):
        pass

    def ry(self, theta, index):
        pass

    def rz(self, theta, index):
        pass

    def measure_all(self):
        super().measure_all()

    def barrier(self):
        super().barrier()

    def draw(self):
        super().draw()

    def get_counts(self, nshot):
        super().get_counts(nshot)

    def get_state_vector(self):
        super().get_state_vector()


class QiskitCircuit(QWrapper):
    def __init__(self, nqubit):
        self.qc = QuantumCircuit(nqubit)

    def h(self, index):
        self.qc.h(index)

    def rx(self, theta, index):
        self.qc.rx(theta, index)

    def ry(self, theta, index):
        self.qc.ry(theta, index)

    def rz(self, theta, index):
        self.qc.rz(theta, index)

    def measure_all(self):
        self.qc.measure_all()

    def barrier(self):
        self.qc.barrier()

    def draw(self):
        self.qc.draw()

    def get_counts(self, nshot):
        job = execute(self.qc, backend=Const.simulator, shots=nshot)
        result = job.result()
        return result.get_counts(self.qc)

    def get_state_vector(self):
        job = execute(self.qc, backend=Const.s_simulator)
        return job.result().get_statevector()
