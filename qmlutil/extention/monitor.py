from qmlutil.core.optimizer import Monitor
from qmlutil.core.cost import Cost
from qmlutil.core.function import F
import matplotlib.pyplot as plt
import numpy as np
from math import pi


class CompositeMonitor(Monitor):
    def __init__(self, monitors):
        self.monitors = monitors

    def watch(self, iter):
        for monitor in self.monitors:
            monitor.watch(iter)

    def save(self, path):
        for monitor in self.monitors:
            monitor.save(path)


class FourierMonitor(Monitor):
    def __init__(self, f: F, start, finish, prefix, bins=100, term=10):
        self.f = f
        self.bins = bins
        self.start = start
        self.finish = finish
        self.prefix = prefix
        self.term = term

    def watch(self, iter):
        if iter % self.term != 0:
            return
        self.transform(iter)

    def transform(self, iter):
        plt.clf()
        width = self.finish - self.start
        dt = width / self.bins  # サンプリング間隔
        x = np.arange(self.start, self.bins * dt, dt)  # 時間軸
        freq = [i / width for i in range(self.bins)]  # 周波数軸
        fs = []
        for v in x:
            fs.append(self.f.value([v for _ in range(self.f.nqubit)]))
        fks = np.fft.fft(fs)
        Amp = np.abs(fks) / self.bins

        # グラフ表示
        plt.xlim([0, self.bins / (2 * width)])
        plt.ylim([0, 0.4])
        plt.grid()
        plt.plot(freq, Amp, label='|F(k)|', marker="o")
        plt.xlabel('Frequency', fontsize=20)
        plt.ylabel('Amplitude', fontsize=20)
        leg = plt.legend(loc=1, fontsize=25)
        leg.get_frame().set_alpha(1)
        plt.savefig("{}_{}.png".format(self.prefix, iter))
        plt.clf()


class FunctionMonitor(Monitor):
    def __init__(self, f: F, xs, ys, prefix, term=10):
        self.f = f
        self.xs = xs
        self.ys = ys
        self.term = term
        self.prefix = prefix

    def watch(self, iter):
        if iter % self.term != 0:
            return
        plt.clf()
        plt.scatter([x[0] for x in self.xs], self.ys)
        dim = len(self.xs[0])
        xmin = self.xs[0][0]
        xmax = self.xs[len(self.xs) - 1][0]
        xs = []
        values = []
        for i in range(101):
            x = xmin + (xmax - xmin) / 100 * i
            xs.append(x)
            array = []
            for j in range(dim):
                array.append(x)
            values.append(self.f.value(array))
        plt.grid()
        plt.plot(xs, values)
        plt.savefig('{}-{}.png'.format(self.prefix, iter))

    def save(self, path):
        pass


class CostValueMonitor(Monitor):
    def __init__(self, cost: Cost, f: F):
        self.cost = cost
        self.f = f
        self.lines = []

    def watch(self, iter):
        value = self.cost.value(self.f)
        line = "{}\t{}".format(iter, value)
        print(line)
        self.lines.append(line + "\n")

    def save(self, output):
        with open(output, 'w') as f:
            f.writelines(self.lines)
