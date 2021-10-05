from scipy.stats import unitary_group
from qiskit import Aer
from qiskit import QuantumCircuit, execute
import random, math, numpy


class Const:
    simulator = Aer.get_backend('qasm_simulator')


class Util:
    @classmethod
    def get_result(cls, qc, shots):
        job = execute(qc, backend=Const.simulator, shots=shots)
        result = job.result()
        return result.get_counts(qc)

    @classmethod
    def generate_random(cls, locality, num_products):
        result = []
        for _ in range(num_products):
            u = unitary_group.rvs(pow(2, locality))
            result.append(u)
        return result


class Encoder:
    def append(self, qc: QuantumCircuit, xs, dagger=False):
        return qc


class TensorEncoder:
    def __init__(self, n):
        self.n = n
        self.name = "tensor"

    def append(self, qc: QuantumCircuit, xs):
        sign = 1
        for i in range(self.n):
            qc.rz(sign * xs[i], i)
        return qc


class EntangleEncoder:
    def __init__(self, n):
        self.n = n
        self.tencoder = TensorEncoder(n)
        self.name = "entangle"

    def append(self, qc: QuantumCircuit, xs):
        qc = self.tencoder.append(qc, xs)
        for i in range(self.n):
            if i == self.n - 1:
                break
            qc.cnot(i, i + 1)
        return qc

class Repetition:
    def __init__(self, encoder, locality, num_products, l):
        us = []
        for i in range(l + 1):
            u_array = Util.generate_random(locality, num_products)
            us.append(u_array)
        self.us = us
        self.encoder = encoder
        self.locality = locality
        self.nqubit = locality * num_products
        self.l = l

    def append(self, qc: QuantumCircuit, x):
        for i, u in enumerate(self.us[0]):
            start = self.locality * i
            end = self.locality * (i + 1)
            qc.unitary(u, [q for q in range(start, end)])
        qc.barrier()
        for i in range(self.l):
            self.encoder.append(qc, x)
            qc.barrier()
            for j, u in enumerate(self.us[i + 1]):
                start = self.locality * j
                end = self.locality * (j + 1)
                qc.unitary(u, [q for q in range(start, end)])
            qc.barrier()
        return qc


def generate_data(nqubit, num):
    results = []
    for i in range(num):
        result = []
        for j in range(nqubit):
            result.append(random.uniform(0, math.pi))
        results.append(result)
    return results


def sigmaz(results, index, shots):
    result = 0
    for key, value in results.items():
        bit = int(key[index])
        if bit == 0:
            result = result + value
        else:
            result = result - value
    return result / shots


def derivative(xs, repetition1, repetition2, encoder, theta, nqubit):
    return shift_cost(xs, repetition1, repetition2, encoder, theta, nqubit) \
           - shift_cost(xs, repetition1, repetition2, encoder, theta, nqubit, True)


def shift_cost(xs, repetition1, repetition2, encoder, theta, nqubit, minus=False):
    qc = QuantumCircuit(nqubit)
    repetition1.append(qc, xs)
    sign = 1
    if minus:
        sign = -1
    qc.rz(theta + sign * math.pi / 2, 0)
    encoder.append(qc, xs)
    repetition2.append(qc, xs)
    qc.measure_all()
    result = sigmaz(Util.get_result(qc, 100), 0, 100)
    return result


def exp(xs, encoder, nqubit, locality, L, l):
    theta = math.pi / 4
    num_products = int(nqubit / locality)
    repetition = Repetition(encoder, locality, num_products, l=l)
    repetition2 = Repetition(encoder, locality, num_products, l=L - l)
    d = derivative(xs, repetition, repetition2, encoder, theta, nqubit)
    return d


if __name__ == '__main__':
    with open('output/variances.txt', "w") as f:
        for nqubit in [2, 4, 6, 8, 10, 12, 14]:
            xs = generate_data(nqubit, 1)[0]
            for locality in [1, nqubit]:
                for encoder in [EntangleEncoder(nqubit), TensorEncoder(nqubit)]:
                    vs = []
                    count = 100
                    for k in range(count):
                        v = exp(xs, encoder, nqubit, locality, 10, 3)
                        vs.append(v * v)
                        if k % 10 == 0:
                            print(nqubit, locality, encoder.name, k)
                    f.write("{}\t{}\t{}\t{}\t{}\n".format(encoder.name, nqubit, locality, numpy.mean(vs), numpy.std(vs) / math.sqrt(count)))
