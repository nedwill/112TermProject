"""
buckets are (hours_available (int), {name: hours_scheduled}) list
tasks are (name, hours_remaining, last_bucket_num)
tasks can only be placed into buckets < last_bucket_num
"""

#for maximizing a given day
def grow_buckets(buckets):
	print buckets
	for i, (hours_available, d) in enumerate(buckets):
		while hours_available > 0:
			unfinished_tasks = set()
			for _hours, future_d in buckets[i+1:]:
				for name in future_d:
					unfinished_tasks.add(name)
			if len(unfinished_tasks) == 0:
				break #should return?
	#given all unfinished tasks, add hours in order of earliest due if we won't break the max
	#given unfinished tasks and non-max tasks, take intersection and inc the earliest
	#if intersection empty, inc earliest task
	print unfinished_tasks

def bucket_scheduler(buckets, tasks):
	tasks_sorted = sorted(tasks, key=lambda x: x[2])
	for name, hours_remaining, last_bucket_num in tasks_sorted:
		while hours_remaining > 0:
			if all(bucket_hours == 0 for bucket_hours in buckets[:last_bucket_num]):
				raise Exception("Schedule failure!")
			for i, (bucket_hours_available, d) in enumerate(buckets[:last_bucket_num]):
				if bucket_hours_available > 0:
					buckets[i] = (bucket_hours_available-1, d)
					hours_remaining -= 1
					if name in d:
						d[name] += 1
					else:
						d[name] = 1
				if hours_remaining == 0:
					break
	return buckets
