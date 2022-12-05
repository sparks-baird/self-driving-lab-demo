import json
import sys
from time import sleep

import uos
from ufastrsa.genprime import genrsa
from ufastrsa.rsa import RSA
from uio import StringIO


def beep(buzzer, power=0.005):
    buzzer.freq(300)
    buzzer.duty_u16(round(65535 * power))
    sleep(0.15)
    buzzer.duty_u16(0)


def get_traceback(err):
    try:
        with StringIO() as f:  # type: ignore
            sys.print_exception(err, f)
            return f.getvalue()
    except Exception as err2:
        print(err2)
        return f"Failed to extract file and line number due to {err2}.\nOriginal error: {err}"  # noqa: E501


def merge_two_dicts(x, y):
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z


def path_exists(path):
    # Check if path exists.
    # Works for relative and absolute path.
    parent = ""  # parent folder name
    name = path  # name of file/folder

    # Check if file/folder has a parent folder
    index = path.rstrip("/").rfind("/")
    if index >= 0:
        index += 1
        parent = path[: index - 1]
        name = path[index:]

    # Searching with iterator is more efficient if the parent contains lost of files/folders
    # return name in uos.listdir(parent)
    return any((name == x[0]) for x in uos.ilistdir(parent))


def encrypt_id(my_id):
    rsa_path = "rsa.json"
    if path_exists(rsa_path):
        with open(rsa_path, "r") as f:
            cipher_data = json.load(f)
            cipher = RSA(
                cipher_data["bits"],
                n=cipher_data["n"],
                e=cipher_data["e"],
                d=cipher_data["d"],
            )
    else:
        bits = 256
        bits, n, e, d = genrsa(bits, e=65537)  # type: ignore
        cipher = RSA(bits, n=n, e=e, d=d)
        with open("rsa.json", "w") as f:
            json.dump(dict(bits=bits, n=n, e=e, d=d), f)

    my_id = int.from_bytes(cipher.pkcs_encrypt(my_id), "big")
    return my_id


def decrypt_id(my_id):
    rsa_path = "rsa.json"
    if path_exists(rsa_path):
        with open(rsa_path, "r") as f:
            cipher_data = json.load(f)
            cipher = RSA(
                cipher_data["bits"],
                n=cipher_data["n"],
                e=cipher_data["e"],
                d=cipher_data["d"],
            )
    else:
        bits = 256
        bits, n, e, d = genrsa(bits, e=65537)  # type: ignore
        cipher = RSA(bits, n=n, e=e, d=d)
        with open("rsa.json", "w") as f:
            json.dump(dict(bits=bits, n=n, e=e, d=d), f)

    my_id = int.from_bytes(cipher.pkcs_decrypt(my_id), "big")
    return my_id
