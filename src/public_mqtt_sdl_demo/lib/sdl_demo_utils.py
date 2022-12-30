import json
import sys
from time import localtime, sleep, ticks_diff, ticks_ms  # type: ignore

import uos
from data_logging import (
    get_local_timestamp,
    get_onboard_temperature,
    write_payload_backup,
)
from machine import PWM, Pin
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


def encrypt_id(my_id, verbose=False):
    rsa_path = "rsa.json"
    # if path_exists(rsa_path):
    try:
        with open(rsa_path, "r") as f:
            cipher_data = json.load(f)
            cipher = RSA(
                cipher_data["bits"],
                n=cipher_data["n"],
                e=cipher_data["e"],
                d=cipher_data["d"],
            )
    except (KeyError, OSError) as e:
        print(e)
        print("Generating new RSA parameters...")
        bits = 256
        bits, n, e, d = genrsa(bits, e=65537)  # type: ignore
        cipher = RSA(bits, n=n, e=e, d=d)
        with open("rsa.json", "w") as f:
            json.dump(dict(bits=bits, n=n, e=e, d=d), f)

    if verbose:
        with open(rsa_path, "r") as f:
            cipher_data = json.load(f)
            print("RSA parameters (keep private):")
            print(cipher_data)

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


def get_onboard_led():
    try:
        onboard_led = Pin("LED", Pin.OUT)  # only works for Pico W
    except Exception as e:
        print(e)
        onboard_led = Pin(25, Pin.OUT)
    return onboard_led


class Experiment(object):
    def __init__(
        self,
        run_experiment_fn,
        devices,
        reset_experiment_fn=None,
        validate_inputs_fn=None,
        emergency_shutdown_fn=None,
        buzzer=None,
        sdcard_ready=False,
    ) -> None:
        self.validate_inputs_fn = validate_inputs_fn
        self.run_experiment_fn = run_experiment_fn
        self.reset_experiment_fn = reset_experiment_fn
        self.devices = devices
        self.emergency_shutdown_fn = emergency_shutdown_fn
        self.buzzer = buzzer
        self.sdcard_ready = sdcard_ready

        if self.reset_experiment_fn is None:

            def do_nothing(*args, **kwargs):
                pass

            self.reset_experiment_fn = do_nothing

        if self.emergency_shutdown_fn is None:
            self.emergency_shutdown_fn = self.reset_experiment_fn

        if self.validate_inputs_fn is None:

            def no_input_validation(*args, **kwargs):
                return True

            self.validate_inputs_fn = no_input_validation

        if self.buzzer is None:
            self.buzzer = PWM(Pin(18))

    def try_experiment(self, msg):
        payload_data = {}
        # # pin numbers not used here, but can help with organization for complex tasks
        # p = int(t[5:])  # pin number

        print(msg)

        # careful not to throw an unrecoverable error due to bad request
        # Perform the experiment and record the results
        try:
            parameters = json.loads(msg)
            payload_data["_input_message"] = parameters

            # don't allow access to hardware if any input values are out of bounds
            self.validate_inputs_fn(parameters)  # type: ignore

            beep(self.buzzer)
            sensor_data = self.run_experiment_fn(parameters, self.devices)
            payload_data = merge_two_dicts(payload_data, sensor_data)

        except Exception as err:
            print(err)
            if "_input_message" not in payload_data.keys():
                payload_data["_input_message"] = msg
            payload_data["error"] = get_traceback(err)

        try:
            payload_data["onboard_temperature_K"] = get_onboard_temperature(unit="K")
            payload_data["sd_card_ready"] = self.sdcard_ready
            stamp, time_str = get_local_timestamp(return_str=True)  # type: ignore
            payload_data["utc_timestamp"] = stamp
            payload_data["utc_time_str"] = time_str
        except OverflowError as e:
            print(get_traceback(e))
        except Exception as e:
            print(get_traceback(e))

        try:
            parameters = json.loads(msg)
            self.reset_experiment_fn(parameters, devices=self.devices)  # type: ignore
        except Exception as e:
            try:
                self.emergency_shutdown_fn(devices=self.devices)  # type: ignore
                payload_data["reset_error"] = get_traceback(e)
            except Exception as e:
                payload_data["emergency_error"] = get_traceback(e)

        return payload_data

    def write_to_sd_card(self, payload_data, fpath="/sd/experiments.txt"):
        try:
            write_payload_backup(payload_data, fpath=fpath)
        except Exception as e:
            w = f"Failed to write to SD card: {get_traceback(e)}"
            print(w)
            payload_data["warning"] = w

        return payload_data

    # def log_to_mongodb(
    #     self,
    #     payload_data,
    #     api_key: str,
    #     url: str,
    #     cluster_name: str,
    #     database_name: str,
    #     collection_name: str,
    #     verbose: bool = True,
    #     retries: int = 2,
    # ):
    #     try:
    #         log_to_mongodb(
    #             payload_data,
    #             url=url,
    #             api_key=api_key,
    #             cluster_name=cluster_name,
    #             database_name=database_name,
    #             collection_name=collection_name,
    #             verbose=verbose,
    #             retries=retries,
    #         )
    #     except Exception as e:
    #         print(f"Failed to log to MongoDB backend: {get_traceback(e)}")


def heartbeat(client, first, ping_interval_ms=15000):
    global lastping
    if first:
        client.ping()
        lastping = ticks_ms()
    if ticks_diff(ticks_ms(), lastping) >= ping_interval_ms:
        client.ping()
        lastping = ticks_ms()
    return


def sign_of_life(led, first, blink_interval_ms=5000):
    global last_blink
    if first:
        led.on()
        last_blink = ticks_ms()
    time_since = ticks_diff(ticks_ms(), last_blink)
    if led.value() == 0 and time_since >= blink_interval_ms:
        led.toggle()
        last_blink = ticks_ms()
    elif led.value() == 1 and time_since >= 500:
        led.toggle()
        last_blink = ticks_ms()


class DummyMotor:
    def __init__(self):
        pass


class DummySensor:
    def __init__(self):
        pass
