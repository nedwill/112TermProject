from hypothesis import given
from hypothesis.strategies import lists, integers, tuples
from bucket_scheduler import bucket_scheduler, grow_buckets

#should schedule everything on first day
def test_bucket_scheduler_constrained():
	buckets = [(8, {}), (0, {}), (8, {})]
	tasks = [("test1", 8, 2)]
	bucket_scheduler(buckets, tasks)

def test_bucket_scheduler_dev():
	buckets = [(8, {}), (0, {}), (8, {})]
	tasks = [("test1", 4, 2), ("test2", 4, 3)]
	buckets = bucket_scheduler(buckets, tasks)
	grow_buckets(buckets)

@given(lists(integers()), lists(tuples(integers(), integers())))
def test_bucket_scheduler(buckets, tasks):
	fixed_buckets = [(x, {}) for x in buckets]
	fixed_tasks = []
	for i, (x, y) in enumerate(tasks):
		fixed_tasks.append((str(i), x, y))
	print fixed_buckets, fixed_tasks
	bucket_scheduler(fixed_buckets, fixed_tasks)

test_bucket_scheduler_dev()
#test_bucket_scheduler()
