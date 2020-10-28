import math
import random

# 算低位零的个数
def low_zeros(value):
    for i in range(1, 32):
        if value >> i << i != value:
            break
    return i - 1


# 通过随机数记录最大的低位零的个数
class BitKeeper(object):

    def __init__(self):
        self.maxbits = 0

    def random(self):
        value = random.randint(0, 2**32-1)
        bits = low_zeros(value)
        if bits > self.maxbits:
            self.maxbits = bits


class Experiment(object):

    def __init__(self, n):
        self.n = n
        self.keeper = BitKeeper()

    def do(self):
        for i in range(self.n):
            self.keeper.random()

    def debug(self):
        print (self.n, '%.2f' % math.log(self.n, 2), self.keeper.maxbits)

'''
在数学中，对数是幂运算的逆运算。亦即是说，假如 𝒙=𝜷^𝒚，则有
𝒚=log𝜷𝒙
其中 𝜷 是对数的底（也称为基数），而 𝒚 就是 𝒙（对于底数 𝜷）的对数。

math.log(x[, base])
使用一个参数，返回 x 的自然对数（底为 e ）。
使用两个参数，返回给定的 base 的对数 x ，计算为 log(x)/log(base) 。
math.log2(x)
返回 x 以2为底的对数。这通常比 log(x, 2) 更准确。
'''

for i in range(1000, 100000, 100):
    exp = Experiment(i)
    exp.do()
    exp.debug()
