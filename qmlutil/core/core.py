from qmlutil.core.encoder import TensorEncoder
from qmlutil.core.optimizer import AdamOptimizer, UnitLRScheduler
from qmlutil.core.observable import PauliZ
from qmlutil.core.cost import MSE
from qmlutil.core.base import CircuitLearning
from qmlutil.core.function import F
from qmlutil.extention.monitor import CostValueMonitor
from math import pi, sin
import random, numpy as np
from matplotlib import pyplot as plt


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
