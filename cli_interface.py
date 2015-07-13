from task_manager import TaskManager
from tasks import Task, FixedTask
import datetime
import sys
from custom_exceptions import NotEnoughTime, TaskAlreadyExists

try:
	MAX_HOURS = int(sys.argv[1])
except IndexError:
	print "[*] No max hours provided: assuming 8."
	MAX_HOURS = 8
except ValueError:
	print "[-] Invalid max hours provided: assuming 8."
	MAX_HOURS = 8
MAXIMIZE_DAYS = False
WORK_DAYS = None #default every day
WORK_TODAY = True

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
	if task[0] == "#": #comments!
		continue
	desc, due, hours = task.split(';') #do this with csv?
	due_dt = datetime.date(*map(int, due.split('-'))) #should handle year/day thing
	if "fixed " == desc[:len("fixed ")]:
		new_task = FixedTask(desc, int(hours), due_dt) #fake the starttime and endtime
	else:
		new_task = Task(desc, int(hours), due_dt)
	try:
		mgr.add(new_task)
	except TaskAlreadyExists:
		print "found duplicate task {}".format(desc)
		exit()

print "[+] {} tasks processed. Attempting to generate schedule.".format(len(tasks_input))

while MAX_HOURS < 24:
	try: #we often expect this to fail so using an exception is a little worse than returning None
		agenda = mgr.calc_agenda(MAX_HOURS, max_days=MAXIMIZE_DAYS, work_days=WORK_DAYS, work_today=WORK_TODAY)
		break
	except NotEnoughTime:
		#it's a little spamming to print this every time. do it better later
		print "[-] Not enough time available to finish your work in {} hours.".format(MAX_HOURS)
		print "[*] Trying with an additional hour per day."
		MAX_HOURS += 1

if MAX_HOURS >= 24:
	"[-] Not enough time available in 24 hours a day to finish your work. :("
	exit()

print "[+] Schedule successfully generated with max {} hours per day.".format(MAX_HOURS)
for i, plan in enumerate(agenda):
	if len(plan) > 0:
		day = index_to_date(i)
		hours_total = sum(x[1] for x in plan)
		print "{}, {} (work {} hours total):".format(week_index_to_day(day.weekday()), day, hours_total)
		for task, hours in plan:
			#print "    {}: {} hour{} ({} hour{} total)".format(task,
			#	hours, 's' if hours > 1 else '', task.hours, 's' if task.hours > 1 else '')
			print "    {}: {} hour{}".format(task, hours, 's' if hours > 1 else '')
