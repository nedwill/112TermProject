from task_manager import TaskManager
from tasks import Task
import datetime
from custom_exceptions import NotEnoughTime

MAX_HOURS = 10
MAXIMIZE_DAYS = False
WORK_DAYS = None #default every day
WORK_TODAY = False

mgr = TaskManager()

tasks_input = open('todo', 'r').read().splitlines()

def index_to_date(i):
	return datetime.date.today() + datetime.timedelta(i)

def week_index_to_day(i):
	if i == 0:
		return "Monday"
	elif i == 1:
		return "Tuesday"
	elif i == 2:
		return "Wednesday"
	elif i == 3:
		return "Thursday"
	elif i == 4:
		return "Friday"
	elif i == 5:
		return "Saturday"
	elif i == 6:
		return "Sunday"
	raise Exception("Invalid Day Index: {}".format(i))

#we don't handle fixed tasks yet, need a nice way to do this
for task in tasks_input:
	desc, due, hours = task.split(';') #do this with csv?
	due_dt = datetime.date(*map(int, due.split('-'))) #should handle year/day thing
	mgr.add(Task(desc, int(hours), due_dt))
try:
	agenda = mgr.calc_agenda(MAX_HOURS, max_days=MAXIMIZE_DAYS, work_days=WORK_DAYS, work_today=WORK_TODAY)
	for i, plan in enumerate(agenda):
		if len(plan) > 0:
			day = index_to_date(i)
			hours_total = sum(x[1] for x in plan)
			print "{}, {} (work {} hours total):".format(week_index_to_day(day.weekday()), day, hours_total)
			for name, hours in plan:
				print "    {}: {} hour{}".format(name, hours, 's' if hours > 1 else '')
except NotEnoughTime:
	print "Not enough time available to finish your work. :("
