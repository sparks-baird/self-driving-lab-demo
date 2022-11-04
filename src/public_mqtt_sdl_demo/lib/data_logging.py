import time

import ntptime
import requests
import uos
from machine import SPI, Pin
from sdcard import sdcard


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
        return True
    except Exception as e:
        print(e)
        return False


def write_payload_backup(payload: str, fpath: str = "experiments.txt"):
    with open(fpath, "a") as file:
        # line = ",".join([str(payload[key]) for key in payload.keys()])
        file.write(f"{payload}\r\n")


def log_to_mongodb(
    payload: str,
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
        "document": payload,
    }

    if verbose:
        print("sending...")
    response = requests.post(url, headers=headers, json=insertPayload)

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


def get_timestamp():
    utc_tuple = time.gmtime(ntptime.time() + 946684800)
    year, month, mday, hour, minute, second, weekday, yearday = utc_tuple
    return f"{year}-{month}-{mday} {hour}:{minute}:{second}"
