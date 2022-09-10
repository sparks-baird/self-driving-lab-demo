from numpy.testing import assert_allclose, assert_almost_equal

from self_driving_lab_demo.core import SelfDrivingLabDemo, SensorSimulator
from self_driving_lab_demo_blinkt.core import (
    SelfDrivingLabDemo as SelfDrivingLabDemoBlinkt,
)
from self_driving_lab_demo_blinkt.core import SensorSimulator as SensorSimulatorBlinkt


def test_simulator():
    sim = SensorSimulator()
    channel_data = list(sim.simulate_sensor_data(12, 24, 48).values())

    check_channel_data = list(
        {
            "ch410": 0.023147948676368064,
            "ch440": 0.6601452972423533,
            "ch470": 2.963652782651812,
            "ch510": 0.5824281659641573,
            "ch550": 0.16141244431969332,
            "ch583": 0.02265512886515825,
            "ch620": 0.2170583882872512,
            "ch670": 0.0035877858941176233,
        }.values()
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_simulation():
    sdl = SelfDrivingLabDemo(simulation=True)
    channel_data = list(sdl.observe_sensor_data(255, 255, 255).values())

    check_channel_data = list(
        {
            "ch410": 0.1634333768675954,
            "ch440": 3.52268313906316,
            "ch470": 15.78482968193261,
            "ch510": 5.726623470078847,
            "ch550": 1.6802722744130456,
            "ch583": 0.25882323407692215,
            "ch620": 4.577713526605947,
            "ch670": 0.04823648999999976,
        }.values()
    )

    assert_allclose(channel_data, check_channel_data)


def test_sdl_demo_target():
    sdl = SelfDrivingLabDemo(autoload=True, simulation=True, target_seed=15)
    data = sdl.evaluate(50, 150, 250)

    check_mae = 2.424794562550509
    check_rmse = 4.948129716391581
    check_frechet = 13.511159888434474

    assert_almost_equal(data["mae"], check_mae, decimal=5)
    assert_almost_equal(data["rmse"], check_rmse, decimal=5)
    assert_almost_equal(data["frechet"], check_frechet, decimal=5)


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
