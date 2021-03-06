"""
buckets are (hours_available (int), {name: hours_scheduled}) list
tasks are (name, hours_remaining, last_bucket_num)
tasks can only be placed into buckets < last_bucket_num
"""

import datetime
import time
from custom_exceptions import NotEnoughTime


def bucket_to_date(bucket_num):
    return datetime.date.today() + datetime.timedelta(days=bucket_num)


def get_task_dict(buckets, tasks):
    "the amount of hours from the last day a task is available"
    task_set = set(task.description for task in tasks)
    d = {}
    for _, future_d in buckets:
        for name, hours in future_d.items():
            if name in task_set:
                # an assignment, not a fixed task
                d[name] = hours
    return d


def get_non_max_set(d):
    if len(d) == 0:
        return d
    m = max(d.values())
    non_max = set()
    for k, v in d.items():
        if v != m:
            non_max.add(k)
    return non_max


def sort_tasks(tasks):
    "sort tasks in order of due date"
    return sorted(tasks, key=lambda task: task.bucket_num())


def get_to_update(tasks_sorted, inc_set):
    for task in tasks_sorted:
        if task.description in inc_set:
            return task.description
    return None


def get_bucket_to_update(buckets):
    for i, (hours_available, d) in enumerate(buckets):
        if hours_available > 0:
            return (i, hours_available, d)
    return None


def get_inc_set(non_max_set, unfinished_tasks):
    if len(non_max_set) == 0:
        return unfinished_tasks
    inc_set = set.intersection(unfinished_tasks, non_max_set)
    if len(inc_set) == 0:
        inc_set = unfinished_tasks
    assert len(inc_set) > 0
    return inc_set


# for maximizing a given day
def grow_buckets(buckets, tasks):
    start = time.time()
    tasks_sorted = sort_tasks(tasks)
    while True:
        if time.time() > start + 2:
            raise Exception("Timeout")

        bucket_to_update = get_bucket_to_update(buckets)
        if bucket_to_update is None:
            break
        i, hours_available, d = bucket_to_update

        # this is inefficient... n^2
        unfinished_task_dict = get_task_dict(buckets[i + 1 :], tasks)

        if len(unfinished_task_dict) == 0:
            return buckets

        unfinished_tasks = set(unfinished_task_dict)

        non_max_set = get_non_max_set(d)

        inc_set = get_inc_set(non_max_set, unfinished_tasks)

        to_update = get_to_update(tasks_sorted, inc_set)
        assert to_update is not None

        hours_to_add = min(unfinished_task_dict[to_update], hours_available)

        if to_update in d:
            d[to_update] += hours_to_add
        else:
            d[to_update] = hours_to_add

        buckets[i] = (hours_available - hours_to_add, d)
        for j in range(len(buckets) - 1, -1, -1):
            (hours_available_take, d_take) = buckets[j]
            if to_update in d_take:
                if d_take[to_update] == hours_to_add:
                    del d_take[to_update]
                else:
                    assert d_take[to_update] > hours_to_add
                    d_take[to_update] -= hours_to_add
                buckets[j] = (hours_available_take + hours_to_add, d_take)
                break

    return buckets


def bucket_scheduler(buckets, tasks):
    """
    buckets = [(8, {"fixed 3h task": 3}), (0, {}), (8, {})]
    tasks = [("test1", 4, 2), ("test2", 4, 3)]
    Those are sample inputs. This is the heart of the application,
    where tasks are scheduled.
    """
    start = time.time()
    if any(task.bucket_num() > len(buckets) for task in tasks):
        raise Exception("Not enough buckets!")
    if any(task.bucket_num() <= 0 for task in tasks):
        raise Exception("Invalid last bucket number!")
    if any(x[0] < 0 for x in buckets):
        raise Exception("Invalid (negative) bucket size!")
    if sum(task.hours for task in tasks) > sum(bucket[0] for bucket in buckets):
        raise NotEnoughTime
    tasks_sorted = sort_tasks(tasks)
    for task in tasks_sorted:
        hours_remaining = task.hours
        last_bucket_num = task.bucket_num()
        while hours_remaining > 0:
            if time.time() > start + 2:
                raise Exception("Timeout")
            hours_average = max(1, hours_remaining / last_bucket_num)
            if all(bucket[0] <= 0 for bucket in buckets[:last_bucket_num]):
                raise NotEnoughTime
            for i, (bucket_hours_available, d) in enumerate(buckets[:last_bucket_num]):
                hours_to_add = min(hours_average, bucket_hours_available)
                if bucket_hours_available > 0:
                    buckets[i] = (bucket_hours_available - hours_to_add, d)
                    hours_remaining -= hours_to_add
                    if task.description in d:
                        d[task.description] += hours_to_add
                    else:
                        d[task.description] = hours_to_add
                if hours_remaining == 0:
                    break
    return buckets
