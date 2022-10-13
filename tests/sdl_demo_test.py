from uuid import uuid4

import numpy as np
from numpy.testing import assert_allclose, assert_almost_equal

from self_driving_lab_demo.core import SelfDrivingLabDemo, SensorSimulator
from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data
from self_driving_lab_demo_blinkt.core import (
    SelfDrivingLabDemo as SelfDrivingLabDemoBlinkt,
)
from self_driving_lab_demo_blinkt.core import SensorSimulator as SensorSimulatorBlinkt


def test_simulator():
    sim = SensorSimulator()
    channel_data = list(sim.simulate_sensor_data(12, 24, 48).values())

    check_channel_data = list(
        {
            "ch410": 831.9335717568799,
            "ch440": 23725.516359642614,
            "ch470": 106513.2068240609,
            "ch510": 20932.375096245254,
            "ch550": 5801.1374228586865,
            "ch583": 814.2217065931691,
            "ch620": 7801.0437457016815,
            "ch670": 128.9444509888443,
        }.values()
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_simulation():
    sdl = SelfDrivingLabDemo(simulation=True)
    channel_data = list(sdl.observe_sensor_data(255, 255, 255).values())

    check_channel_data = list(
        {
            "ch410": 5873.769415281079,
            "ch440": 126604.6683886277,
            "ch470": 567304.2531959089,
            "ch510": 205813.93125487852,
            "ch550": 60388.716698840944,
            "ch583": 9302.065621007128,
            "ch620": 164522.29171205347,
            "ch670": 1733.6117327615912,
        }.values()
    )

    assert_allclose(channel_data, check_channel_data)

    fidelity_channel_data = list(
        sdl.observe_sensor_data(
            255, 255, 255, atime=100 * 2, astep=999 * 2, gain=128 * 2
        ).values()
    )

    check_fidelity_channel_data = np.array(check_channel_data) * 8
    # large relative tolerance since not exactly 8 times larger
    # this is due to the calculation of integration time
    assert_allclose(fidelity_channel_data, check_fidelity_channel_data, rtol=0.01)


def test_sdl_demo_target():
    sdl = SelfDrivingLabDemo(autoload=True, simulation=True, target_seed=15)
    data = sdl.evaluate(50, 150, 250)

    check_mae = 87146.7286109353
    check_rmse = 177834.9903063588
    check_frechet = 485588.9246047528

    assert_almost_equal(data["mae"], check_mae, decimal=5)
    assert_almost_equal(data["rmse"], check_rmse, decimal=5)
    assert_almost_equal(data["frechet"], check_frechet, decimal=5)


def test_public_demo():
    sdl = SelfDrivingLabDemo(
        autoload=True,
        target_seed=15,
        observe_sensor_data_fn=mqtt_observe_sensor_data,
        observe_sensor_data_kwargs=dict(
            pico_id="test", session_id=f"pytest-{str(uuid4())}"
        ),
    )
    results = sdl.evaluate(10, 11, 12)
    fidelity_results = sdl.evaluate(
        10, 11, 12, atime=100 * 2, astep=999 * 2, gain=128 * 2
    )
    print(results)
    print(fidelity_results)


def test_blinkt_simulator():
    sim = SensorSimulatorBlinkt()
    channel_data = sim.simulate_sensor_data(0.5, 12, 24, 48)

    check_channel_data = (
        3.6003093860216055e-05,
        0.005718901898901329,
        0.005328294858512386,
        0.0040458290797878394,
        0.0,
        0.0035949178953476857,
        0.00015071481701215217,
        0.0,
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_blinkt_simulation():
    sdl = SelfDrivingLabDemoBlinkt(simulation=True)
    channel_data = sdl.observe_sensor_data(0.5, 255, 255, 255)

    check_channel_data = (
        0.0001912664361323978,
        0.030381666337913314,
        0.03527681080335163,
        0.04298693397274579,
        0.0,
        0.07639200527613832,
        0.0032026898615082336,
        0.0,
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_blinkt_target():
    sdl = SelfDrivingLabDemoBlinkt(autoload=True, simulation=True, target_seed=15)
    data = sdl.evaluate(0.25, 50, 150, 250)

    check_mae = 0.0069205842812467815

    assert_almost_equal(data["mae"], check_mae, decimal=5)
