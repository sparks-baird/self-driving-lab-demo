from numpy.testing import assert_allclose
from self_driving_lab_demo.core import SelfDrivingLabDemo, SensorSimulator


def test_simulator():
    sim = SensorSimulator()
    channel_data = sim.simulate_sensor_data(0.5, 12, 24, 48)

    check_channel_data = (
        -5.034047338661404e-06,
        0.005718901898901329,
        0.005328294858512386,
        0.0040458290797878394,
        0.0,
        0.0035949178953476857,
        0.00015071481701215217,
        0.0,
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_simulation():
    sdl = SelfDrivingLabDemo(simulation=True)
    channel_data = sdl.observe_sensor_data(0.5, 255, 255, 255)

    check_channel_data = (
        -2.674337648663871e-05,
        0.030381666337913314,
        0.03527681080335163,
        0.04298693397274579,
        0.0,
        0.07639200527613832,
        0.0032026898615082336,
        0.0,
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_target():
    sdl = SelfDrivingLabDemo(autoload=True, simulation=True, target_seed=15)
    data = sdl.evaluate(0.25, 50, 150, 250)

    check_mae = 0.006910933400822429

    if data["mae"] != check_mae:
        raise ValueError(f"MAE is not correct: {data['mae']}")
