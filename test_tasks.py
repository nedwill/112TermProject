from hypothesis import given, Settings, example
from hypothesis.strategies import integers, booleans, lists, tuples
import datetime
from tasks import InvalidTask, FixedTask
from planner import Planner

year = integers(2015, 2016)
month = integers(6, 12)
day = integers(1, 31)
hour = integers(0, 23)
recurring = integers(0, 2**7-1)
hours = integers(0, 100)

def days(x):
    assert 0 <= x < 2**7
    ret = []
    for i in range(7):
        if (x >> i) & 1:
            ret.append(i)
    return ret

real_today = datetime.date.today()
real_tomorrow = real_today + datetime.timedelta(1)
real_dayafter = real_today + datetime.timedelta(2)

@given(lists(tuples(recurring, tuples(year, month, day, hour), hour)), lists(tuples(hours, hours,
    tuples(year, month, day))), hour, booleans(), settings=Settings(max_examples=10000))
@example([(0, (real_tomorrow.year, real_tomorrow.month, real_tomorrow.day, 10), 18)],
    [(8, 0, (real_dayafter.year, real_dayafter.month, real_dayafter.day))], 8, True)
def test_calcagenda(fixed_l, l, max_hours, max_days):
    planner = Planner(max_hours=max_hours, max_days=max_days, debug=True)
    fixed_l = [("fixed"+str(name), recurring, time1, time2_hour) for (name, (recurring, time1, time2_hour)) in enumerate(fixed_l)]
    for name, recurring, time1, time2_hour in fixed_l:
        (year, month, day, _) = time1
        time2 = (year, month, day, time2_hour) #just a different hour
        recurring = days(recurring)
        if len(recurring) == 0:
            recurring = None
        try:
            planner.add_fixed_task(name, datetime.datetime(*time1), datetime.datetime(*time2), recurring)
        except ValueError:
            return
        except InvalidTask:
            return
    l = [(str(name), hours, hours_done, due) for (name, (hours, hours_done, due)) in enumerate(l)]
    for name, hours, hours_done, due in l:
        try:
            planner.add_task(name, hours, hours_done, datetime.date(*due))
        except ValueError:
            return
        except InvalidTask:
            return
    agenda = planner.create_agenda_safe()
    trivial_agenda = planner.create_agenda_trivial()
    planner.toggle_max_days()
    other_agenda = planner.create_agenda_safe()
    assert (trivial_agenda is None) is (agenda is None) is (other_agenda is None)
    if agenda is not None:
        scheduled_hours = 0
        today = datetime.date.today()
        total_hours = sum(x[1] - x[2] for x in l)
        total_hours += sum(x[3] - x[2][3] for x in fixed_l)
        for i,day in enumerate(agenda):
            this_day_hours = 0
            for task, hours in day:
                if isinstance(task, FixedTask):
                    assert task.due >= (today + datetime.timedelta(i))
                else:
                    assert task.due > (today + datetime.timedelta(i))
                assert 0 <= hours <= max_hours
                scheduled_hours += hours
                this_day_hours += hours
            assert this_day_hours <= max_hours
        assert scheduled_hours == total_hours

test_calcagenda()
