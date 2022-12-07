import ray
from ax.service.ax_client import AxClient
from ax.utils.measurement.synthetic_functions import branin

batch_size = 2
num_trials = 11

ax_client = AxClient()
ax_client.create_experiment(
    parameters=[
        {"name": "x1", "type": "range", "bounds": [-5.0, 10.0]},
        {"name": "x2", "type": "range", "bounds": [0.0, 15.0]},
    ],
    objective_name="branin",
    minimize=True,
    # Sets max parallelism to 10 for all steps of the generation strategy.
    choose_generation_strategy_kwargs={
        "num_trials": num_trials,
        "max_parallelism_override": batch_size,
        "enforce_sequential_optimization": False,
    },
)


@ray.remote
def evaluate(parameters):
    return {"branin": branin(parameters["x1"], parameters["x2"])}


n = 0
while n < num_trials:
    curr_batch_size = batch_size if n + batch_size < num_trials else num_trials - n

    trial_mapping, optimization_complete = ax_client.get_next_trials(curr_batch_size)
    n = n + curr_batch_size

    # start running trials in a queue (new trials will start as resources are freed)
    futures = [evaluate.remote(parameters) for parameters in trial_mapping.values()]

    # wait for all trials in the batch to complete before continuing (i.e. blocking)
    results = ray.get(futures)

    # report the completion of trials to the Ax client
    for trial_index, raw_data in zip(trial_mapping.keys(), results):
        ax_client.complete_trial(trial_index=trial_index, raw_data=raw_data)
