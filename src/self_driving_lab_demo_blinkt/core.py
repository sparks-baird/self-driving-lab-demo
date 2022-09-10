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
import sys
from importlib.resources import open_text
from time import sleep

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from sklearn.metrics import mean_absolute_error, mean_squared_error

from self_driving_lab_demo import data as data_module

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

try:
    import board
    from adafruit_as7341 import AS7341
    from blinkt import clear, set_brightness, set_pixel, show
except (NotImplementedError, ModuleNotFoundError) as e:
    print(e)
    _logger.warning(
        "Safe to ignore if this is CI or not on a Raspberry Pi. However, only the simulator will be available."  # noqa: E501
    )

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from self_driving_lab_demo.skeleton import fib`,
# when using this Python module as a library.

CHANNEL_WAVELENGTHS = [
    415,
    445,
    480,
    515,
    560,
    615,
    670,
    720,
]

# based on https://www.johndcook.com/wavelength_to_RGB.html
CHANNEL_HEX_COLORS = [
    "#7600ed",
    "#0028ff",
    "#00d5ff",
    "#1fff00",
    "#c3ff00",
    "#ff8900",
    "#ff0000",
    "#db0000",
]


class SensorSimulator(object):
    def __init__(self):
        self.red_interp = self.create_interpolator("red.csv")
        self.green_interp = self.create_interpolator("green.csv")
        self.blue_interp = self.create_interpolator("blue.csv")

    @property
    def channel_wavelengths(self):
        return CHANNEL_WAVELENGTHS

    @property
    def channel_hex_colors(self):
        return CHANNEL_HEX_COLORS

    def create_interpolator(self, fname):
        df = pd.read_csv(
            open_text(data_module, fname),
            header=None,
            names=["wavelength", "relative_intensity"],
        )

        df["relative_intensity"].clip(lower=0.0, inplace=True)

        # average y-values for repeat x-values
        # see also https://stackoverflow.com/a/51258988/13697228
        df = df.groupby("wavelength", as_index=False).mean()

        return interp1d(
            df["wavelength"],
            df["relative_intensity"],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )

    def _simulate_sensor_data(self, wavelengths, brightness, R, G, B):
        rI, gI, bI = brightness * np.array([R, G, B], dtype=int) / 255
        channel_data = np.sum(
            [
                self.red_interp(wavelengths) * rI,
                self.green_interp(wavelengths) * gI,
                self.blue_interp(wavelengths) * bI,
            ],
            axis=0,
        )
        return tuple(channel_data)

    def simulate_sensor_data(self, brightness, R, G, B):
        return self._simulate_sensor_data(self.channel_wavelengths, brightness, R, G, B)


if "adafruit_as7341" in sys.modules:
    # uses board.SCL and board.SDA
    i2c = board.I2C()
    sensor = AS7341(i2c)
else:
    i2c = None
    sensor = None


def blinkt_observe_sensor_data(self, brightness: float, R: int, G: int, B: int):
    if self.simulation:
        return self.simulate_sensor_data(brightness, R, G, B)
    try:
        set_brightness(brightness)
        clear()
        # hardcoded to the pixel in the 3-position (0-indexing)
        set_pixel(3, R, G, B)
        show()
        # list of 8 values
        channel_data = self.sensor.all_channels
        sleep(self.rest_seconds)
        return channel_data
    except Exception as e:
        print(e)
    finally:
        # turn off the LED at the end no matter what
        clear()
        show()


class SelfDrivingLabDemo(object):
    def __init__(
        self,
        random_rng=np.random.default_rng(42),
        target_seed=604523,
        rest_seconds=0.1,
        max_brightness=0.35,
        autoload=False,
        simulation=False,
        observe_sensor_data_fn=blinkt_observe_sensor_data,
    ):
        self.random_rng = random_rng
        self.target_seed = target_seed
        self.rest_seconds = rest_seconds
        self.max_brightness = max_brightness
        self.autoload = autoload
        self.simulation = simulation

        def observe_sensor_data(brightness, R, G, B):
            return observe_sensor_data_fn(self, brightness, R, G, B)

        self.observe_sensor_data = observe_sensor_data

        self.simulator = SensorSimulator()

        if autoload:
            # must come after creating sensor attribute
            self.load_target_data()

    def simulate_sensor_data(self, brightness, R, G, B):
        return self.simulator.simulate_sensor_data(brightness, R, G, B)

    def get_random_inputs(self, rng=None):
        rng = self.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than `max_brightness`
        brightness = self.max_brightness * rng.random()
        RGB = 255 * rng.random(3)
        R, G, B = np.round(RGB).astype(int)
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
        ]

    @property
    def channel_wavelengths(self):
        return CHANNEL_WAVELENGTHS

    def get_target_inputs(self):
        return self.get_random_inputs(np.random.default_rng(self.target_seed))

    def load_target_data(self):
        self.target_data = self.observe_sensor_data(*self.get_target_inputs())
        return self.target_data

    def evaluate(self, brightness, R, G, B):
        data = self.observe_sensor_data(brightness, R, G, B)
        results = {name: datum for name, datum in zip(self.channel_names, data)}

        results["mae"] = mean_absolute_error(self.target_data, data)
        results["rmse"] = mean_squared_error(self.target_data, data, squared=False)
        return results


class SDLSimulation(SelfDrivingLabDemo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_data = self.load_target_data()

    def observe_sensor_data(self, brightness, R, G, B):
        return super().observe_sensor_data(brightness, R, G, B)


# %% Code Graveyard

# _logger.debug( f"Choosing random inputs. brightness: {brightness}, red: {R}, green:
#     {G}, blue: {B}"  # noqa: E501
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
#     #
#     https://docs.python.org/3/library/contextlib.
# html#replacing-any-use-of-try-finally-and-flag-variables
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

# red_interp = interp1d(red_df["wavelength"], red_df["relative_intensity"],
# kind="cubic", fill_value=0.0)
# green_interp = interp1d(green_df["wavelength"], green_df["relative_intensity"],
# kind="cubic", fill_value=0.0)
# blue_interp = interp1d(blue_df["wavelength"], blue_df["relative_intensity"],
# kind="cubic", fill_value=0.0)


# red_df.loc[:, "relative_intensity"] = red_df["relative_intensity"] * rI
# green_df.loc[:, "relative_intensity"] = green_df["relative_intensity"] * gI
# blue_df.loc[:, "relative_intensity"] = blue_df["relative_intensity"] * bI

# red_interp, green_interp, blue_interp = [
#     interp_color(df) for df in [red_df, green_df, blue_df]
# ]

# def _scale_by_brightness(df, scale):
#     df["relative_intensity"] = df["relative_intensity"] * scale
#     return df

# red_df, green_df, blue_df = [
#     pd.read_csv(
#         open_text(data_module, fname),
#         header=None,
#         names=["wavelength", "relative_intensity"],
#     )
#     for fname in ["red.csv", "green.csv", "blue.csv"]
# ]
# [
#     df["relative_intensity"].clip(lower=0.0, inplace=True)
#     for df in [red_df, green_df, blue_df]
# ]

# def _interp_color(df):
#     return interp1d(
#         df["wavelength"], df["relative_intensity"], kind="cubic", fill_value=0.0
#     )

# self.red_interp, self.green_interp, self.blue_interp = [
#     _interp_color(df) for df in [red_df, green_df, blue_df]
# ]

# channel_names = self.channel_names.pop("ch_clear").pop("ch_nir")

# nir: near infrared
# extra_channels = (self.sensor.channel_clear, self.sensor.channel_nir)
# channel_data = (self.sensor.all_channels + extra_channels)

# "ch_clear",
# "ch_nir",

# https://docs.circuitpython.org/projects/as7341/en/latest/examples.html#flicker-detection
# self.sensor.flicker_detection_enabled = True

# board_name = board.__name__
# sensor_name = AS7341.__name__
