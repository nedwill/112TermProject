from hypothesis import given, assume#, Settings
from hypothesis.specifiers import integers_in_range
import datetime
from tasks import FixedTask, TaskList, Task, InvalidTask
from main import CalendarPlanner

year = integers_in_range(2010, 2020)
month = integers_in_range(1, 12)
day = integers_in_range(1, 31)
hour = integers_in_range(0, 23)
recurring = integers_in_range(0, 6)

#fixed and recurring
@given([(str, [recurring], (year, month, day, hour), (year, month, day, hour))])
def test_calcagenda_fixed(l):
    cal = CalendarPlanner()
    tasks = TaskList()
    for name, recurring, time1, time2 in l:
        recurring = list(set(recurring)) #kill duplicates
        try:
            task = FixedTask(name, datetime.datetime(*time1), datetime.datetime(*time2), recurring)
            tasks.add(task)
        except ValueError:
            pass
    cal.tasks = tasks
    cal.createAgenda()

#don't test names; no interesting bugs there
#from hypothesis import Settings
#@given([(int, int, (year, month, day))], hour, bool, settings=Settings(max_examples=5000))
@given([(int, int, (year, month, day))], hour, bool)
def test_calcagenda_assignments(l, max_hours, max_days):
    #print max_hours, l
    tasks = TaskList()
    try:
        assume(all(datetime.date(*x[2]) > datetime.date.today() for x in l))
    except ValueError:
        return

    l = [(str(name), hours, hours_done, due) for (name, (hours, hours_done, due)) in enumerate(l)]
    for name, hours, hours_done, due in l:
        try:
            task = Task(name, hours, hours_done, datetime.date(*due))
            tasks.add(task)
        except ValueError:
            return
        except InvalidTask:
            return
    agenda = tasks.calc_agenda(max_hours, max_days=max_days)
    #what if we should be able to make an agenda but we don't?
    #difficult to model :(
    if agenda is not None:
        scheduled_hours = 0
        for day in agenda:
            for task, hours in day:
                scheduled_hours += hours
        assert scheduled_hours == sum(x[1] - x[2] for x in l)

#test_calcagenda_fixed()
test_calcagenda_assignments()
