from unittest import TestCase
from qmlutil.core.pqc import TEN, ALT
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt

class TestVQE(TestCase):
    def test_exec(self):
        qc = QuantumCircuit(16)
        ALT(16, 4, 4).add(qc)
        qc.draw('mpl')
        plt.show()