import ray
from ray_get_reproducer_utils import get_data, put_data

# Start Ray. This creates some processes that can do work in parallel.
ray.init(num_cpus=2)


# Add this line to signify that the function can be run in parallel (as a
# "task"). Ray will load-balance different `square` tasks automatically.
@ray.remote
def square(x):
    put_data()
    get_data()
    return x * x


# Create some parallel work using a list comprehension, then block until the
# results are ready with `ray.get`.
results = ray.get([square.remote(x) for x in range(100)])

ray.shutdown()

1 + 1
