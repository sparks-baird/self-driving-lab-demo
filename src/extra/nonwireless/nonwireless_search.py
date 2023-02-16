# %% [markdown]
# # Nonwireless Pico Usage and Search
#
# You might run into issues sourcing a Pico W or you might have issues
# connecting/authenticating with a particular wireless network. Not to fret: you can still
# use a regular Pico (or the Pico W) in a USB-to-USB interface.
#
# The corresponding [`src/nonwireless/main.py`](../src/nonwireless/main.py) script needs
# to be running on the Pico. Unplug and replug the USB to ensure the currently uploaded
# main.py program starts running. The NeoPixel LED on the Maker Pi Pico should blink twice
# as a sign that the program is running.

# %% [markdown]
# First, let's open a serial connection with the Pico.

# %%
import sys

import serial

# If on Windows, might not be COM5, check device manager --> Ports
# https://www.tomshardware.com/how-to/detect-com-port-windows-serial-port-notifier
com = "COM5" if "win" in sys.platform else "/dev/ttyACM0"

s = serial.Serial(com, 115200)

# %% [markdown]
# We can send two commands (encoded as strings) to the Pico: `set_color(R, G, B)` and
# `read_sensor(astep, atime)`. Here, we'll define some helper functions so we don't have
# to deal with the strings directly.

# %%
from ast import literal_eval
from time import sleep

from self_driving_lab_demo.core import CHANNEL_NAMES


def set_color(red, green, blue):
    s.write(f"set_color({red}, {green}, {blue})\n".encode("utf-8"))


def read_sensor(astep=100, atime=999):
    s.write(f"read_sensor({astep}, {atime})\n".encode("utf-8"))
    sensor_data_str = s.readline().strip().decode("utf-8")
    s.readline()  # get rid of the extra line
    if sensor_data_str == "":
        raise ValueError("No data returned")
    return literal_eval(sensor_data_str)


def observe_sensor_data(red, green, blue, astep=100, atime=999):
    set_color(red, green, blue)
    sensor_data = read_sensor(astep=astep, atime=atime)
    return {channel: datum for channel, datum in zip(CHANNEL_NAMES, sensor_data)}


# %%
set_color(10, 10, 10)
sleep(1)
sensor_data = read_sensor()
print(sensor_data)
set_color(0, 0, 0)

# %%
data = observe_sensor_data(10, 10, 10)
set_color(0, 0, 0)
print(data)

# %%
from self_driving_lab_demo import SelfDrivingLabDemo

sdl = SelfDrivingLabDemo(
    observe_sensor_data_fn=observe_sensor_data,
    observe_sensor_data_kwargs=dict(astep=100, atime=999),
    autoload=True,
)
sdl.clear()

# %%
sdl.evaluate(10, 20, 30)
sdl.clear()

# %% [markdown]
# ## Optimization
#
# > Note: the rest will proceed as was done in previous notebooks.
#
# While there are great numerical tutorials comparing [grid search vs. random search vs.
# Bayesian optimization](https://towardsdatascience.com/grid-search-vs-random-search-vs-bayesian-optimization-2e68f57c3c46), here, we'll compare these three search methods in a way that perhaps you've never seen before,
# namely a self-driving laboratory demo!
#
# ### Setup
#
# We define our optimization task parameters and take care of imports.

# %% [markdown]
# ### Optimization Task Parameters
#
# We'll use 125 iterations repeated 5 times. The use of 125 iterations instead of something
# "cleaner" like 50 or 100 is due to constraints of doing uniform (full-factorial) grid
# search. $n^d$ number of points are required for uniform grid search, where $n$ and $d$
# represent number of points per dimension (`n_pts_per_dim`) and number of dimensions
# (`3`), respectively.

# %%
num_iter = 5**3
num_repeats = 5
SEEDS = range(10, 10 + num_repeats)

# %% [markdown]
# We also instantiate multiple `SelfDrivingLabDemo` instances, each with their own
# unique target spectrum, and then turn off the LED.

# %%
sdls = [
    SelfDrivingLabDemo(
        observe_sensor_data_fn=observe_sensor_data,
        observe_sensor_data_kwargs=dict(astep=100, atime=999),
        autoload=True,
        target_seed=seed,
    )
    for seed in SEEDS
]
sdls[0].clear()


# %% [markdown]
# Notice that the target_data is different for each.

# %%
import pandas as pd

df = pd.DataFrame([sdl.target_results for sdl in sdls])
df.loc[:, sdl.channel_names]  # sort columns by wavelength

# %% [markdown]
#
#
# ### Imports
#
# We'll be using `scikit-learn`'s `ParameterGrid` for grid search, `self_driving_lab_demo`'s built-in
# `get_random_inputs` for random search, and `ax-platform`'s Gaussian Process Expected
# Improvement (GPEI) model for Bayesian
# optimization. To help with defining the grid search space, we will also use the
# `bounds` and `parameters` class property of `SelfDrivingLabDemo` for convenience. Note
# that 89 is the upper limit for RGB values instead of 255 since 255 is very bright.

# %%
import numpy as np
from ax import optimize
from sklearn.model_selection import ParameterGrid
from tqdm.notebook import tqdm

# %%
sdls[0].bounds

# %%
sdls[0].parameters

# %% [markdown]
# ### Grid Search
#
# First, we need to define our parameter grid. We'll divide up the 3-dimensional parameter
# space as evenly as possible (see `num_pts_per_dim` below).

# %%
param_grid = {}
num_pts_per_dim = round(num_iter ** (1 / len(sdl.bounds)))
for name, bnd in sdl.bounds.items():
    param_grid[name] = np.linspace(bnd[0], bnd[1], num=num_pts_per_dim)
    if isinstance(bnd[0], int):
        param_grid[name] = np.round(param_grid[name]).astype(int)
