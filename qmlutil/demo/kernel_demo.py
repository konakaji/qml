from qmlutil.core.function import Kernel
from qmlutil.core.encoder import TensorEncoder

if __name__ == '__main__':
    enc = TensorEncoder()
    kernel = Kernel(encoder=enc, nqubit=2)
    print("kernel", kernel.dot([0.5], [2.5]))
