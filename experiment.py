from qmlutil.core.encoder import TensorEncoder
from qmlutil.core.optimizer import AdamOptimizer, UnitLRScheduler
from qmlutil.core.observable import PauliZ
from qmlutil.core.cost import MSE
from qmlutil.core.base import CircuitLearning
from qmlutil.core.function import F
from qmlutil.extention.monitor import CostValueMonitor, CompositeMonitor, FunctionMonitor, FourierMonitor
from math import pi, sin
import random, numpy as np
from matplotlib import pyplot as plt
from qmlutil.core.const import Impl


class Repository:
    def fetch(self, count):
        pass

    def theory(self, x):
        pass


class SinRepository(Repository):
    def __init__(self, noise, nqubit=1, seed=0, period=2 * pi):
        self.nqubit = nqubit
        self.noise = noise
        self.seed = seed
        self.period = period
        random.seed(self.seed)

    def fetch(self, count):
        xs = []
        ys = []
        width = self.period / count
        for i in range(count):
            x = (i + 0.5) * width + random.gauss(0, self.noise)
            eps = random.gauss(0, self.noise)
            y = self.theory(x) + eps
            xs.append([x] * self.nqubit)
            ys.append(y)
        return xs, ys

    def theory(self, x):
        return sin(x * 2 * pi / self.period)


class TwoSinRepository(Repository):
    def __init__(self, noise, nqubit=1, seed=0, period_one=2 * pi, period_two=2 / 3 * pi):
        self.nqubit = nqubit
        self.noise = noise
        self.seed = seed
        self.period_one = period_one
        self.period_two = period_two
        self.period = max(self.period_one, self.period_two)
        random.seed(self.seed)

    def fetch(self, count):
        xs = []
        ys = []
        width = self.period / count
        for i in range(count):
            x = (i + 0.5) * width + random.gauss(0, self.noise)
            eps = random.gauss(0, self.noise)
            y = self.theory(x) + eps
            xs.append([x] * self.nqubit)
            ys.append(y)
        return xs, ys

    def theory(self, x):
        return (sin(x * 2 * pi / self.period_one) + sin(x * 2 * pi / self.period_two)) / 2


def check(seed, nqubit, l_count, specific):
    if specific == None:
        return True
    if seed != specific[2] or nqubit != specific[0] or l_count != specific[1]:
        return False
    return True


if __name__ == '__main__':
    specific = None
    # specific = (4, 6, 1)
    for seed in range(1, 2):
        for nqubit in range(1, 6):
            for l_count in [2, 4, 6, 8]:
                if not check(seed, nqubit, l_count, specific):
                    continue
                print(seed, nqubit, l_count)
                pqc_l_count = 3
                prefix = "twosin2pi+2-3pi"
                repository = TwoSinRepository(0.2, nqubit=nqubit, seed=seed, period_two=2/3 * pi)
                xs, ys = repository.fetch(15)
                plt.clf()
                plt.scatter([x[0] for x in xs], ys)
                plt.grid()
                plt.plot([repository.period / 100 * i for i in range(0, 100)],
                         [repository.theory(2 * pi / 100 * i) for i in range(0, 100)])
                cost = MSE(xs, ys)
                f = F(TensorEncoder(), PauliZ(nqubit, 0), nqubit, l_count, pqc_l_count, impl=Impl.QULAC)
                plt.show()
                monitor = CompositeMonitor([CostValueMonitor(cost, f),
                                            FunctionMonitor(f, xs, ys,
                                                            "output/{}_fig_{}_{}_{}".format(prefix, nqubit, l_count,
                                                                                            seed)),
                                            FourierMonitor(f, 0, repository.period,
                                                           "output/{}_fig_fourier_{}_{}_{}".format(prefix, nqubit,
                                                                                                   l_count, seed))
                                            ])
                random.seed(seed)
                optimizer = AdamOptimizer(scheduler=UnitLRScheduler(0.1), maxiter=100, monitor=monitor)
                learning = CircuitLearning(f, cost, optimizer)
                learning.exec()
                plt.clf()
                plt.scatter([x[0] for x in xs], ys)
                plt.grid()
                plt.plot([repository.period / 100 * i for i in range(0, 100)],
                         [repository.theory(2 * pi / 100 * i) for i in range(0, 100)])
                final_xs = []
                for i in range(100):
                    final_x = []
                    for j in range(nqubit):
                        final_x.append(repository.period * i / 100)
                    final_xs.append(final_x)
                plt.plot([repository.period / 100 * i for i in range(0, 100)],
                         [f.value(final_xs[i]) for i in range(0, 100)])
                plt.savefig('output/{}_fig_{}_{}_{}.png'.format(prefix, nqubit, l_count, seed))
                monitor.save("output/{}_cost{}_{}_{}.txt".format(prefix, nqubit, l_count, seed))
