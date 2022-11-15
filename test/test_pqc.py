from unittest import TestCase
from qmlutil.core.pqc import ALT
from qwrapper.circuit import init_circuit


class TestVQE(TestCase):
    def test_exec(self):
        qc = init_circuit(4, "qiskit")
        ALT(4, 8, 2, block_l_count=2).add(qc)
