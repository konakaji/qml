from qmlutil.core.optimizer import Monitor
from qmlutil.core.cost import Cost
from qmlutil.core.function import FBase, Energy


class CompositeMonitor(Monitor):
    def __init__(self, monitors):
        self.monitors = monitors

    def watch(self, iter):
        for monitor in self.monitors:
            monitor.watch(iter)

    def save(self, paths):
        for monitor, path in zip(self.monitors, paths):
            monitor.save(path)


class EnergyValueMonitor(Monitor):
    def __init__(self, f: Energy, verbose=True):
        self.f = f
        self.lines = []
        self.verbose = verbose

    def watch(self, iter):
        value = self.f.value()
        line = "{}\t{}".format(iter, value)
        if self.verbose:
            print(line, flush=True)
        self.lines.append(line + "\n")

    def save(self, output):
        with open(output, 'w') as f:
            f.writelines(self.lines)


class CostValueMonitor(Monitor):
    def __init__(self, cost: Cost, f: FBase):
        self.cost = cost
        self.f = f
        self.lines = []

    def watch(self, iter):
        value = self.cost.value(self.f)
        line = "{}\t{}".format(iter, value)
        print(line, flush=True)
        self.lines.append(line + "\n")

    def save(self, output):
        with open(output, 'w') as f:
            f.writelines(self.lines)
