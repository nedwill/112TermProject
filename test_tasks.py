from hypothesis import given, assume, Settings
from hypothesis.strategies import integers, text, booleans, lists, tuples
import datetime
from tasks import FixedTask, Task, InvalidTask
from task_manager import TaskManager
from main import Controller

year = integers(2010, 2020)
month = integers(1, 12)
day = integers(1, 31)
hour = integers(0, 23)
recurring = integers(0, 6)

#fixed and recurring
@given(lists(tuples(text(), lists(recurring), tuples(year, month, day, hour), tuples(year, month, day, hour))), integers())
def test_calcagenda_fixed(l, max_hours):
    tasks = TaskManager()
    for name, recurring, time1, time2 in l:
        recurring = list(set(recurring)) #kill duplicates
        try:
            task = FixedTask(name, datetime.datetime(*time1), datetime.datetime(*time2), recurring)
            tasks.add(task)
        except ValueError:
            pass
    tasks.calc_agenda(max_hours)

#don't test names; no interesting bugs there
#from hypothesis import Settings
#@given([(int, int, (year, month, day))], hour, bool, settings=Settings(max_examples=5000))
@given(lists(tuples(integers(), integers(), tuples(year, month, day))), hour, booleans())
def test_calcagenda_assignments(l, max_hours, max_days):
    #print max_hours, l
    tasks = TaskManager()
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
    agenda = tasks.calc_agenda(max_hours, max_days)
    #what if we should be able to make an agenda but we don't?
    #difficult to model :(
    trivial_agenda = tasks.calc_agenda(max_hours, max_days, trivial=True)
    assert (trivial_agenda is None) is (agenda is None)
    if agenda is not None:
        scheduled_hours = 0
        today = datetime.date.today()
        for i,day in enumerate(agenda):
            this_day_hours = 0
            for task, hours in day:
                assert task.due > (today + datetime.timedelta(i))
                assert 0 <= hours <= max_hours
                scheduled_hours += hours
                this_day_hours += hours
            assert this_day_hours <= max_hours
        assert scheduled_hours == sum(x[1] - x[2] for x in l)

test_calcagenda_fixed()
test_calcagenda_assignments()
