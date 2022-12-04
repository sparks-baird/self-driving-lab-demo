import json
from queue import Queue

sensor_data_queue: "Queue[dict]" = Queue()
timeout = 30

hostname = "test.mosquitto.org"

prefix = "sdl-demo/picow/test/"
neopixel_topic = prefix + "GPIO/NaN"
sensor_topic = prefix + "as7341/"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(sensor_topic, qos=1)


def on_message(client, userdata, msg):
    sensor_data_queue.put(json.loads(msg.payload))


# TODO: implement simulator class

# TODO: set up public demo and order additional copy of demo for development


# def test_simulator():
#     sim = SensorSimulatorLiquid()
#     channel_data = list(
#         sim.simulate_sensor_data(
#             dict(
#                 R=0.01,
#                 Y=0.02,
#                 B=0.03,
#             )
#         ).values()
#     )

#     check_channel_data = list(
#         {
#             "ch410": 831.9335717568799,
#             "ch440": 23725.516359642614,
#             "ch470": 106513.2068240609,
#             "ch510": 20932.375096245254,
#             "ch550": 5801.1374228586865,
#             "ch583": 814.2217065931691,
#             "ch620": 7801.0437457016815,
#             "ch670": 128.9444509888443,
#         }.values()
#     )


#     assert_allclose(channel_data, check_channel_data)


# def test_sdl_demo_simulation():
#     sdl = SelfDrivingLabDemoLiquid(simulation=True)
#     channel_data = list(
#         sdl.observe_sensor_data(
#             dict(
#                 R=0.01,
#                 Y=0.02,
#                 B=0.03,
#             )
#         ).values()
#     )


#     check_channel_data = list(
#         {
#             "ch410": 5873.769415281079,
#             "ch440": 126604.6683886277,
#             "ch470": 567304.2531959089,
#             "ch510": 205813.93125487852,
#             "ch550": 60388.716698840944,
#             "ch583": 9302.065621007128,
#             "ch620": 164522.29171205347,
#             "ch670": 1733.6117327615912,
#         }.values()
#     )

#     assert_allclose(channel_data, check_channel_data)

#     fidelity_channel_data = list(
#         sdl.observe_sensor_data(
#             dict(R=0.01, Y=0.01, B=0.01, atime=100 * 2, astep=999 * 2, gain=128 * 2)
#         ).values()
#     )

#     check_fidelity_channel_data = np.array(check_channel_data) * 8
#     # large relative tolerance since not exactly 8 times larger
#     # this is due to the calculation of integration time
#     assert_allclose(fidelity_channel_data, check_fidelity_channel_data, rtol=0.01)


# def test_sdl_demo_target():
#     sdl = SelfDrivingLabDemoLiquid(autoload=True, simulation=True, target_seed=15)
#     data = sdl.evaluate(dict(R=0.1, Y=0.2, B=0.3))

#     check_mae = 87146.7286109353
#     check_rmse = 177834.9903063588
#     check_frechet = 485588.9246047528

#     assert_almost_equal(data["mae"], check_mae, decimal=5)
#     assert_almost_equal(data["rmse"], check_rmse, decimal=5)
#     assert_almost_equal(data["frechet"], check_frechet, decimal=5)


# def test_public_demo():
#     sdl = SelfDrivingLabDemoLiquid(
#         autoload=False,
#         target_seed=15,
#         observe_sensor_data_fn=mqtt_observe_sensor_data,
#         observe_sensor_data_kwargs=dict(
#             pico_id="test", session_id=f"pytest-{str(uuid4())}"
#         ),
#     )
#     sdl.target_results = sdl.observe_sensor_data(dict(R=0.03, Y=0.02, B=0.01))
#     results = sdl.evaluate(dict(R=0.01, Y=0.02, B=0.03))
#     fidelity_results = sdl.evaluate(
#         dict(R=0.01, Y=0.02, B=0.03, atime=100 * 2, astep=999 * 2, gain=128 * 2)
#     )
#     print(results)
#     print(fidelity_results)


# def test_bad_payload_values():
#     R = -0.01
#     Y = -0.02
#     B = -0.03
#     atime = None
#     astep = dict()
#     gain = []
#     session_id = str(uuid4())
#     experiment_id = str(uuid4())

#     client = mqtt.Client()  # create new instance
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(hostname)  # connect to broker
#     client.subscribe(sensor_topic, qos=1)

#     # ensures double quotes for JSON compatiblity
#     payload = json.dumps(
#         dict(
#             R=R,
#             Y=Y,
#             B=B,
#             atime=atime,
#             astep=astep,
#             gain=gain,
#             _session_id=session_id,
#             _experiment_id=experiment_id,
#         )
#     )
#     client.publish(neopixel_topic, payload, qos=2)

#     client.loop_start()
#     t0 = time()
#     while True:
#         if time() - t0 > timeout:
#             raise ValueError("Sensor data retrieval timed out")
#         # not sure why the following isn't enough
#         sensor_data = sensor_data_queue.get(True, timeout)
#         inp = sensor_data["_input_message"]

#         if (
#             isinstance(inp, dict)
#             and inp["_session_id"] == session_id
#             and inp["_experiment_id"] == experiment_id
#         ):
#             client.loop_stop()
#             sensor_data.pop("_input_message")
#             print(sensor_data)
#             if sensor_data["error"] is None:
#                 raise ValueError(
#                     "No error detected despite bad dictionary values (e.g. RGB)"
#                 )
#             break


# def test_bad_json_payload():
#     client = mqtt.Client()  # create new instance
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(hostname)  # connect to broker
#     client.subscribe(sensor_topic, qos=1)

#     payload = "This (bad) payload should be a JSON-formatted string via e.g. json.dumps(...)"  # noqa: E501
#     client.publish(
#         neopixel_topic,
#         payload,
#         qos=2,
#     )

#     client.loop_start()
#     t0 = time()
#     while True:
#         if time() - t0 > timeout:
#             raise ValueError("Sensor data retrieval timed out")
#         # not sure why the following isn't enough
#         sensor_data = sensor_data_queue.get(True, timeout)
#         if sensor_data["_input_message"] == payload:
#             client.loop_stop()
#             sensor_data.pop("_input_message")
#             print(sensor_data)
#             if sensor_data["error"] is None:
#                 raise ValueError("No error detected despite non-JSON payload..")
#             break
