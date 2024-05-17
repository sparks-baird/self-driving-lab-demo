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
from self_driving_lab_demo.utils.observe import liquid_observe_sensor_data


class SensorSimulatorLiquid(SensorSimulator):
    def __init__(self):
        pass
        # TODO: find experimental spectra for simulation (could be from this demo)
        # self.red_interp = self.create_interpolator("red_dye.csv")
        # self.yellow_interp = self.create_interpolator("yellow_dye.csv")
        # self.blue_interp = self.create_interpolator("blue_dye.csv")

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
        self, wavelengths, R, Y, B, atime=100, astep=999, gain=128
    ):
        # TODO: sample based on Gaussian distributions instead of discrete wavelengths
        wavelengths = np.array(wavelengths)[:, 0]

        channel_data = np.sum(
            [
                self.red_interp(wavelengths) * R,
                self.yellow_interp(wavelengths) * Y,
                self.blue_interp(wavelengths) * B,
            ],
            axis=0,
        )
        integration_time = (astep + 1) * (atime + 1) * 2.78 / 1000  # as7341.py
        channel_data = channel_data * integration_time * gain
        return {name: data for name, data in zip(CHANNEL_NAMES, channel_data)}

    def simulate_sensor_data(self, parameters):
        raise NotImplementedError(
            "TODO: simulate data using experimental spectra of food dyes"
        )


class SelfDrivingLabDemoLiquid(SelfDrivingLabDemo):
    def __init__(
        self,
        random_rng=np.random.default_rng(),
        target_seed=604523,
        rest_seconds=0.0,
        max_power=0.35,
        autoload=False,
        simulation=False,
        simulator=SensorSimulatorLiquid(),
        observe_sensor_data_fn=liquid_observe_sensor_data,
        observe_sensor_data_kwargs={},  # dict(PICO_ID="a123b456")
    ):
        super().__init__(
            random_rng=random_rng,
            target_seed=target_seed,
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
        R, Y, B = rng.random(3) * self.max_power
        return {"R": R, "Y": Y, "B": B}

    @property
    def bounds(self):
        mx = float(self.max_power)
        return dict(
            R=[0.0, mx],
            Y=[0.0, mx],
            B=[0.0, mx],
            w=[0.0, mx],
            prerinse_power=[0.0, mx],
            prerinse_time=[1.0, 20.0],
            runtime=[1.0, 20.0],
            atime=[0, 255],
            astep=[0, 65534],
            gain=[0.5, 512.0],
        )

    @property
    def parameters(self):
        parameters = []
        for nm, bnd in self.bounds.items():
            if nm in [
                "R",
                "Y",
                "B",
                "w",
                "prerinse_power",
                "prerinse_time",
                "runtime",
                "atime",
                "astep",
            ]:
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

        target_data = [
            float(self.target_results[ch] - self.target_results["background"][ch])
            for ch in self.channel_names
        ]
        data = [
            float(results[ch] - results["background"][ch]) for ch in self.channel_names
        ]

        results["mae"] = mean_absolute_error(target_data, data)
        results["rmse"] = root_mean_squared_error(target_data, data)

        target_dist = np.array([self.channel_wavelengths, target_data]).T
        dist = np.array([self.channel_wavelengths, data]).T
        results["frechet"] = frechet_dist(target_dist, dist)
        return results

    def clear(self):
        self.observe_sensor_data(dict(R=0, Y=0, B=0))
