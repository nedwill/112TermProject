from task_manager import TaskManager
from tasks import Task, FixedTask
import datetime
import sys
from custom_exceptions import NotEnoughTime, TaskAlreadyExists
from tabulate import tabulate

try:
	MAX_HOURS = int(sys.argv[1])
except IndexError:
	print "[*] No max hours provided: assuming 8."
	MAX_HOURS = 8
except ValueError:
	print "[-] Invalid max hours provided: assuming 8."
	MAX_HOURS = 8
MAXIMIZE_DAYS = False
WORK_DAYS = None #[0,1,2,3,4] #None #default every day
WORK_TODAY = True
USER_SPEC_DAYS = {}

try:
	with open('user_specified_days', 'r') as f:
		user_specified_days_raw = f.read()
	for line in user_specified_days_raw.splitlines():
		date, hours = line.split(";")
		date_dt = datetime.date(*map(int, date.split('-')))
		offset = (date_dt - datetime.date.today()).days
		if offset >= 0:
			USER_SPEC_DAYS[offset] = int(hours)
except IOError:
	print "[*] User specified days not provided."

mgr = TaskManager()

with open('todo', 'r') as f:
	tasks_input = f.read().splitlines()

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

def make_recurring(recurring):
	rec = []
	d = {
		"monday": 0,
		"tuesday": 1,
		"wednesday": 2,
		"thursday": 3,
		"friday": 4,
		"saturday": 5,
		"sunday": 6
	}
	recurring = recurring.lower()
	for day_name, day_num in d.iteritems():
		if day_name in recurring:
			rec.append(day_num)
	return rec

#we don't handle fixed tasks yet, need a nice way to do this
for task in tasks_input:
	task = task.strip()
	if task[0] == "#": #comments!
		continue
	if "recurring " == task[:len("recurring ")]:
		desc, recurring, due, hours = task.split(';')
		due_dt = datetime.date(*map(int, due.split('-'))) #should handle year/day thing
		recurring = make_recurring(recurring)
		print desc, int(hours), due_dt, recurring
		new_task = FixedTask(desc, int(hours), due_dt, recurring)
	else:
		desc, due, hours = task.split(';') #do this with csv?
		due_dt = datetime.date(*map(int, due.split('-')))
		if "fixed " == desc[:len("fixed ")]:
			new_task = FixedTask(desc, int(hours), due_dt) #fake the starttime and endtime
		else:
			if due_dt <= datetime.date.today():
				print "[!] Task `{}` due on or before today.".format(desc)
				continue
			new_task = Task(desc, int(hours), due_dt)
	try:
		mgr.add(new_task)
	except TaskAlreadyExists:
		print "found duplicate task {}".format(desc)
		exit()

print "[+] {} tasks processed. Attempting to generate schedule.".format(mgr.num_tasks())

prompted = False
while MAX_HOURS < 24:
	try: #we often expect this to fail so using an exception is a little worse than returning None
		agenda = mgr.calc_agenda(MAX_HOURS, max_days=MAXIMIZE_DAYS,\
			work_days=WORK_DAYS, work_today=WORK_TODAY, user_specified_days=USER_SPEC_DAYS)
		break
	except NotEnoughTime:
		#it's a little spamming to print this every time. do it better later
		if not prompted:	
			print "[!] Not enough time available to finish your work in {} hours, increasing as necessary.".format(MAX_HOURS)
			prompted = True
		MAX_HOURS += 1

if MAX_HOURS >= 24:
	print "[-] Not enough time available in 24 hours a day to finish your work. :("
	exit()

print "[+] Schedule successfully generated with max {} hours per day.".format(MAX_HOURS)
for i, plan in enumerate(agenda):
	if len(plan) > 0:
		day = index_to_date(i)
		hours_total = sum(x[1] for x in plan)
		print ""
		print "{}, {} (work {} hours total):".format(week_index_to_day(day.weekday()), day, hours_total)
		final = [[task.description, "{}/{}".format(hours, task.hours), task.due.strftime("%m-%d")] for (task, hours) in plan]
		print tabulate(final, headers=["Task", "Hours", "Due"])
