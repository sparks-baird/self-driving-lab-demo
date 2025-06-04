import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "self-driving-lab-demo"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from self_driving_lab_demo.core import SelfDrivingLabDemo, SensorSimulator
from self_driving_lab_demo.demos.light import (
    SelfDrivingLabDemoLight,
    SensorSimulatorLight,
)
from self_driving_lab_demo.demos.liquid import (
    SelfDrivingLabDemoLiquid,
    SensorSimulatorLiquid,
)
from self_driving_lab_demo.utils.observe import (
    get_paho_client,
    liquid_observe_sensor_data,
    mqtt_observe_sensor_data,
    pico_server_observe_sensor_data,
)
from self_driving_lab_demo.utils.search import (
    grid_search,
    random_search,
)

__all__ = [
    "SelfDrivingLabDemo",
    "SelfDrivingLabDemoLight",
    "SelfDrivingLabDemoLiquid",
    "SensorSimulator",
    "SensorSimulatorLight",
    "SensorSimulatorLiquid",
    "mqtt_observe_sensor_data",
    "liquid_observe_sensor_data",
    "pico_server_observe_sensor_data",
    "grid_search",
    "random_search",
    "get_paho_client",
]
