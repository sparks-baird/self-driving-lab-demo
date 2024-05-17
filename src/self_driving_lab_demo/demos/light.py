from importlib.resources import open_text

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from similaritymeasures import frechet_dist
from sklearn.metrics import mean_absolute_error

try:
    from sklearn.metrics import root_mean_squared_error
except ImportError:
    from sklearn.metrics import mean_squared_error

    def root_mean_squared_error(y_true, y_pred):
        return np.sqrt(mean_squared_error(y_true, y_pred))


from self_driving_lab_demo import data as data_module
from self_driving_lab_demo.core import SelfDrivingLabDemo, SensorSimulator
from self_driving_lab_demo.utils.channel_info import (
    CHANNEL_HEX_COLORS,
    CHANNEL_NAMES,
    CHANNEL_WAVELENGTHS_MEAN_FWHM,
)
from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data


class SensorSimulatorLight(SensorSimulator):
    def __init__(self):
        self.red_interp = self.create_interpolator("neopixel_red.csv")
        self.green_interp = self.create_interpolator("neopixel_green.csv")
        self.blue_interp = self.create_interpolator("neopixel_blue.csv")

    @property
    def channel_wavelengths(self):
        return CHANNEL_WAVELENGTHS_MEAN_FWHM

    @property
    def channel_hex_colors(self):
        return CHANNEL_HEX_COLORS

    def create_interpolator(self, fname):
        wavelength_lbl = "wavelength"  # nm
        intensity_lbl = "relative_intensity"  # (uW/cm^2)/nm

        df = pd.read_csv(
            open_text(data_module, fname),
            header=0,
            names=[wavelength_lbl, intensity_lbl],
        )

        df["relative_intensity"] = df["relative_intensity"].clip(lower=0.0)

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

    def _simulate_sensor_data(
        self, wavelengths, R, G, B, atime=100, astep=999, gain=128
    ):
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
        integration_time = (astep + 1) * (atime + 1) * 2.78 / 1000  # as7341.py
        channel_data = channel_data * integration_time * gain
        return {name: data for name, data in zip(CHANNEL_NAMES, channel_data)}

    def simulate_sensor_data(self, parameters):
        R = parameters["R"]
        G = parameters["G"]
        B = parameters["B"]
        atime = parameters.get("atime", 100)
        astep = parameters.get("astep", 999)
        gain = parameters.get("gain", 128)
        return self._simulate_sensor_data(
            self.channel_wavelengths, R, G, B, atime=atime, astep=astep, gain=gain
        )


class SelfDrivingLabDemoLight(SelfDrivingLabDemo):
    def __init__(
        self,
        random_rng=np.random.default_rng(),
        target_seed=604523,
        target_inputs=None,
        rest_seconds=0.0,
        max_power=0.35,
        autoload=False,
        simulation=False,
        simulator=SensorSimulatorLight(),
        observe_sensor_data_fn=mqtt_observe_sensor_data,
        observe_sensor_data_kwargs={},  # dict(PICO_ID="a123b456")
    ):
        """
        This class extends the SelfDrivingLabDemo class to simulate a self-driving
        lab demo with light sensors.

        Parameters
        ----------
        random_rng : numpy random generator, optional
            The random number generator used for generating random inputs, by
            default np.random.default_rng()
        target_seed : int, optional
            The seed used for generating target inputs, as long as target_inputs is
            not set directly using the class attribute, by default 604523
        target_inputs : dict, optional
            The target inputs for the demo, by default None
        rest_seconds : float, optional
            The rest time in seconds between actions, by default 0.0
        max_power : float, optional
            The maximum power for the light from 0.0 to 1.0, by default 0.35
        autoload : bool, optional
            Whether to load target data automatically, by default False
        simulation : bool, optional
            Whether to run in simulation mode, by default False
        simulator : SensorSimulatorLight, optional
            The simulator used for the demo, by default SensorSimulatorLight()
        observe_sensor_data_fn : function, optional
            The function used to observe sensor data, by default
            mqtt_observe_sensor_data
        observe_sensor_data_kwargs : dict, optional
            The keyword arguments for the observe_sensor_data function, by default
            {}

        Examples
        --------
        >>> demo = SelfDrivingLabDemoLight(
        ...     random_rng=np.random.default_rng(),
        ...     target_seed=604523,
        ...     target_inputs=None,
        ...     rest_seconds=0.0,
        ...     max_power=0.35,
        ...     autoload=True,
        ...     simulation=False,
        ...     simulator=SensorSimulatorLight(),
        ...     observe_sensor_data_fn=mqtt_observe_sensor_data,
        ...     observe_sensor_data_kwargs={},
        ... )
        >>> demo.evaluate(dict(R=50, G=150, B=250))
        """
        super().__init__(
            random_rng=random_rng,
            target_seed=target_seed,
            target_inputs=target_inputs,
            rest_seconds=rest_seconds,
            max_power=max_power,
            autoload=autoload,
            simulation=simulation,
            simulator=simulator,
            observe_sensor_data_fn=observe_sensor_data_fn,
            observe_sensor_data_kwargs=observe_sensor_data_kwargs,
        )

    def get_random_inputs(self, rng=None):
        rng = self.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than `max_brightness`
        RGB = 255 * rng.random(3) * self.max_power
        R, G, B = np.round(RGB).astype(int)
        return {"R": int(R), "G": int(G), "B": int(B)}

    @property
    def bounds(self):
        mx = int(np.round(self.max_power * 255))
        return dict(
            R=[0, mx],
            G=[0, mx],
            B=[0, mx],
            atime=[0, 255],
            astep=[0, 65534],
            gain=[0.5, 512],
        )

    @property
    def parameters(self):
        parameters = []
        for nm, bnd in self.bounds.items():
            if nm in ["R", "G", "B", "atime", "astep"]:
                parameters.append(dict(name=nm, type="range", bounds=bnd))
            elif nm in ["gain"]:
                parameters.append(
                    dict(
                        name=nm,
                        type="choice",
                        is_ordered=True,
                        values=[
                            0.5,
                            1.0,
                            2.0,
                            4.0,
                            8.0,
                            16.0,
                            32.0,
                            64.0,
                            128.0,
                            256.0,
                            512.0,
                        ],
                    )
                )
            else:
                raise ValueError(f"unknown parameter {nm}")
        return parameters

    @property
    def channel_names(self):
        return CHANNEL_NAMES

    @property
    def channel_wavelengths_mean_fwhm(self):
        return CHANNEL_WAVELENGTHS_MEAN_FWHM

    @property
    def channel_wavelengths(self):
        return [ch[0] for ch in self.channel_wavelengths_mean_fwhm]

    def evaluate(self, parameters):
        if not hasattr(self, "target_results"):
            raise ValueError(
                "must call `load_target_data` first or instantiate with autoload=True"
            )
        results = self.observe_sensor_data(parameters)
        if results.get("error", None) is not None:
            raise ValueError(results["error"])

        target_data = [float(self.target_results[ch]) for ch in self.channel_names]
        data = [float(results[ch]) for ch in self.channel_names]

        results["mae"] = mean_absolute_error(target_data, data)
        results["rmse"] = root_mean_squared_error(target_data, data)

        target_dist = np.array([self.channel_wavelengths, target_data]).T
        dist = np.array([self.channel_wavelengths, data]).T
        results["frechet"] = frechet_dist(target_dist, dist)
        return results

    def clear(self):
        self.observe_sensor_data(dict(R=0, G=0, B=0))
