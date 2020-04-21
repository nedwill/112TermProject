from hypothesis import given, assume
from hypothesis.strategies import lists, integers, tuples
from bucket_scheduler import bucket_scheduler, grow_buckets
from custom_exceptions import NotEnoughTime

# should schedule everything on first day
def test_bucket_scheduler_constrained():
    buckets = [(8, {}), (0, {}), (8, {})]
    tasks = [("test1", 8, 2)]
    bucket_scheduler(buckets, tasks)


def test_bucket_scheduler_dev():
    buckets = [(8, {}), (0, {}), (8, {})]
    tasks = [("test1", 4, 2), ("test2", 4, 3)]
    buckets = bucket_scheduler(buckets, tasks)
    print(grow_buckets(buckets, tasks))


# (buckets, [(hours, due date), ...])
@given(lists(integers()), lists(tuples(integers(), integers())))
def test_bucket_scheduler(buckets, tasks_):
    if not buckets:
        return

    "TODO: improve checking for time availability"
    tasks = []

    for task in tasks:
        # assume(all(task[1] <= len(buckets) for task in tasks))
        task[1] %= len(buckets)
        # assume(all(task[1] > 0 for task in tasks))
        if task[1] <= 0:
            task[1] = 1

    # for faster testing
    assume(all(bucket >= 0 for bucket in buckets))
    total_buckets = sum(bucket for bucket in buckets)
    assume(sum(task[0] for task in tasks) <= total_buckets)

    fixed_buckets = [(x, {}) for x in buckets]
    fixed_tasks = []
    for i, (x, y) in enumerate(tasks):
        fixed_tasks.append((str(i), x, y))
    try:
        buckets = bucket_scheduler(fixed_buckets, fixed_tasks)
    except NotEnoughTime:
        return
    buckets = grow_buckets(buckets, fixed_tasks)
    grown_buckets = {}
    for _hours, d in buckets:
        for task_name, hours in d.items():
            if task_name in grown_buckets:
                grown_buckets[task_name] += hours
            else:
                grown_buckets[task_name] = hours
    task_buckets = {}
    for name, hours_remaining, _last_bucket_num in fixed_tasks:
        if hours_remaining > 0:
            task_buckets[name] = hours_remaining
    assert grown_buckets == task_buckets


test_bucket_scheduler_dev()
test_bucket_scheduler()
