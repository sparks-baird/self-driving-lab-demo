import numpy as np
from ax import optimize
from sklearn.model_selection import ParameterGrid


def grid_search(sdl, num_iter):
    param_grid = {}
    parameters = sdl.bounds
    parameters = dict(R=parameters["R"], G=parameters["G"], B=parameters["B"])
    parameters
    num_pts_per_dim = int(np.floor(num_iter ** (1 / len(parameters))))
    for name, bnd in parameters.items():
        param_grid[name] = np.linspace(bnd[0], bnd[1], num=num_pts_per_dim)
        if isinstance(bnd[0], int):
            param_grid[name] = np.round(param_grid[name]).astype(int)

    grid = list(ParameterGrid(param_grid))

    grid_data = [sdl.evaluate(pt["R"], pt["G"], pt["B"]) for pt in grid]

    return grid, grid_data


def random_search(sdl, num_iter):
    random_inputs = []
    random_data = []

    def get_random_color(sdl, rng=None):
        rng = sdl.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than `max_brightness`
        RGB = 255 * rng.random(3) * sdl.max_brightness
        R, G, B = np.round(RGB).astype(int)
        return int(R), int(G), int(B)

    for i in range(num_iter):
        random_inputs.append(get_random_color(sdl))
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

    bounds = dict(R=sdl.bounds["R"], G=sdl.bounds["G"], B=sdl.bounds["B"])
    parameters = [dict(name=nm, type="range", bounds=bnd) for nm, bnd in bounds.items()]

    best_parameters, values, experiment, model = optimize(
        parameters=parameters,
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
