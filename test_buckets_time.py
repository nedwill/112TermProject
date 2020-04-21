import pickle
from timeit import timeit
from bucket_scheduler import bucket_scheduler, grow_buckets
from custom_exceptions import NotEnoughTime

with open('bucket_calls') as f:
	calls = pickle.load(f)

def test(buckets, tasks):
    fixed_buckets = [(x, {}) for x in buckets]
    fixed_tasks = []
    for i, (x, y) in enumerate(tasks):
        fixed_tasks.append((str(i), x, y))
    try:
        buckets = bucket_scheduler(fixed_buckets, fixed_tasks)
    except NotEnoughTime:
        return
    grow_buckets(buckets, fixed_tasks)

def test_all():
	for call in calls:
		test(*call)

print(timeit(stmt='test_all', setup='from __main__ import test_all', number=10000000))
