from hypothesis import given
from hypothesis.specifiers import integers_in_range
import datetime
from tasks import FixedTask, TaskList, Task
from main import CalendarPlanner

year = integers_in_range(2010, 2020)
month = integers_in_range(1, 12)
day = integers_in_range(1, 31)
hour = integers_in_range(0, 23)

@given([(str, (year, month, day, hour), (year, month, day, hour))])
def test_calcagenda_fixed(l):
    cal = CalendarPlanner()
    tasks = TaskList()
    for name, time1, time2 in l:
        try:
            task = FixedTask(name, datetime.datetime(*time1), datetime.datetime(*time2))
            tasks.add(task)
        except ValueError:
            pass
    cal.tasks = tasks
    cal.createAgenda()

@given([(str, int, int, (year, month, day))])
def test_calcagenda_assignments(l):
    cal = CalendarPlanner()
    tasks = TaskList()
    for name, hours, hours_done, due in l:
        try:
            task = Task(name, hours, hours_done, datetime.date(*due))
            tasks.add(task)
        except ValueError:
            pass
    cal.tasks = tasks
    cal.createAgenda()

@given([(int, int, (year, month, day))])
def test_get_hours_per_day_list(l):
    tl = TaskList()
    today = datetime.date.today()
    for hours, hours_done, due in l:
        try:
            due_dt = datetime.date(*due)
        except ValueError:
            #skip invalid dates
            continue
        if due_dt < today:
            #only care about tasks due in the future
            continue
        task = Task("test", hours, hours_done, due_dt)
        hours_day_list = tl._get_hours_per_day_list(task)
        #print hours_day_list
        assert sum(hours_day_list) == (task.hours - task.hours_done)
        assert 0 < len(set(hours_day_list)) < 3 #one or two hour options
        for i in xrange(len(hours_day_list)):
            for j in xrange(i+1, len(hours_day_list)):
                hours_day_list[i] >= hours_day_list[j]

test_calcagenda_fixed()
test_calcagenda_assignments()
test_get_hours_per_day_list()
