from ufastrsa.rsa import RSA, genrsa


def main():
    bits = 512
    print("RSA bits", bits)
    r = RSA(*genrsa(bits, e=65537))
    if r:
        print("RSA OK")
        data = b"a message to sign and encrypt via RSA"
        print("random data len:", len(data), data)
        assert r.pkcs_verify(r.pkcs_sign(data)) == data
        print("pkcs_verify OK")
        assert r.pkcs_decrypt(r.pkcs_encrypt(data)) == data
        print("pkcs_decrypt OK")
        print(dir(r))


if __name__ == "__main__":
    main()
