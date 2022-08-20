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
from importlib.resources import open_text
from self_driving_lab_demo import data

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
        self,
        random_rng=np.random.default_rng(42),
        target_seed=604523,
        rest_seconds=0.1,
        max_brightness=0.5,
        autoload=False,
        simulation=False,
    ):
        self.random_rng = random_rng
        self.target_seed = target_seed
        self.rest_seconds = rest_seconds
        self.max_brightness = max_brightness
        self.autoload = autoload
        self.simulation = simulation

        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        self.sensor = AS7341(self.i2c)
        # https://docs.circuitpython.org/projects/as7341/en/latest/examples.html#flicker-detection
        self.sensor.flicker_detection_enabled = True

        if autoload:
            # must come after creating sensor attribute
            self.load_target_data()

    def observe_sensor_data(self, brightness, R, G, B):
        if self.simulation:
            return self.simulate_sensor_data(brightness, R, G, B)
        try:
            set_brightness(brightness)
            clear()
            # hardcoded to the pixel in the 3-position (0-indexing)
            set_pixel(3, R, G, B)
            show()
            # nir: near infrared
            # extra_channels = (self.sensor.channel_clear, self.sensor.channel_nir)
            # list of 10 values
            # channel_data = (self.sensor.all_channels + extra_channels)  
            channel_data = self.sensor.all_channels
            sleep(self.rest_seconds)
            return channel_data
        except Exception as e:
            print(e)
        finally:
            # turn off the LED at the end no matter what
            clear()
            show()

    def simulate_sensor_data(self, brightness, R, G, B):
        rI, gI, bI = brightness * np.array([R, G, B]) / 255
        red, green, blue = [open_text(module, fname) for fname in ["red.csv", "green.csv", "blue.csv"]]
        return np.array([rI, gI, bI, red, green, blue])

    def get_random_inputs(self, rng):
    df = pd.read_csv(train_csv)
        return channel_data

    def get_random_inputs(self, rng=None):
        rng = self.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than 0.5
        brightness = self.max_brightness * rng.random()
        RGB = 255 * rng.random(3)
        R, G, B = RGB.astype(int)
        return brightness, R, G, B

    @property
    def bounds(self):
        return dict(
            brightness=[0.0, self.max_brightness], R=[0, 255], G=[0, 255], B=[0, 255]
        )

    @property
    def parameters(self):
        return [
            dict(name=nm, type="range", bounds=bnd) for nm, bnd in self.bounds.items()
        ]

    @property
    def channel_names(self):
        return [
            "ch415_violet",
            "ch445_indigo",
            "ch480_blue",
            "ch515_cyan",
            "ch560_green",
            "ch615_yellow",
            "ch670_orange",
            "ch720_red",
            # "ch_clear",
            # "ch_nir",
        ]

    @property
    def channel_wavelengths(self):
        return [
            415,
            445,
            480,
            515,
            560,
            615,
            670,
            720,
            # None,
            # None,
        ]

    def get_target_inputs(self):
        return self.get_random_inputs(np.random.default_rng(self.target_seed))

    def load_target_data(self):
        self.target_data = self.observe_sensor_data(*self.get_target_inputs())
        return self.target_data

    def evaluate(self, brightness, R, G, B):
        data = self.observe_sensor_data(brightness, R, G, B)
        results = {name: datum for name, datum in zip(self.channel_names, data)}
        channel_names = self.channel_names.pop("ch_clear").pop("ch_nir")

        
        results["mae"] = mean_absolute_error(self.target_data, data)
        results["rmse"] = mean_squared_error(self.target_data, data, squared=False)
        return results


class SDLSimulation(SelfDrivingLabDemo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_data = self.load_target_data()

    @override
    def observe_sensor_data(self, brightness, R, G, B):
        return super().observe_sensor_data(brightness, R, G, B)

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

# only 2 frequencies supported, 1000 Hz, 1200 Hz (otherwise None)
# flicker_detected = self.sensor.flicker_detected
# flicker_frequency = flicker_detected if flicker_detected else 0.0

# flicker_frequency,  # unit: Hz

# osd = observe_sensor_data(
#     self.sensor, brightness, R, G, B, rest_seconds=self.rest_seconds
# )
# with osd as data:
#     return data

# from contextlib import contextmanager

# @contextmanager
# def observe_sensor_data(sensor: AS7341, brightness, R, G, B, rest_seconds=0.5):
#     # ExitStack with @stack.callback would be an alternative to try, except, finally
#     # https://docs.python.org/3/library/contextlib.html#replacing-any-use-of-try-finally-and-flag-variables
#     try:
#         set_brightness(brightness)
#         clear()
#         set_pixel(3, R, G, B)  # hardcoded to the pixel in the 3-position (0-indexing)
#         show()
#         sleep(rest_seconds)
#         # nir: near infrared
#         extra_channels = (sensor.channel_clear, sensor.channel_nir)
#         return sensor.all_channels + extra_channels  # list of 10 values
#     except Exception as e:
#         print(e)
#     finally:
#         # turn off the LED at the end no matter what
#         clear()
#         show()
