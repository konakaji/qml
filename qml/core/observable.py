from qmlutil.core.wrapper import QWrapper as QuantumCircuit
from abc import abstractmethod, ABC


class Observable(ABC):
    def exact(self, qc: QuantumCircuit):
        return 0

    def sample(self, qc: QuantumCircuit, nshot):
        return 0

    @abstractmethod
    def serialize(self):
        return "observable"


class BitObj:
    def __init__(self, nqubit, state_vector):
        results = []
        for i, v in enumerate(state_vector):
            bit_str = format(i, 'b').zfill(nqubit)
            array = []
            for j in range(0, nqubit):
                array.append(bit_str[nqubit - j - 1])
            results.append((array, v))
        self.coefficients = results

    def probability(self, target_bit_indices, values):
        if len(target_bit_indices) != len(values):
            raise AttributeError
        result = 0
        for r in self.coefficients:
            bit_array = r[0]
            if not self.is_target(bit_array, target_bit_indices, values):
                continue
            v = r[1]
            result = result + abs(v * v)
        return result

    def is_target(self, array, bit_indices, values):
        for i, index in enumerate(bit_indices):
            if array[index] != values[i]:
                return False
        return True


class PauliZ(Observable):
    def __init__(self, nqubit, target_qubit):
        self.nqubit = nqubit
        self.target_qubit = target_qubit

    def exact(self, qc: QuantumCircuit):
        bitobj = BitObj(self.nqubit, qc.get_state_vector())
        return bitobj.probability([self.target_qubit], ['0']) - bitobj.probability([self.target_qubit], ['1'])

    def sample(self, qc: QuantumCircuit, nshot):
        pass

    def serialize(self):
        return "pauliz"
