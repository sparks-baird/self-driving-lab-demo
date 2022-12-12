from typing import Any, Dict, Optional

import torch

# from ax.core.objective import ScalarizedObjective
from ax.modelbridge import get_sobol
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.models.torch.botorch_modular.surrogate import Surrogate
from ax.service.ax_client import AxClient
from botorch.acquisition.active_learning import (
    MCSampler,
    qNegIntegratedPosteriorVariance,
)
from botorch.acquisition.input_constructors import (
    MaybeDict,
    acqf_input_constructor,
    construct_inputs_mc_base,
)
from botorch.acquisition.objective import AcquisitionObjective
from botorch.models.gp_regression import SingleTaskGP
from botorch.models.model import Model
from botorch.utils.datasets import SupervisedDataset
from torch import Tensor


@acqf_input_constructor(qNegIntegratedPosteriorVariance)
def construct_inputs_qNIPV(
    model: Model,
    mc_points: Tensor,
    training_data: MaybeDict[SupervisedDataset],
    objective: Optional[AcquisitionObjective] = None,
    X_pending: Optional[Tensor] = None,
    sampler: Optional[MCSampler] = None,
    **kwargs: Any,
) -> Dict[str, Any]:

    if model.num_outputs == 1:
        objective = None

    base_inputs = construct_inputs_mc_base(
        model=model,
        training_data=training_data,
        sampler=sampler,
        X_pending=X_pending,
        objective=objective,
    )

    return {**base_inputs, "mc_points": mc_points}


def objective_function(x):
    f = x["x1"] ** 2 + x["x2"] ** 2 + x["x3"] ** 2
    return {"f": (f, None)}


parameters = [
    {"name": "x1", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
    {"name": "x2", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
    {"name": "x3", "type": "range", "bounds": [0.0, 1.0], "value_type": "float"},
]
ax_client_tmp = AxClient()
ax_client_tmp.create_experiment(parameters=parameters)
sobol = get_sobol(ax_client_tmp.experiment.search_space)
mc_points = sobol.gen(1024).param_df.values
mcp = torch.tensor(mc_points)

model_kwargs_val = {
    "surrogate": Surrogate(SingleTaskGP),
    "botorch_acqf_class": qNegIntegratedPosteriorVariance,
    "acquisition_options": {"mc_points": mcp},
}

gs = GenerationStrategy(
    steps=[
        GenerationStep(model=Models.SOBOL, num_trials=5),
        GenerationStep(
            model=Models.BOTORCH_MODULAR, num_trials=15, model_kwargs=model_kwargs_val
        ),
    ]
)

ax_client = AxClient(generation_strategy=gs)
ax_client.create_experiment(
    name="active_learning_experiment",
    parameters=parameters,
    objective_name="f",
    minimize=True,
)

for _ in range(20):
    trial_params, trial_index = ax_client.get_next_trial()
    data = objective_function(trial_params)
    ax_client.complete_trial(trial_index=trial_index, raw_data=data["f"])
