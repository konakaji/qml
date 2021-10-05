import numpy as np
from qmlutil.core.function import FBase


class Cost:
    def __init__(self, xs, ys):
        self.xs = xs
        self.ys = ys

    def value(self, f: FBase):
        return 0

    def build_gradient(self, f: FBase):
        def function(parameters):
            f.update(parameters)

        return function


class MSE(Cost):
    def __init__(self, xs, ys):
        super().__init__(xs, ys)

    def value(self, f: FBase):
        result = 0
        for i, x in enumerate(self.xs):
            y = self.ys[i]
            s = (y - f.value(x))
            result = result + s ** 2
        result = result / (2 * len(self.xs))
        return result

    def build_gradient(self, f: FBase):
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
