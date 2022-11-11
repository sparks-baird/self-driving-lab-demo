import sys
import time

import machine
import ntptime
import uos
import urequests
from machine import SPI, Pin
from sdcard import sdcard
from uio import StringIO

# # uses a more robust ntptime
# from lib.ntptime import ntptime


def get_traceback(err):
    try:
        with StringIO() as f:  # type: ignore
            sys.print_exception(err, f)
            return f.getvalue()
    except Exception as err2:
        print(err2)
        return f"Failed to extract file and line number due to {err2}.\nOriginal error: {err}"  # noqa: E501


def initialize_sdcard(
    spi_id=1,
    cs_pin=15,
    sck_pin=10,
    mosi_pin=11,
    miso_pin=12,
    baudrate=1000000,
    polarity=0,
    phase=0,
    bits=8,
    firstbit=SPI.MSB,
    verbose=True,
):
    try:
        cs = Pin(cs_pin, Pin.OUT)

        spi = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=polarity,
            phase=phase,
            bits=bits,
            firstbit=firstbit,
            sck=Pin(sck_pin),
            mosi=Pin(mosi_pin),
            miso=Pin(miso_pin),
        )

        # Initialize SD card
        sd = sdcard.SDCard(spi, cs)

        vfs = uos.VfsFat(sd)
        uos.mount(vfs, "/sd")  # type: ignore
        if verbose:
            print("SD Card initialized successfully")
        return True
    except Exception as e:
        if verbose:
            print(get_traceback(e))
            print("SD Card failed to initialize")
        return False


def write_payload_backup(payload: str, fpath: str = "/sd/experiments.txt"):
    with open(fpath, "a") as file:
        # line = ",".join([str(payload[key]) for key in payload.keys()])
        file.write(f"{payload}\r\n")


def log_to_mongodb(
    document: dict,
    api_key: str,
    url: str,
    cluster_name: str,
    database_name: str,
    collection_name: str,
    verbose: bool = True,
):
    # based on https://medium.com/@johnlpage/introduction-to-microcontrollers-and-the-pi-pico-w-f7a2d9ad1394
    headers = {"api-key": api_key}

    insertPayload = {
        "dataSource": cluster_name,
        "database": database_name,
        "collection": collection_name,
        "document": document,
    }

    if verbose:
        print(f"sending document to {cluster_name}:{database_name}:{collection_name}")
    response = urequests.post(url, headers=headers, json=insertPayload)

    if verbose:
        print(
            "Response: (" + str(response.status_code) + "), msg = " + str(response.text)
        )
        if response.status_code == 201:
            print("Added Successfully")
        else:
            print("Error")

    # Always close response objects so we don't leak memory
    response.close()


def get_timestamp(timeout=2):
    ntptime.timeout = timeout  # type: ignore
    utc_tuple = time.gmtime(ntptime.time())
    year, month, mday, hour, minute, second, weekday, yearday = utc_tuple
    return f"{year}-{month}-{mday} {hour:02}:{minute:02}:{second:02}"


def get_onboard_temperature(unit="K"):
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    reading = sensor_temp.read_u16() * conversion_factor
    celsius_degrees = 27 - (reading - 0.706) / 0.001721
    if unit == "C":
        return celsius_degrees
    elif unit == "K":
        return celsius_degrees + 273.15
    elif unit == "F":
        return celsius_degrees * 9 / 5 + 32
    else:
        raise ValueError("Invalid unit. Must be one of 'C', 'K', or 'F")
