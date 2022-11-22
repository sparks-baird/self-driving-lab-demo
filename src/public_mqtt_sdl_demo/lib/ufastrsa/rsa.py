from ufastrsa.genprime import pow3
from ufastrsa.srandom import rndsrcnz


class RSA:
    def __init__(self, bits, n=None, e=None, d=None):
        self.bits = bits
        self.bytes = (bits + 7) >> 3
        self.n = n
        self.e = e
        self.d = d
        self.rndsrcnz = rndsrcnz

    def pkcs_sign(self, value):
        len_padding = self.bytes - 3 - len(value)
        assert len_padding >= 0, len_padding
        base = int.from_bytes(
            b"\x00\x01" + len_padding * b"\xff" + b"\x00" + value, "big"
        )
        return int.to_bytes(pow3(base, self.d, self.n), self.bytes, "big")

    def pkcs_verify(self, value):
        assert len(value) == self.bytes
        signed = int.to_bytes(
            pow3(int.from_bytes(value, "big"), self.e, self.n), self.bytes, "big"
        )
        idx = signed.find(b"\0", 1)
        assert idx != -1 and signed[:idx] == b"\x00\x01" + (idx - 2) * b"\xff"
        return signed[idx + 1 :]

    def pkcs_encrypt(self, value):
        len_padding = self.bytes - 3 - len(value)
        assert len_padding >= 0
        base = int.from_bytes(
            b"\x00\x02" + self.rndsrcnz(len_padding) + b"\x00" + value, "big"
        )
        return int.to_bytes(pow3(base, self.e, self.n), self.bytes, "big")

    def pkcs_decrypt(self, value):
        assert len(value) == self.bytes
        decrypted = int.to_bytes(
            pow3(int.from_bytes(value, "big"), self.d, self.n), self.bytes, "big"
        )
        idx = decrypted.find(b"\0", 2)
        assert idx != -1 and decrypted[:2] == b"\x00\x02"
        return decrypted[idx + 1 :]
