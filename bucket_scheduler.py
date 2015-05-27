"""
buckets are (hours_available (int), {name: hours_scheduled}) list
tasks are (name, hours_remaining, last_bucket_num)
tasks can only be placed into buckets < last_bucket_num
"""

import time

class NotEnoughTime(Exception):
	pass

def get_task_set(buckets):
	s = set()
	for _hours, future_d in buckets:
		for name in future_d:
			s.add(name)

def get_non_max_set(d):
	m = max(d.values())
	non_max = {}
	for k, v in d.iteritems():
		if v != m:
			non_max.add(k)
	return non_max

def grow(buckets, name):
	pass #given a bucket, add an hour for that name and subtract for the last occurence of it

def sort_tasks(tasks):
	return sorted(tasks, key=lambda x: x[2])

#for maximizing a given day
def grow_buckets(buckets, tasks):
	start = time.time()
	tasks_sorted = sort_tasks(tasks)
	while True:
		if all(x[0] == 0 for x in buckets): #all buckets full
			break
		for i, (hours_available, d) in enumerate(buckets):
			if time.time() > start + 2:
				raise Exception("Timeout")
			if hours_available > 0:
				unfinished_tasks = get_task_set(buckets[i+1:])
				if len(unfinished_tasks) == 0:
					return buckets
				non_max_set = get_non_max_set(d)
				if len(non_max_set) == 0:
					inc_set = unfinished_tasks
				else:
					inc_set = set.intersection(unfinished_tasks, non_max_set)
				for name, _, _ in tasks_sorted:
					if name in inc_set:
						to_update = name
						break
				if to_update in d:
					d[to_update] += 1
				else:
					d[to_update] = 1
				buckets[i] = (hours_available-1, d)
				for j in range(len(buckets)-1, -1, -1):
					(hours_available_take, d_take) = buckets[j]
					if to_update in d_take:
						if d_take[to_update] == 1:
							del d_take[to_update]
						else:
							d_take[to_update] -= 1
					buckets[j] = (hours_available_take+1, d_take)
				break

	#given all unfinished tasks, add hours in order of earliest due if we won't break the max
	#given unfinished tasks and non-max tasks, take intersection and inc the earliest
	#if intersection empty, inc earliest task
	print unfinished_tasks

def bucket_scheduler(buckets, tasks):
	start = time.time()
	if any(x[2] > len(buckets) for x in tasks):
		raise Exception("Not enough buckets!")
	if any(x[2] <= 0 for x in tasks):
		raise Exception("Invalid last bucket number!")
	if sum(task[1] for task in tasks) > sum(bucket[0] for bucket in buckets):
		raise Exception("Not enough time!")
	tasks_sorted = sort_tasks(tasks)
	for name, hours_remaining, last_bucket_num in tasks_sorted:
		while hours_remaining > 0:
			if time.time() > start + 2:
				raise Exception("Timeout")
			hours_average = max(1, hours_remaining / last_bucket_num)
			if all(bucket[0] <= 0 for bucket in buckets[:last_bucket_num]):
				raise NotEnoughTime
			for i, (bucket_hours_available, d) in enumerate(buckets[:last_bucket_num]):
				hours_to_add = min(hours_average, bucket_hours_available)
				if bucket_hours_available > 0:
					buckets[i] = (bucket_hours_available-hours_to_add, d)
					hours_remaining -= hours_to_add
					if name in d:
						d[name] += hours_to_add
					else:
						d[name] = hours_to_add
				if hours_remaining == 0:
					break
	return buckets
