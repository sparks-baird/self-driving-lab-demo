from ufastrsa import srandom

try:
    from _crypto import NUMBER as tomsfastmath

    pow3_ = tomsfastmath.exptmod
    invmod_ = tomsfastmath.invmod
    generate_prime_ = tomsfastmath.generate_prime

    def genprime(num=1024, test=25, safe=False):
        return generate_prime_(num, test, safe)

except ImportError:
    pow3_ = pow

    def invmod_(a, b):
        c, d, e, f, g = 1, 0, 0, 1, b
        while b:
            q = a // b
            a, c, d, b, e, f = b, e, f, a - q * b, c - q * e, d - q * f
        assert a >= 0 and c % g >= 0
        return a == 1 and c % g or 0

    def miller_rabin_pass(a, n):
        n_minus_one = n - 1
        s, d = get_lowest_set_bit(n_minus_one)
        a_to_power = pow3(a, d, n)
        if a_to_power == 1:
            return True
        for i in range(s):
            if a_to_power == n_minus_one:
                return True
            a_to_power = pow3(a_to_power, 2, n)
        if a_to_power == n_minus_one:
            return True
        return False

    class MillerRabinTest:
        def __init__(self, randint, repeat):
            self.randint = randint
            self.repeat = repeat

        def __call__(self, n):
            randint = self.randint
            n_minus_one = n - 1
            for repeat in range(self.repeat):
                a = randint(1, n_minus_one)
                if not miller_rabin_pass(a, n):
                    return False
            return True

    class GenPrime:
        def __init__(self, getrandbits, testfn):
            self.getrandbits = getrandbits
            self.testfn = testfn

        def __call__(self, bits):
            getrandbits = self.getrandbits
            testfn = self.testfn
            while True:
                p = (1 << (bits - 1)) | getrandbits(bits - 1) | 1
                if p % 3 != 0 and p % 5 != 0 and p % 7 != 0 and testfn(p):
                    break
            return p

    miller_rabin_test = MillerRabinTest(srandom.randint, 25)
    genprime = GenPrime(srandom.getrandbits, miller_rabin_test)


def pow3(x, y, z):
    return pow3_(x, y, z)


def invmod(a, b):
    return invmod_(a, b)


def get_lowest_set_bit(n):
    i = 0
    while n:
        if n & 1:
            return i, n
        n >>= 1
        i += 1
    raise "Error"


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def get_bit_length(n):
    return srandom.get_bit_length(n)


class GenRSA:
    def __init__(self, genprime):
        self.genprime = genprime

    def __call__(self, bits, e=None, with_crt=False):
        pbits = (bits + 1) >> 1
        qbits = bits - pbits
        if e is None:
            e = 65537
        elif e < 0:
            e = self.genprime(-e)
        while True:
            p = self.genprime(pbits)
            if gcd(e, p - 1) == 1:
                break
        while True:
            while True:
                q = self.genprime(qbits)
                if gcd(e, q - 1) == 1 and p != q:
                    break
            n = p * q
            if get_bit_length(n) == bits:
                break
            p = max(p, q)
        p_minus_1 = p - 1
        q_minus_1 = q - 1
        phi = p_minus_1 * q_minus_1
        d = invmod(e, phi)
        if with_crt:
            dp = d % p_minus_1
            dq = d % q_minus_1
            qinv = invmod(q, p)
            assert qinv < p
            return bits, n, e, d, p, q, dp, dq, qinv
        else:
            return bits, n, e, d


genrsa = GenRSA(genprime)
