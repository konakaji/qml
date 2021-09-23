from qiskit import QuantumCircuit
from optimizer import Optimizer, AdamOptimizer, UnitLRScheduler, Monitor
from math import pi, sin
import random, util, numpy as np
from matplotlib import pyplot as plt


class Encoder:
    def encode(self, qc: QuantumCircuit, vector):
        return qc


class TensorEncoder(Encoder):
    def encode(self, qc: QuantumCircuit, vector):
        for i, v in enumerate(vector):
            qc.rz(v, i)
        return qc


class PQC:
    def __init__(self, nqubit, l_count):
        self.nqubit = nqubit
        self.l_count = l_count
        self.rotations = []
        self.thetas = []
        self.reset()

    def reset(self):
        results = []
        thetas = []
        for _ in range(self.nqubit * self.l_count):
            results.append(random.randint(0, 2))
            thetas.append(random.uniform(0, 4 * pi))
        self.rotations = results
        self.thetas = thetas

    def add(self, qc):
        self.add_with_shift(qc)

    def update(self, params):
        self.thetas = params

    def add_with_shift(self, qc, target_index=None, angle=0.0):
        for i in range(self.l_count):
            for j in range(self.nqubit):
                index = self.nqubit * i + j
                extra = 0
                if index == target_index:
                    extra = angle
                self.rotate(qc, self.rotations[index], self.thetas[index] + extra, j)
            self.entangle(qc)
            qc.barrier()

    def rotate(self, qc, rotation, theta, target):
        if rotation == 0:
            qc.rx(theta, target)
        elif rotation == 1:
            qc.ry(theta, target)
        elif rotation == 2:
            qc.rz(theta, target)

    def entangle(self, qc):
        pass


class HEA(PQC):
    def entangle(self, qc):
        for i in range(self.nqubit):
            if i % 2 == 0 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        for i in range(self.nqubit):
            if i % 2 == 1 and i != self.nqubit - 1:
                qc.cnot(i, i + 1)
        return qc


class Observable:
    def expectation(self, qc: QuantumCircuit):
        return 0


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

    def expectation(self, qc: QuantumCircuit):
        bitobj = BitObj(self.nqubit, util.get_statevector_result(qc))
        return bitobj.probability([self.target_qubit], ['0']) - bitobj.probability([self.target_qubit], ['1'])


class F:
    def __init__(self, encoder: Encoder, observable: Observable, nqubit, l_count, pqc_l_count):
        self.encoder = encoder
        self.observable = observable
        self.nqubit = nqubit
        self.l_count = l_count
        self.pqc_l_count = pqc_l_count
        self.pqcs = []
        self.reset()

    def reset(self):
        pqcs = []
        for i in range(self.l_count + 1):
            pqcs.append(HEA(self.nqubit, self.pqc_l_count))
        self.pqcs = pqcs

    def circuit(self, vector):
        return self._circuit_with_shift(vector)

    def params(self):
        results = []
        for pqc in self.pqcs:
            results.extend(pqc.thetas)
        return results

    def value(self, vector):
        return self._value_with_shift(vector)

    def gradient_vector(self, vector):
        results = []
        for l_index in range(self.l_count + 1):
            p_count = self.nqubit * self.pqc_l_count
            for p_index in range(p_count):
                results.append(self._gradient(vector, l_index, p_index))
        return results

    def update(self, params):
        for l_index in range(self.l_count):
            start = l_index * self.nqubit * self.pqc_l_count
            end = (l_index + 1) * self.nqubit * self.pqc_l_count
            self.pqcs[l_index].update(params[start:end])

    def _gradient(self, vector, l_index, p_index):
        return self._value_with_shift(vector, l_index, p_index, angle=pi / 2) \
               - self._value_with_shift(vector, l_index, p_index, angle=-pi / 2)

    def _circuit_with_shift(self, vector, l_index=None, p_index=0, angle=0.0):
        qc = QuantumCircuit(self.nqubit)
        for i in range(self.l_count):
            if i == l_index:
                self.pqcs[i].add_with_shift(qc, p_index, angle)
            else:
                self.pqcs[i].add(qc)
            self.encoder.encode(qc, vector)
            qc.barrier()
        if self.l_count == l_index:
            self.pqcs[self.l_count].add_with_shift(qc, p_index, angle)
        else:
            self.pqcs[self.nqubit].add(qc)
        return qc

    def _value_with_shift(self, vector, l_index=None, p_index=0, angle=0.0):
        qc = self._circuit_with_shift(vector, l_index, p_index, angle)
        return self.observable.expectation(qc)


