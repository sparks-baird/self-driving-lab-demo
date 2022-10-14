from uuid import uuid4  # universally unique identifier

from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties

from self_driving_lab_demo import SelfDrivingLabDemo, mqtt_observe_sensor_data

pico_id = "test"  # @param {type:"string"}
num_repeats = 1  # @param {type:"integer"}
seeds = range(10, 10 + num_repeats)
num_iter = 5
SESSION_ID = str(uuid4())  # random session ID
print(f"session ID: {SESSION_ID}")

sdls = [
    SelfDrivingLabDemo(
        autoload=True,  # perform target data experiment automatically
        observe_sensor_data_fn=mqtt_observe_sensor_data,  # (default)
        observe_sensor_data_kwargs=dict(pico_id=pico_id, session_id=SESSION_ID),
        target_seed=seed,
    )
    for seed in seeds
]

channels = sdls[0].channel_names
bounds = dict(R=sdls[0].bounds["R"], G=sdls[0].bounds["G"], B=sdls[0].bounds["B"])
parameters = [dict(name=nm, type="range", bounds=bnd) for nm, bnd in bounds.items()]

objectives = {
    ch: ObjectiveProperties(minimize=True, threshold=1000.0) for ch in channels
}

ax_client = AxClient()
ax_client.create_experiment(
    name="sdl-demo-moo",
    parameters=parameters,
    objectives=objectives,
    overwrite_existing_experiment=True,
)
