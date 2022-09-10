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
from importlib.resources import open_text
from time import sleep

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from similaritymeasures import frechet_dist
from sklearn.metrics import mean_absolute_error, mean_squared_error

from self_driving_lab_demo import data as data_module
from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# ---- Python API ----
# The functions defined in this section can be imported by users in their
# Python scripts/interactive interpreter, e.g. via
# `from self_driving_lab_demo.skeleton import fib`,
# when using this Python module as a library.

CHANNEL_WAVELENGTHS = [
    (410, 29),
    (440, 33),
    (470, 36),
    (510, 40),
    (550, 42),
    (583, 44),
    (620, 53),
    (670, 60),
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

CHANNEL_NAMES = [
    "ch410",
    "ch440",
    "ch470",
    "ch510",
    "ch550",
    "ch583",
    "ch620",
    "ch670",
]

wavelength_lbl = "wavelength"  # nm
intensity_lbl = "relative_intensity"  # (uW/cm^2)/nm


class SensorSimulator(object):
    def __init__(self):
        self.red_interp = self.create_interpolator("neopixel_red.csv")
        self.green_interp = self.create_interpolator("neopixel_green.csv")
        self.blue_interp = self.create_interpolator("neopixel_blue.csv")

    @property
    def channel_wavelengths(self):
        return CHANNEL_WAVELENGTHS

    @property
    def channel_hex_colors(self):
        return CHANNEL_HEX_COLORS

    def create_interpolator(self, fname):
        df = pd.read_csv(
            open_text(data_module, fname),
            header=0,
            names=[wavelength_lbl, intensity_lbl],
        )

        df[intensity_lbl].clip(lower=0.0, inplace=True)

        # average y-values for repeat x-values
        # see also https://stackoverflow.com/a/51258988/13697228
        df = df.groupby("wavelength", as_index=False).mean()

        return interp1d(
            df[wavelength_lbl],
            df[intensity_lbl],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )

    def _simulate_sensor_data(self, wavelengths, R, G, B):
        rI, gI, bI = np.array([R, G, B]) / 255

        # TODO: sample based on Gaussian distributions instead of discrete wavelengths

        wavelengths = np.array(wavelengths)[:, 0]

        channel_data = np.sum(
            [
                self.red_interp(wavelengths) * rI,
                self.green_interp(wavelengths) * gI,
                self.blue_interp(wavelengths) * bI,
            ],
            axis=0,
        )
        return {name: data for name, data in zip(CHANNEL_NAMES, channel_data)}

    def simulate_sensor_data(self, R, G, B):
        return self._simulate_sensor_data(self.channel_wavelengths, R, G, B)


class SelfDrivingLabDemo(object):
    def __init__(
        self,
        random_rng=np.random.default_rng(42),
        target_seed=604523,
        rest_seconds=0.1,
        max_brightness=0.35,
        autoload=False,
        simulation=False,
        observe_sensor_data_fn=mqtt_observe_sensor_data,
        observe_sensor_data_kwargs={},  # dict(PICO_ID="a123b456")
    ):
        self.random_rng = random_rng
        self.target_seed = target_seed
        self.rest_seconds = rest_seconds
        self.max_brightness = max_brightness
        self.autoload = autoload
        self.simulation = simulation

        self.observe_sensor_data_fn = observe_sensor_data_fn
        self.observe_sensor_data_kwargs = observe_sensor_data_kwargs

        self.simulator = SensorSimulator()

        if autoload:
            # must come after creating sensor attribute
            self.load_target_data()

    def observe_sensor_data(self, R, G, B):
        if self.simulation:
            return self.simulate_sensor_data(R, G, B)
        try:
            sleep(self.rest_seconds)
            return self.observe_sensor_data_fn(
                R, G, B, **self.observe_sensor_data_kwargs
            )
        except Exception as e:
            print(e)

    def simulate_sensor_data(self, R, G, B):
        return self.simulator.simulate_sensor_data(R, G, B)

    def get_random_inputs(self, rng=None):
        rng = self.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than `max_brightness`
        RGB = 255 * rng.random(3) * self.max_brightness
        R, G, B = np.round(RGB).astype(int)
        return int(R), int(G), int(B)

    @property
    def bounds(self):
        mx = int(np.round(self.max_brightness * 255))
        return dict(R=[0, mx], G=[0, mx], B=[0, mx])

    @property
    def parameters(self):
        return [
            dict(name=nm, type="range", bounds=bnd) for nm, bnd in self.bounds.items()
        ]

    @property
    def channel_names(self):
        return CHANNEL_NAMES

    @property
    def channel_wavelengths(self):
        return CHANNEL_WAVELENGTHS

    def get_target_inputs(self):
        return self.get_random_inputs(np.random.default_rng(self.target_seed))

    def load_target_data(self):
        self.target_results = self.observe_sensor_data(*self.get_target_inputs())
        return self.target_results

    def evaluate(self, R, G, B):
        if not hasattr(self, "target_results"):
            raise ValueError(
                "must call `load_target_data` first or instantiate with autoload=True"
            )
        results = self.observe_sensor_data(R, G, B)
        target_data = list(self.target_results.values())
        data = list(results.values())

        results["mae"] = mean_absolute_error(target_data, data)
        results["rmse"] = mean_squared_error(target_data, data, squared=False)
        results["frechet"] = frechet_dist(target_data, data)
        return results

    def clear(self):
        self.observe_sensor_data(0, 0, 0)


class SDLSimulation(SelfDrivingLabDemo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_data = self.load_target_data()

    def observe_sensor_data(self, R, G, B):
        return super().observe_sensor_data(R, G, B)


# %% Code Graveyard

# from scipy.integrate import quad
# from scipy.stats import norm

# wavelengths, fwhms = np.array(wavelengths)

# wavelength_grid = np.arange(200, 801)

# weighted_filter = np.zeros_like(wavelength_grid)
# for wavelength, fwhm in zip(wavelengths, fwhm):
#     rv = norm(loc=wavelength, scale=fwhm / 2.355)
#     weighted_filter = weighted_filter + rv.pdf(wavelength_grid)
