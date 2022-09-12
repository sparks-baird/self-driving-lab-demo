import numpy as np
from ax import optimize
from sklearn.model_selection import ParameterGrid


def grid_search(sdl, num_iter):
    param_grid = {}
    num_pts_per_dim = int(np.floor(num_iter ** (1 / len(sdl.bounds))))
    for name, bnd in sdl.bounds.items():
        param_grid[name] = np.linspace(bnd[0], bnd[1], num=num_pts_per_dim)
        if isinstance(bnd[0], int):
            param_grid[name] = np.round(param_grid[name]).astype(int)

    grid = list(ParameterGrid(param_grid))

    grid_data = [sdl.evaluate(pt["R"], pt["G"], pt["B"]) for pt in grid]

    return grid, grid_data


def random_search(sdl, num_iter):
    random_inputs = []
    random_data = []
    for i in range(num_iter):
        random_inputs.append(sdl.get_random_inputs())
        random_data.append(sdl.evaluate(*random_inputs[i]))
    return random_inputs, random_data


def ax_bayesian_optimization(sdl, num_iter, objective_name="frechet"):
    def evaluation_function(parameters):
        results = sdl.evaluate(
            R=parameters["R"],
            G=parameters["G"],
            B=parameters["B"],
        )
        # Ax doesn't like the nested dictionary nor a flattened dict with string data
        results.pop("_input_message", None)
        return results

    best_parameters, values, experiment, model = optimize(
        parameters=sdl.parameters,
        evaluation_function=evaluation_function,
        objective_name=objective_name,
        minimize=True,
        total_trials=num_iter,
    )

    return best_parameters, values, experiment, model


#     trial_df = experiment.get_trials_data_frame()

#     ax_inputs = trial_df.values.tolist()

#     bayesian_mae = [
#         [trial.objective_mean for trial in exp.trials.values()]
#         for exp in experiment
#     ]
#     return ax_inputs

# grid_mae = [[g["mae"] for g in gd] for gd in grid_data]
# random_mae = [[r["mae"] for r in rd] for rd in random_data]
# bayesian_mae = [
#     [trial.objective_mean for trial in exp.trials.values()]
#     for exp in experiment
# ]

#  = np.minimum.accumulate(np.mean(mae, axis=1), axis=1)

# std_mae = np.std(mae, axis=1)
