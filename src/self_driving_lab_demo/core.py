"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
``[options.entry_points]`` section in ``setup.cfg``::

    console_scripts =
         fibonacci = ${package}.skeleton:run

Then run ``pip install .`` (or ``pip install -e .`` for editable mode)
which will install the command ``fibonacci`` inside your current environment.

Besides console scripts, the header (i.e. until ``_logger``...) of this file can
also be used as template for Python modules.

Note:
    This file can be renamed depending on your needs or safely removed if not needed.

References:
    - https://setuptools.pypa.io/en/latest/userguide/entry_point.html
    - https://pip.pypa.io/en/stable/reference/pip_install
"""

import logging
from time import sleep

import board
import numpy as np
from adafruit_as7341 import AS7341
from blinkt import clear, set_brightness, set_pixel, show
from sklearn.metrics import mean_absolute_error, mean_squared_error

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from self_driving_lab_demo.skeleton import fib`,
# when using this Python module as a library.


class SelfDrivingLabDemo(object):
    def __init__(
        self, rng=np.random.default_rng(42), rest_seconds=0.5, max_brightness=0.5
    ):
        self.rng = rng
        self.rest_seconds = rest_seconds
        self.max_brightness = max_brightness

        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.sensor = AS7341(self.i2c)
        # https://docs.circuitpython.org/projects/as7341/en/latest/examples.html#flicker-detection
        self.sensor.flicker_detection_enabled = True

    def observe_sensor_data(self, brightness, R, G, B):
        set_brightness(brightness)
        clear()
        set_pixel(3, R, G, B)  # hardcoded to the pixel in the 3-position (0-indexing)
        show()
        sleep(self.rest_seconds)
        extra_channels = [
            self.sensor.channel_clear,
            self.sensor.channel_nir,  # near infrared
            self.sensor.flicker_detected,  # unit: Hz
        ]
        data = self.sensor.all_channels + extra_channels  # list of 11 values
        clear()
        show()
        return data

    def get_random_inputs(self):
        # 1.0 is really bright, so no more than 0.5
        brightness = self.max_brightness * self.rng.random()
        RGB = 255 * self.rng.random(3)
        R, G, B = RGB.astype(int)
        return brightness, R, G, B

    def get_bounds(self):
        return dict(
            brightness=(0.0, self.max_brightness), R=(0, 255), G=(0, 255), B=(0, 255)
        )

    def get_target_inputs(self, seed=604523):
        self.targ_rng = np.random.default_rng(seed)
        return self.get_random_inputs()

    def evaluate(self, brightness, R, G, B):
        data = self.observe_sensor_data(brightness, R, G, B)
        return {
            "ch415_violet": data[0],
            "ch445_indigo": data[1],
            "ch480_blue": data[2],
            "ch515_cyan": data[3],
            "ch555_green": data[4],
            "ch590_yellow": data[5],
            "ch630_orange": data[6],
            "ch680_red": data[7],
            "ch_clear": data[8],
            "ch_nir": data[9],
            "flicker": data[10],
            "mae": mean_absolute_error(self.target_data, data),
            "rmse": mean_squared_error(self.target_data, data, squared=False),
        }


def fib(n):
    """Fibonacci example function

    Args:
      n (int): integer

    Returns:
      int: n-th Fibonacci number
    """
    assert n > 0
    a, b = 1, 1
    for _i in range(n - 1):
        a, b = b, a + b
    return a


## Code Graveyard

# _logger.debug(
#     f"Choosing random inputs. brightness: {brightness}, red: {R}, green: {G}, blue: {B}"  # noqa: E501
# )
# _logger.debug(
#     f"Setting brightness: {brightness}, red: {R}, green: {G}, blue: {B}"
# )
