from qml.core.function import Energy
from qml.core.initializer import VQAInitializer
from qwrapper.optimizer import AdamOptimizer


class VQE:
    def __init__(self, expectation: Energy,
                 initializer: VQAInitializer,
                 optimizer: AdamOptimizer, nshot=0):
        self.expectation = expectation
        self.initializer = initializer
        self.optimizer = optimizer
        self.nshot = nshot

    def exec(self):
        def gradient(params):
            self.expectation.update(params)
            return self.expectation.gradient(self.initializer, self.nshot)

        self.optimizer.do_optimize(gradient, self.expectation.params(), self.value)

    def value(self, params=None):
        return self.expectation.value(self.initializer, self.nshot, params)
