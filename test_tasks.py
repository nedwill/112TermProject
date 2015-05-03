from hypothesis import given
from hypothesis.specifiers import integers_in_range
import datetime
from tasks import FixedTask, TaskList, Task
from main import CalendarPlanner

#(self,description,hours,hoursDone,due)
#(self,description,startTime,endTime,recurring=None)

#[{"type": "fixed", "name": "sample", "time2": [2012, 11, 28, 17], "time1": [2012, 11, 28, 17]}, {"hours": 5, "hours_done": 0, "type": "task", "name": "sample2", "due": [2012, 11, 28]}]

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

test_calcagenda_fixed()
test_calcagenda_assignments()
