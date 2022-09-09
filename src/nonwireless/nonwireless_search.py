"""Corresponding main.py script needs to be running on Pico."""
import sys

if "win" in sys.platform:
    # this might be different for you, check device manager --> Ports
    # https://www.tomshardware.com/how-to/detect-com-port-windows-serial-port-notifier
    com = "COM5"
else:
    com = "/dev/ttyACM0"

import sys

import serial

# open a serial connection
s = serial.Serial(com, 115200)


# %% Code Graveyard

# from lib.host_nonwireless import Talker
# t = Talker(com)
# t.send("set_color(10, 10, 10)")
