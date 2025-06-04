import numpy as np
from sklearn.model_selection import ParameterGrid


def grid_search(sdl, num_iter):
    param_grid = {}
    parameters = sdl.bounds
    parameters = dict(R=parameters["R"], G=parameters["G"], B=parameters["B"])
    num_pts_per_dim = int(np.floor(num_iter ** (1 / len(parameters))))
    for name, bnd in parameters.items():
        param_grid[name] = np.linspace(bnd[0], bnd[1], num=num_pts_per_dim)
        if isinstance(bnd[0], int):
            param_grid[name] = np.round(param_grid[name]).astype(int)

    grid = list(ParameterGrid(param_grid))

    grid_data = [sdl.evaluate(dict(R=pt["R"], G=pt["G"], B=pt["B"])) for pt in grid]

    return grid, grid_data


def random_search(sdl, num_iter):
    random_inputs = []
    random_data = []

    def get_random_color(sdl, rng=None):
        rng = sdl.random_rng if rng is None else rng
        # 1.0 is really bright, so no more than `max_power`
        RGB = 255 * rng.random(3) * sdl.max_power
        R, G, B = np.round(RGB).astype(int)
        return dict(R=int(R), G=int(G), B=int(B))

    for i in range(num_iter):
        random_inputs.append(get_random_color(sdl))
        random_data.append(sdl.evaluate(random_inputs[i]))
    return random_inputs, random_data


def ax_bayesian_optimization(sdl, num_iter, objective_name="frechet"):
    # Import ax only when needed to avoid top-level import issues
    from ax.service.ax_client import AxClient
    
    def evaluation_function(parameters):
        results = sdl.evaluate(
            dict(R=parameters["R"], G=parameters["G"], B=parameters["B"])
        )
        # Ax doesn't like the nested dictionary nor a flattened dict with string data
        keep_keys = {"frechet", "rmse", "mae"}
        drop_keys = list(set(results.keys()) - keep_keys)
        [results.pop(key, None) for key in drop_keys]
        return results

    bounds = dict(R=sdl.bounds["R"], G=sdl.bounds["G"], B=sdl.bounds["B"])
    parameters = [dict(name=nm, type="range", bounds=bnd) for nm, bnd in bounds.items()]

    # Initialize AxClient with the experiment configuration
    ax_client = AxClient()
    ax_client.create_experiment(
        parameters=parameters,
        objective_name=objective_name,
        minimize=True,
    )

    # Run optimization loop
    for i in range(num_iter):
        trial_parameters, trial_index = ax_client.get_next_trial()
        # Evaluate the trial
        raw_data = evaluation_function(trial_parameters)
        # Complete the trial with the results
        ax_client.complete_trial(trial_index=trial_index, raw_data=raw_data)

    # Get the best parameters
    best_parameters, values = ax_client.get_best_parameters()
    
    # Get experiment and model for compatibility
    experiment = ax_client.experiment
    model = ax_client.generation_strategy.model

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
