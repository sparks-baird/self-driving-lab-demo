"""Source: https://ax.dev/docs/api.html"""
from ax.service.ax_client import AxClient
from ax.utils.measurement.synthetic_functions import branin

ax_client = AxClient()
ax_client.create_experiment(
    name="branin_test_experiment",
    parameters=[
        {
            "name": "x1",
            "type": "range",
            "bounds": [-5.0, 10.0],
            "value_type": "float",
        },
        {
            "name": "x2",
            "type": "range",
            "bounds": [0.0, 10.0],
        },
    ],
    objective_name="branin",
    minimize=True,
)

for _ in range(15):
    parameters, trial_index = ax_client.get_next_trial()
    ax_client.complete_trial(
        trial_index=trial_index, raw_data=branin(parameters["x1"], parameters["x2"])
    )

best_parameters, metrics = ax_client.get_best_parameters()

print(best_parameters)
