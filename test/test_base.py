from unittest import TestCase
from qmlutil.core.function import Energy
from qmlutil.core.vqa import VQE
from qmlutil.core.observable import PauliZ
from qmlutil.core.const import Impl
from qmlutil.core.optimizer import AdamOptimizer
from qmlutil.core.monitor import EnergyValueMonitor


class TestVQE(TestCase):
    def test_exec(self):
        energy = Energy(PauliZ(3, 0), 3, 4, Impl.QULAC)
        optimizer = AdamOptimizer(monitor=EnergyValueMonitor(energy))
        vqe = VQE(energy, optimizer)
        vqe.exec()
