# https://github.com/ray-project/ray/issues/5554#issuecomment-558397627
import ray
from tqdm import tqdm


def test():
    import time

    time.sleep(0.05)
    return 1


test_r = ray.remote(test)

ray.init(ignore_reinit_error=True, num_cpus=2)


def to_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        yield ray.get(done[0])


obj_ids = [test_r.remote() for i in range(100)]

results = [result for result in tqdm(to_iterator(obj_ids))]
print(results)
