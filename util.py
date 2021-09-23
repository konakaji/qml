from qiskit import Aer
from qiskit import execute


class Const:
    simulator = Aer.get_backend('qasm_simulator')
    s_simulator = Aer.get_backend('statevector_simulator')


def get_statevector_result(qc):
    job = execute(qc, backend=Const.s_simulator)
    return job.result().get_statevector()


def get_simulator_result(qc, shots):
    job = execute(qc, backend=Const.simulator, shots=shots)
    result = job.result()
    return result.get_counts(qc)

