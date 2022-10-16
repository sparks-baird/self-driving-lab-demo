"""https://github.com/facebook/Ax/issues/475, credit: soerenjalas (Sören Jalas)"""

import torch
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.service.ax_client import AxClient
from botorch.test_functions.multi_fidelity import AugmentedHartmann

problem = AugmentedHartmann(negate=True)


def objective(parameters):
    # x7 is the fidelity
    x = torch.tensor([parameters.get(f"x{i+1}") for i in range(7)])
    return {"f": (problem(x).item(), 0.0)}


gs = GenerationStrategy(
    steps=[
        GenerationStep(model=Models.SOBOL, num_trials=6),
        GenerationStep(model=Models.GPKG, num_trials=-1),
    ]
)


ax_client = AxClient(generation_strategy=gs)
ax_client.create_experiment(
    name="sdl_demo_mf_experiment",
    parameters=[
        {
            "name": "x1",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x2",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x3",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x4",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x5",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x6",
            "type": "range",
            "bounds": [0.0, 1.0],
        },
        {
            "name": "x7",
            "type": "range",
            "bounds": [0.0, 1.0],
            "is_fidelity": True,
            "target_value": 1.0,
        },
    ],
    objective_name="f",
)
# Initial sobol samples
for i in range(16):
    parameters, trial_index = ax_client.get_next_trial()
    ax_client.complete_trial(trial_index=trial_index, raw_data=objective(parameters))

# KGBO
for i in range(6):
    q_p, q_t = [], []
    # Simulate batches
    for q in range(4):
        parameters, trial_index = ax_client.get_next_trial()
        q_p.append(parameters)
        q_t.append(trial_index)
    for q in range(4):
        pi = q_p[q]
        ti = q_t[q]
        ax_client.complete_trial(trial_index=ti, raw_data=objective(pi))
