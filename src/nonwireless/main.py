"""https://stackoverflow.com/questions/72151781/how-can-i-get-raspberry-pi-pico-to-communicate-with-pc-external-devices"""
import sys
from time import sleep

from as7341_sensor import Sensor
from machine import Pin
from neopixel import NeoPixel

pixels = NeoPixel(Pin(28), 1)  # 1 pixel on Pin 28

sensor = Sensor()


def set_color(red, green, blue):
    pixels[0] = (red, green, blue)
    pixels.write()


def read_sensor(astep, atime, gain):
    sensor._astep = astep
    sensor._atime = atime
    sensor._gain = gain
    return sensor.all_channels


for _ in range(1):
    set_color(10, 10, 10)
    print(read_sensor(100, 999), "\n")
    sleep(1)
    set_color(0, 0, 0)
    sleep(1)

print(
    f"The following commands are available to run via host: {set_color.__name__}(r, g, b), {read_sensor.__name__}(astep, atime)\n"
)

while True:
    # read a command from the host
    v = sys.stdin.readline().strip()

    fn_name = v.split("(")[0]
    args = v.split("(")[-1].split(")")[:-1][0].replace(" ", "").split(",")

    if set_color.__name__ in fn_name:
        r, g, b = [int(a) for a in args]
        set_color(r, g, b)
    elif read_sensor.__name__ in fn_name:
        astep, atime = [int(a) for a in args]
        sensor_data = read_sensor(astep, atime)
        print(f"{sensor_data}\n")
