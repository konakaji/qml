from qmlutil.core.function import F
from qmlutil.core.cost import Cost
from qmlutil.core.optimizer import Optimizer


class CircuitLearning:
    def __init__(self, function: F, cost: Cost, optimizer: Optimizer):
        self.function = function
        self.cost = cost
        self.optimizer = optimizer

    def exec(self):
        gradient_function = self.cost.build_gradient(self.function)
        self.optimizer.do_optimize(gradient_function, self.function.params())
