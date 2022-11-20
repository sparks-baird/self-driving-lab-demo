# pip install olymp sqlalchemy matplotlib
# initalize the Olympus orchestrator
from time import time

from olympus import Campaign, Database, Olympus

olymp = Olympus()
# we declare a local database to which we store our campaign results
database = Database()

DATASET = "photo_pce10"
# DATASET = path.join(
#     "\sterg",
#     "Miniconda3",
#     "envs",
#     "sdl-demo",
#     "lib",
#     "site-packages",
#     "olympus",
#     "datasets",
#     "dataset_photo_pce10",
# )  # "hplc"

# MODEL =
# "Rs\sterg\Miniconda3\envs\sdl-demo\lib\site-packages\olympus\models\modelBayesNeuralNet"

NUM_REPETITIONS = 10
PLANNERS = ["Grid"]

elapsed_times = {"planner": [], "time": []}
for PLANNER in PLANNERS:
    for repetition in range(NUM_REPETITIONS):
        print(f"Algorithm: {PLANNER} [repetition {repetition+1}]")

        start_time = time()
        olymp.run(
            planner=PLANNER,  # run simulation with <PLANNER>,
            dataset=DATASET,  # on emulator trained on dataset <DATASET>;
            # model=MODEL,
            campaign=Campaign(),  # store results in a new campaign,
            database=database,  # but use the same database to store campaign;
            num_iter=100,  # run benchmark for num_iter iterations
        )
        elapsed_time = time() - start_time
        elapsed_times["planner"].append(PLANNER)
        elapsed_times["time"].append(elapsed_time)
