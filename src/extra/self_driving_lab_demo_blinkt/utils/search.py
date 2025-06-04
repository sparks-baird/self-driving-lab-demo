import numpy as np
from sklearn.model_selection import ParameterGrid


def grid_search(sdl, num_iter):
    param_grid = {}
    num_pts_per_dim = round(num_iter ** (1 / len(sdl.bounds)))
    for name, bnd in sdl.bounds.items():
        param_grid[name] = np.linspace(bnd[0], bnd[1], num=num_pts_per_dim)
        if isinstance(bnd[0], int):
            param_grid[name] = np.round(param_grid[name]).astype(int)

    grid = list(ParameterGrid(param_grid))

    grid_data = [
        sdl.evaluate(pt["brightness"], pt["R"], pt["G"], pt["B"]) for pt in grid
    ]

    return grid, grid_data


def random_search(sdl, num_iter):
    random_inputs = []
    random_data = []
    for i in range(num_iter):
        random_inputs.append(sdl.get_random_inputs())
        random_data.append(sdl.evaluate(*random_inputs[i]))
    return random_inputs, random_data


def ax_bayesian_optimization(sdl, num_iter):
    # Import ax only when needed to avoid top-level import issues
    from ax.service.ax_client import AxClient
    
    def evaluation_function(parameters):
        return sdl.evaluate(
            brightness=parameters["brightness"],
            R=parameters["R"],
            G=parameters["G"],
            B=parameters["B"],
        )

    # Initialize AxClient with the experiment configuration
    ax_client = AxClient()
    ax_client.create_experiment(
        parameters=sdl.parameters,
        objective_name="mae",
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
