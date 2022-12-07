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

import numpy as np

from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data

__author__ = "sgbaird"
__copyright__ = "sgbaird"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

# ---- Python API ----


class SensorSimulator(object):
    def __init__(self):
        pass

    def simulate_sensor_data(self, parameters):
        raise NotImplementedError("This method must be implemented by a subclass.")


class SelfDrivingLabDemo(object):
    def __init__(
        self,
        random_rng=np.random.default_rng(42),
        target_seed=604523,
        rest_seconds=0.0,
        max_power=0.35,
        autoload=False,
        simulation=False,
        simulator=SensorSimulator(),
        observe_sensor_data_fn=mqtt_observe_sensor_data,
        observe_sensor_data_kwargs={},  # dict(PICO_ID="a123b456")
    ):
        self.random_rng = random_rng
        self.target_seed = target_seed
        self.rest_seconds = rest_seconds
        self.max_power = max_power
        self.autoload = autoload
        self.simulation = simulation

        self.observe_sensor_data_fn = observe_sensor_data_fn
        self.observe_sensor_data_kwargs = observe_sensor_data_kwargs

        self.simulator = simulator

        if autoload:
            # must come after creating sensor attribute
            self.observe_target_results()

    def observe_sensor_data(self, parameters):
        if self.simulation:
            return self.simulate_sensor_data(parameters)
        sleep(self.rest_seconds)

        return self.observe_sensor_data_fn(
            **parameters, **self.observe_sensor_data_kwargs
        )

    def simulate_sensor_data(self, parameters):
        return self.simulator.simulate_sensor_data(parameters)

    def get_random_inputs(self, rng=None):
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def bounds(self):
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def parameters(self):
        raise NotImplementedError("Must be implemented by subclass")

    def get_target_inputs(self):
        return self.get_random_inputs(np.random.default_rng(self.target_seed))

    def observe_target_results(self):
        self.target_results = self.observe_sensor_data(self.get_target_inputs())
        if self.target_results is None or (
            self.target_results.get("error", None) is not None
        ):
            raise RuntimeError(self.target_results["error"])
        return self.target_results

    def evaluate(self, parameters):
        raise NotImplementedError("Must be implemented by subclass")


class SDLSimulation(SelfDrivingLabDemo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_data = self.observe_target_results()

    def observe_sensor_data(self, R, G, B, atime=100, astep=999, gain=128):
        return super().observe_sensor_data(R, G, B, atime=atime, astep=astep, gain=gain)


# %% Code Graveyard

# from scipy.integrate import quad
# from scipy.stats import norm

# wavelengths, fwhms = np.array(wavelengths)

# wavelength_grid = np.arange(200, 801)

# weighted_filter = np.zeros_like(wavelength_grid)
# for wavelength, fwhm in zip(wavelengths, fwhm):
#     rv = norm(loc=wavelength, scale=fwhm / 2.355)
#     weighted_filter = weighted_filter + rv.pdf(wavelength_grid)

# target_data = list(self.target_results.values())
# data = list(results.values())

# target_dist = [[wv, pow] for wv, pow in zip(CHANNEL_WAVELENGTHS, target_data)]
# dist = [(wv, pow) for wv, pow in zip(CHANNEL_WAVELENGTHS, data)]
