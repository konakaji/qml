import random
from unittest import TestCase
from qml.core.initializer import ZVQAInitializer
from qml.core.function import Energy
from qml.core.pqc import TimeEvolutionPQC
from qml.core.vqe import VQE
from qwrapper.hamiltonian import HeisenbergModel
from qwrapper.obs import PauliObservable
from qwrapper.optimizer import AdamOptimizer


class TestVQE(TestCase):
    def test_exec(self):
        nqubit = 2
        seed = 31

        random.seed(seed)
        pqc = TimeEvolutionPQC(nqubit)
        pqc.add_time_evolution(PauliObservable("XI"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("YI"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("ZI"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("IX"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("IY"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("IZ"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("XX"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("YY"), random.uniform(-2, 2))
        pqc.add_time_evolution(PauliObservable("ZZ"), random.uniform(-2, 2))
        obs = HeisenbergModel(nqubit)
        energy = Energy(obs, nqubit, pqc)
        vqe = VQE(energy, ZVQAInitializer(nqubit, "qulacs"),
                  AdamOptimizer(maxiter=400))
        vqe.exec()
        self.assertAlmostEquals(vqe.value(), -2.000)