print(f"num_pts_per_dim: {num_pts_per_dim}")

# %% [markdown]
# Notice how many distinct values are along each dimension.

# %%
param_grid

# %% [markdown]
# After assembling the full grid, notice that the total number of points is $5^3 = 125$.

# %%
grid = list(ParameterGrid(param_grid))
print("grid:\n", grid[0:4], "...", grid[-1:])
print("\nNumber of grid points: ", len(grid))

# %% [markdown]
# Now, we can start the actual search. The grid search locations are fixed
# for each of the repeat optimization campaigns; however the observed sensor data will be
# stochastic and the target spectrum is different for each repeat run. An alternative approach to setting a
# fixed budget and varying the target solution would be to see how many iterations it takes to meet a criteria for the
# objective function similar to [this post](https://towardsdatascience.com/grid-search-vs-random-search-vs-bayesian-optimization-2e68f57c3c46); however, a fixed budget seems more characteristic of a real chemistry
# or materials optimization campaign due to limits on funding, time, and other resources:
# (i.e. we'll search until we find what we're looking for, until we run out of
# resources, or until we decide it's no longer worth the expense, whichever comes first).

# %%
grid_data = [
    [sdl.evaluate(pt["R"], pt["G"], pt["B"]) for pt in grid] for sdl in tqdm(sdls)
]
sdls[0].clear()

# %% [markdown]
# ### Random Search

# %% [markdown]
# Now, let's perform random search as we did before in
# [`2.0-random-search.ipynb`](2.0-random-search.ipynb), storing the inputs and outputs as we go.

# %%
random_inputs = []
random_data = []
for _ in tqdm(range(num_repeats)):
    random_input = []
    random_datum = []
    for i in range(num_iter):
        random_input.append(sdl.get_random_inputs())
        random_datum.append(sdl.evaluate(*random_input[i]))
    random_inputs.append(random_input)
    random_data.append(random_datum)
sdls[0].clear()

# %% [markdown]
# ### Bayesian Optimization
#
# Now, we'll use an optimization algorithm that learns from prior information. Once a
# small set of initialization points have been evaluated, the algorithm will leverage the
# previously observed information to intelligently select the next point to evaluate. The
# selected point will be a trade-off between exploiting the highest performance and
# exploring uncertain regions (i.e. exploitation/exploration trade-off). We'll also use
# a discretized Frechet distance in place of mean absolute error as a more robust
# comparison between discrete distributions.

# %%
bo_results = []
objective_name = "frechet"

for sdl in tqdm(sdls):

    def evaluation_function(parameters):
        data = sdl.evaluate(
            parameters["R"],
            parameters["G"],
            parameters["B"],
        )
        return data[objective_name]

    bo_results.append(
        optimize(
            parameters=sdl.parameters,
            evaluation_function=evaluation_function,
            minimize=True,
            total_trials=num_iter,
        )
    )

best_parameters, values, experiment, model = zip(*bo_results)
sdls[0].clear()

# %% [markdown]
# ### Analysis
#
# Now that we've run our three optimizations, let's compare the performance in tabular
# form and visually.

# %% [markdown]
# ### Preparing the data

# %%
grid_obj = [[g[objective_name] for g in gd] for gd in grid_data]
random_obj = [[r[objective_name] for r in rd] for rd in random_data]
bayesian_obj = [exp.fetch_data().df["mean"].tolist() for exp in experiment]

# %%
obj = np.array([grid_obj, random_obj, bayesian_obj])
obj.shape

# %% [markdown]
# ### Tabular

# %%
avg_obj = np.mean(np.minimum.accumulate(obj, axis=2), axis=1)
std_obj = np.std(avg_obj, axis=1)
avg_obj.shape

# %%
np.mean(random_obj)

# %%
best_avg_obj = np.min(avg_obj, axis=1)
best_avg_obj

# %% [markdown]
# ### Best Objective vs. Iteration

# %%
names = ["grid", "random", "bayesian"]
df = pd.DataFrame(
    {
        **{f"{n}_{objective_name}": m for n, m in zip(names, avg_obj)},
        **{f"{n}_std": s for n, s in zip(names, std_obj)},
    }
)


# %%
obj_df = pd.melt(
    df.reset_index(),
    id_vars=["index"],
    value_vars=[
        f"grid_{objective_name}",
        f"random_{objective_name}",
        f"bayesian_{objective_name}",
    ],
    var_name="method",
    value_name=objective_name,
)

std_df = pd.melt(
    df.reset_index(),
    id_vars=["index"],
    value_vars=["grid_std", "random_std", "bayesian_std"],
    var_name="method",
    value_name="std",
)

obj_df.loc[:, "method"] = obj_df.loc[:, "method"].apply(
    lambda x: x.replace(f"_{objective_name}", "")
)
std_df.loc[:, "method"] = std_df.loc[:, "method"].apply(lambda x: x.replace("_std", ""))

# %%
results_df = obj_df.merge(std_df, on=["method", "index"]).rename(
    columns=dict(index="iteration")
)
results_df

# %% [markdown]
# ### Visualization
# As we might expect, Bayesian optimization outperforms random search while grid and
# random search are on par with each other.

# %%
# import plotly.express as px
from self_driving_lab_demo.utils.plotting import line

fig = line(
    data_frame=results_df,
    x="iteration",
    y=objective_name,
    error_y="std",
    error_y_mode="band",
    color="method",
)
max_y = (results_df[objective_name] + results_df["std"]).max()
fig.update_yaxes(range=[0.0, max_y * 1.02])
fig

# %% [markdown]
# #### Example Output
#
# ![pico-grid-random-bayesian-simulator](pico-grid-random-bayesian-simulator.png)
