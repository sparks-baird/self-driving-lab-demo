from uuid import uuid4  # universally unique identifier

from self_driving_lab_demo import SelfDrivingLabDemoLight, mqtt_observe_sensor_data
from self_driving_lab_demo.utils.search import (
    ax_bayesian_optimization,
    grid_search,
    random_search,
)

num_iter = 8

PICO_ID = "test"  # @param {type:"string"}
SESSION_ID = str(uuid4())  # random session ID
print(f"session ID: {SESSION_ID}")

sdl = SelfDrivingLabDemoLight(
    autoload=True,  # perform target data experiment automatically
    simulation=True,
    observe_sensor_data_fn=mqtt_observe_sensor_data,  # (default)
    observe_sensor_data_kwargs=dict(pico_id=PICO_ID, session_id=SESSION_ID),
)


def test_grid_search():
    grid, grid_data = grid_search(sdl, num_iter)
    assert grid is not None and grid_data is not None


def test_random_search():
    random_inputs, random_data = random_search(sdl, num_iter)
    assert random_inputs is not None and random_data is not None


def test_ax_bayesian_optimization():
    best_parameters, values, experiment, model = ax_bayesian_optimization(sdl, num_iter)
    assert (
        best_parameters is not None
        and values is not None
        and experiment is not None
        and model is not None
    )
