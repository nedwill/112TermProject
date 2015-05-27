from hypothesis import given, assume
from hypothesis.strategies import lists, integers, tuples
from bucket_scheduler import bucket_scheduler, grow_buckets, NotEnoughTime

#should schedule everything on first day
def test_bucket_scheduler_constrained():
	buckets = [(8, {}), (0, {}), (8, {})]
	tasks = [("test1", 8, 2)]
	bucket_scheduler(buckets, tasks)

def test_bucket_scheduler_dev():
	buckets = [(8, {}), (0, {}), (8, {})]
	tasks = [("test1", 4, 2), ("test2", 4, 3)]
	buckets = bucket_scheduler(buckets, tasks)
	grow_buckets(buckets, tasks)

@given(lists(integers()), lists(tuples(integers(), integers())))
def test_bucket_scheduler(buckets, tasks):
	"TODO: improve checking for time availability"
	assume(all(task[1] <= len(buckets) for task in tasks))
	assume(all(task[1] > 0 for task in tasks))
	assume(sum(task[0] for task in tasks) <= sum(bucket for bucket in buckets))
	print buckets,tasks
	fixed_buckets = [(x, {}) for x in buckets]
	fixed_tasks = []
	for i, (x, y) in enumerate(tasks):
		fixed_tasks.append((str(i), x, y))
	#print fixed_buckets, fixed_tasks
	try:
		bucket_scheduler(fixed_buckets, fixed_tasks)
	except NotEnoughTime:
		pass

test_bucket_scheduler_dev()
#test_bucket_scheduler()
