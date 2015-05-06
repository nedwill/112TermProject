from hypothesis import given, assume, Settings
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

#don't test names; no interesting bugs there
@given([(int, int, (year, month, day))], hour)#, settings=Settings(max_examples=5000))
def test_calcagenda_assignments(l, max_hours):
    #print max_hours, l
    tasks = TaskList()
    try:
        assume(all(datetime.date(*x[2]) > datetime.date.today() for x in l))
    except ValueError:
        return

    l = [(str(name), abs(hours), hours_done % (abs(hours) + 1), due) for (name,(hours, hours_done, due)) in enumerate(l)]
    for name, hours, hours_done, due in l:
        hours = abs(hours)
        hours_done %= (hours + 1) #keep in range of hours
        try:
            task = Task(name, hours, hours_done, datetime.date(*due))
            tasks.add(task)
        except ValueError:
            pass
    agenda = tasks.calcAgenda(max_hours)
    #what if we should be able to make an agenda but we don't?
    #difficult to model :(
    if agenda is not None:
        scheduled_hours = 0
        for day in agenda:
            for task, hours in day:
                scheduled_hours += hours
        #we could probably do better than <=
        #we need that because if max_hours is 0 we lose instantly
        #print "{} scheduled_hours".format(scheduled_hours),l
        assert scheduled_hours == sum(x[1] - x[2] for x in l)

#test_calcagenda_fixed()
test_calcagenda_assignments()
#test_calcagenda_assignments([(b'', 1538064, 1, (2017, 1, 3))], 8)
