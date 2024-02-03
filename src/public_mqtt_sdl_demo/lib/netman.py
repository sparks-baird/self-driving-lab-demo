#              .';:cc;.
#            .,',;lol::c.
#            ;';lddddlclo
#            lcloxxoddodxdool:,.
#            cxdddxdodxdkOkkkkkkkd:.
#          .ldxkkOOOOkkOO000Okkxkkkkx:.
#        .lddxkkOkOOO0OOO0000Okxxxxkkkk:
#       'ooddkkkxxkO0000KK00Okxdoodxkkkko
#      .ooodxkkxxxOO000kkkO0KOxolooxkkxxkl
#      lolodxkkxxkOx,.      .lkdolodkkxxxO.
#      doloodxkkkOk           ....   .,cxO;
#      ddoodddxkkkk:         ,oxxxkOdc'..o'
#      :kdddxxxxd,  ,lolccldxxxkkOOOkkkko,
#       lOkxkkk;  :xkkkkkkkkOOO000OOkkOOk.
#        ;00Ok' 'O000OO0000000000OOOO0Od.
#         .l0l.;OOO000000OOOOOO000000x,
#            .'OKKKK00000000000000kc.
#               .:ox0KKKKKKK0kdc,.
#                      ...
#
# Author: peppe8o
# Date: Jul 24th, 2022
# Version: 1.0
# https://peppe8o.com

# modified by @sgbaird from source:
# https://peppe8o.com/getting-started-with-wifi-on-raspberry-pi-pico-w-and-micropython/

import time

import network
import rp2
from ubinascii import hexlify


def connectWiFi(ssid, password, country=None, wifi_energy_saver=False, retries=3):
    for _ in range(retries):
        try:
            if country is not None:
                # https://www.google.com/search?q=wifi+country+codes
                rp2.country(country)
            wlan = network.WLAN(network.STA_IF)
            if not wifi_energy_saver:
                wlan.config(pm=0xA11140)  # avoid the energy-saving WiFi mode
            wlan.active(True)

            mac = hexlify(network.WLAN().config("mac"), ":").decode()
            print(f"MAC address: {mac}")

            wlan.connect(ssid, password)
            # Wait for connect or fail
            max_wait = 10
            while max_wait > 0:
                if wlan.status() < 0 or wlan.status() >= 3:
                    break
                max_wait -= 1
                print("waiting for connection...")
                time.sleep(1)

            # Handle connection error
            if wlan.status() != 3:
                raise RuntimeError("network connection failed")
            else:
                print("connected")
                status = wlan.ifconfig()
                print("ip = " + status[0])
            return status
        except RuntimeError as e:
            print(f"Attempt failed with error: {e}. Retrying...")
    raise RuntimeError(
        "All attempts to connect to the network failed. Ensure you are using a 2.4 GHz WiFi network with WPA-2 authentication. See the additional prerequisites section from https://doi.org/10.1016/j.xpro.2023.102329 or the https://github.com/sparks-baird/self-driving-lab-demo/issues/76 for additional troubleshooting help."
    )
