import itertools
from uuid import uuid4

import ray

# from public_mqtt_sdl_demo.secrets import PICO_ID
from self_driving_lab_demo.utils.observe import mqtt_observe_sensor_data

PICO_ID = "test"

session_ids = [str(uuid4()) for _ in range(4)]

ray.init(num_cpus=6)


@ray.remote
def parallel_observe_sensor_data(R, G, B, session_id):
    return mqtt_observe_sensor_data(R, G, B, pico_id=PICO_ID, session_id=session_id)


params1 = [(x, x, x, session_ids[0]) for x in range(10, 101, 5)]
params2 = [(x, x, x, session_ids[1]) for x in range(10, 101, 5)]
params3 = [(x, x, x, session_ids[2]) for x in range(10, 101, 5)]
params4 = [(x, x, x, session_ids[3]) for x in range(10, 101, 5)]
params2.reverse()
params4.reverse()

# https://stackoverflow.com/questions/7946798/interleave-multiple-lists-of-the-same-length-in-python
params = list(itertools.chain(*zip(params1, params2, params3, params4)))

data = ray.get([parallel_observe_sensor_data.remote(*p) for p in params])
ray.shutdown()

1 + 1

# %% Code Graveyard

# @ray.remote
# def square(x):
#     return x * x

# ray.get([square.remote(x) for x in range(1000)])
