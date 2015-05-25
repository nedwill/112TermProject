"""
buckets are (hours_available (int), {name: hours_scheduled}) list
tasks are (name, hours_remaining, last_bucket_num)
tasks can only be placed into buckets < last_bucket_num
"""

def bucket_scheduler(buckets, tasks):
	tasks_sorted = sorted(key=lambda x: x[2])
	for name, hours_remaining, last_bucket_num in tasks_sorted:
		while hours_remaining > 0:
			if all(bucket_hours == 0 for bucket_hours in buckets[:last_bucket_num]):
				raise Exception("Schedule failure!")
			for i, (bucket_hours_available, d) in enumerate(buckets[:last_bucket_num]):
				if bucket_hours_available > 0:
					buckets[i] -= 1
					hours_remaining -= 1
					if name in d:
						d[name] += 1
					else:
						d[name] = 1
				if hours_remaining == 0:
					break
	return buckets
