import cryptolib
from machine import unique_id
from ubinascii import hexlify

my_id = hexlify(unique_id()).decode()

# key = urandom(32)
# print(key)
key = b"\x89J\xdd(\xdfl\xc2>\xaf\xe7\xb5\x92\xf0\xb3\x91\xac)*{\xf5\x85\xf3\x12\xfd]m\x87\x8dIn\x93\xd7"
cipher = cryptolib.aes(key, 1)
encrypted = cipher.encrypt(my_id)
print(encrypted)

cipher2 = cryptolib.aes(key, 1)
print(cipher2.decrypt(encrypted))
