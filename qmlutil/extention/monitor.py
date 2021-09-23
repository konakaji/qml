from qmlutil.core.optimizer import Monitor
from qmlutil.core.cost import Cost
from qmlutil.core.function import F


class CostValueMonitor(Monitor):
    def __init__(self, cost: Cost, f: F):
        self.cost = cost
        self.f = f

    def watch(self, iter):
        print("{}\t{}".format(iter, self.cost.value(self.f)))
