from functools import reduce
from os import urandom

from ufastrsa.util import get_bit_length


class Random:
    def __init__(self, seed=None, rndsrc=None):
        if rndsrc is None:
            rndsrc = urandom
        self.rndsrc = rndsrc

    def getrandbits(self, k):
        if not k >= 0:
            raise ValueError("number of bits must be >= 0")
        return reduce(
            lambda x, y: x << 8 | y,
            self.rndsrc(k >> 3),
            int.from_bytes(self.rndsrc(1), "little") & ((1 << (k & 7)) - 1),
        )

    def randint(self, a, b):
        if a > b:
            raise ValueError("empty range for randint(): %d, %d" % (a, b))
        c = 1 + b - a
        k = get_bit_length(c - 1)
        while True:
            r = self.getrandbits(k)
            if r <= c:
                break
        return a + r

    def rndsrcnz(self, size):
        rv = self.rndsrc(size).replace(b"\x00", b"")
        mv = size - len(rv)
        while mv > 0:
            rv += self.rndsrc(mv).replace(b"\x00", b"")
            mv = size - len(rv)
        assert len(rv) == size
        return rv


basernd = Random()
rndsrc = basernd.rndsrc
getrandbits = basernd.getrandbits
randint = basernd.randint
rndsrcnz = basernd.rndsrcnz