def transform(self, f: F):
    N = 100  # サンプル数
    width = 2 * pi
    dt = width / N  # サンプリング間隔
    x = np.arange(0, N * dt, dt)  # 時間軸
    freq = [i / width for i in range(N)]  # 周波数軸
    nqubit = 1
    f = F(TensorEncoder(), PauliZ(nqubit, 0), nqubit, 20, 2)
    f.circuit([0]).draw('mpl')
    plt.show()
    # 振幅スペクトルを計算

    nqubit = 1
    fs = []
    for v in x:
        fs.append(f.value([v]))
    fks = np.fft.fft(fs)
    Amp = np.abs(fks) / N

    # グラフ表示
    plt.figure()
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 17
    plt.subplot(121)
    plt.plot(x, fs, label='f(n)')
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Signal", fontsize=20)
    plt.grid()
    leg = plt.legend(loc=1, fontsize=25)
    leg.get_frame().set_alpha(1)
    plt.subplot(122)
    plt.xlim([0, 5])
    plt.plot(freq, Amp, label='|F(k)|', marker="o")
    plt.xlabel('Frequency', fontsize=20)
    plt.ylabel('Amplitude', fontsize=20)
    plt.grid()
    leg = plt.legend(loc=1, fontsize=25)
    leg.get_frame().set_alpha(1)
    plt.show()


class Cost:
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    def value(self, f: F):
        return 0

    def build_gradient(self, f: F):
        def function(parameters):
            f.update(parameters)

        return function


class MSE(Cost):
    def __init__(self, xs, ys):
        super().__init__(xs, ys)

    def value(self, f: F):
        result = 0
        for i, x in enumerate(self.xs):
            y = self.ys[i]
            s = (y - f.value(x))
            result = result + s ** 2
        result = result / (2 * len(self.xs))
        return result

    def build_gradient(self, f: F):
        def function(parameters):
            f.update(parameters)
            result = [0] * len(f.params())
            for i, x in enumerate(self.xs):
                y = self.ys[i]
                coeff = -(y - f.value(x))
                vec = f.gradient_vector(x)
                result = [result[i] + coeff * v for i, v in enumerate(vec)]
            return np.array(result)

        return function


class CircuitLearning:
    def __init__(self, function: F, cost: Cost, optimizer: Optimizer):
        self.function = function
        self.cost = cost
        self.optimizer = optimizer

    def exec(self):
        gradient_function = self.cost.build_gradient(self.function)
        self.optimizer.do_optimize(gradient_function, self.function.params())


class Repository:
    def fetch(self, count):
        pass


class SinRepository:
    def __init__(self, noise, seed=0, period=2 * pi):
        self.noise = noise
        self.seed = seed
        self.period = period

    def fetch(self, count):
        xs = []
        ys = []
        random.seed(self.seed)
        for _ in range(count):
            x = random.uniform(0, self.period)
            eps = random.gauss(0, self.noise)
            y = sin(x * 2 * pi / self.period) + eps
            xs.append([x])
            ys.append(y)
        return xs, ys


class CostValueMonitor(Monitor):
    def __init__(self, cost: Cost, f: F):
        self.cost = cost
        self.f = f

    def watch(self, iter):
        print("{}\t{}".format(iter, self.cost.value(f)))


if __name__ == '__main__':
    nqubit = 1
    for l_count in [4, 6, 8]:
        pqc_l_count = 2
        repository = SinRepository(0.5, period=5 * pi)
        xs, ys = repository.fetch(30)
        plt.scatter(xs, ys)
        plt.grid()
        plt.plot([repository.period / 100 * i for i in range(0, 100)],
                 [sin(2 * pi / 100 * i) for i in range(0, 100)])
        cost = MSE(xs, ys)
        f = F(TensorEncoder(), PauliZ(nqubit, 0), nqubit, l_count, pqc_l_count)
        plt.plot([repository.period / 20 * i for i in range(0, 20)],
                 [f.value([repository.period / 20 * i]) for i in range(0, 20)])
        plt.show()
        optimizer = AdamOptimizer(scheduler=UnitLRScheduler(0.1), maxiter=40, monitor=CostValueMonitor(cost, f))
        learning = CircuitLearning(f, cost, optimizer)
        learning.exec()
        plt.clf()
        plt.scatter(xs, ys)
        plt.grid()
        plt.plot([repository.period / 100 * i for i in range(0, 100)],
                 [sin(2 * pi / 100 * i) for i in range(0, 100)])
        plt.plot([repository.period / 20 * i for i in range(0, 20)],
                 [f.value([repository.period / 20 * i]) for i in range(0, 20)])
        plt.show()
