from qmlutil.core.function import FBase, Energy
from qmlutil.core.cost import Cost
from qmlutil.core.optimizer import Optimizer


class CircuitLearning:
    def __init__(self, function: FBase, cost: Cost, optimizer: Optimizer):
        self.function = function
        self.cost = cost
        self.optimizer = optimizer

    def exec(self):
        gradient_function = self.cost.build_gradient(self.function)
        self.optimizer.do_optimize(gradient_function, self.function.params())


class VQE:
    def __init__(self, expectation: Energy, optimizer: Optimizer):
        self.expectation = expectation
        self.optimizer = optimizer

    def exec(self):
        def gradient(params):
            self.expectation.update(params)
            return self.expectation.gradient_vector()
        self.optimizer.do_optimize(gradient, self.expectation.params())
