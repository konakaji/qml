from abc import ABC, abstractmethod
from qwrapper.circuit import init_circuit


class VQAInitializer(ABC):
    @abstractmethod
    def initialize(self):
        pass


class ZVQAInitializer(VQAInitializer):
    def __init__(self, nqubit, tool):
        self.nqubit = nqubit
        self.tool = tool

    def initialize(self):
        return init_circuit(self.nqubit, self.tool)
