import datetime
from tasks import FixedTask, Task
from bucket_scheduler import bucket_scheduler, grow_buckets
from custom_exceptions import TaskAlreadyExists


class TaskManager(object):
    def __init__(self):
        self.fixed = {}  # fixed tasks
        self.assignments = {}  # assignments with due dates
        self.latest_task = datetime.date.today()  # initialize last task date to today

    def add(self, task):
        if task.description in set.union(set(self.fixed), set(self.assignments)):
            raise TaskAlreadyExists
        if isinstance(task, FixedTask):
            self.fixed[task.description] = task
        elif isinstance(task, Task):
            self.assignments[task.description] = task
        if task.due > self.latest_task:  # due date > lastestTask
            self.latest_task = task.due

    # now removing goes by the exact string
    # we should have a function that does fuzzy matching
    def remove(self, description):
        # super pernicious bug found with stateful testing
        description = unicode(description)
        if description in self.fixed:
            ret = self.fixed[description]
            del self.fixed[description]
            return ret
        elif description in self.assignments:
            ret = self.assignments[description]
            del self.assignments[description]
            return ret

    def add_hours(self, description, hours):
        if description in self.assignments:
            task = self.assignments[description]
            task.hours -= hours
            if task.hours <= 0:
                self.remove(description)
            return task

    def get_task(self, description):
        assert not (description in self.fixed and description in self.assignments)
        if description in self.fixed:
            return self.fixed[description]
        if description in self.assignments:
            return self.assignments[description]

    # recurring tasks have an end
    def _calc_agenda_recurring(self, days_away, task, plan_tasks):
        assert plan_tasks is not None
        for i in range(days_away + 1):
            dayOfWeek = datetime.date.weekday(
                datetime.date.today() + datetime.timedelta(i)
            )
            if dayOfWeek not in task.recurring:
                continue
            if task.hours > plan_tasks[i][0]:
                plan_tasks[i][0] = 0
            else:
                plan_tasks[i][0] -= task.hours
            assert task.description not in plan_tasks[i][1]
            plan_tasks[i][1][task.description] = task.hours
        return plan_tasks

    def _calc_agenda_fixed(self, plan_tasks):
        assert plan_tasks is not None
        for task in self.fixed.values():
            days_away = (task.due - datetime.date.today()).days
            if days_away < 0:
                continue
            if task.recurring is not None and len(task.recurring) > 0:
                plan_tasks = self._calc_agenda_recurring(days_away, task, plan_tasks)
            else:
                # plan_tasks[days_away] is (hours_remaining, {name: hours_scheduled})
                if task.hours > plan_tasks[days_away][0]:
                    plan_tasks[days_away][0] = 0
                else:
                    plan_tasks[days_away][0] -= task.hours
                assert plan_tasks[days_away][0] >= 0  # should have checked this already
                assert (
                    task.description not in plan_tasks[days_away][1]
                )  # why would it already be in there?
                plan_tasks[days_away][1][task.description] = task.hours
        return plan_tasks

    def _calc_agenda_assignments(self, assignments, work_today, max_days, plan_tasks):
        assert plan_tasks is not None
        if not work_today:
            plan_tasks[0][0] = 0

        # format tasks in bucket_scheduler way
        tasks = []
        for task in assignments:
            # TODO(nedwill): we should probably print expired tasks somewhere
            if task.due > datetime.date.today():
                tasks.append(task)

        # get the schedule
        plan_tasks = bucket_scheduler(plan_tasks, tasks)

        if max_days:
            plan_tasks = grow_buckets(plan_tasks, tasks)

        return plan_tasks

    def _format_for_app(self, plan_tasks):
        "should be list of (task, hours)"
        assert plan_tasks is not None
        new_plan_tasks = []
        for _, plan_dict in plan_tasks:
            # plan_dict is description -> hours
            plan_dict_list = [(self.get_task(x), y) for (x, y) in plan_dict.items()]
            new_plan_tasks.append(list(sorted(plan_dict_list, key=lambda x: x[0].due)))
        return new_plan_tasks

    def init_bucket(self, day, max_hours, work_days, user_specified_days):
        today_day_of_week = datetime.date.weekday(datetime.date.today())
        day_of_week = (today_day_of_week + day) % 7
        if day in user_specified_days:
            return [user_specified_days[day], {}]
        elif day_of_week not in work_days:
            return [0, {}]
        else:
            return [max_hours, {}]

    def calc_agenda(
        self,
        max_hours,
        max_days=False,
        work_days=None,
        work_today=True,
        user_specified_days=None,
    ):
        """
        max_days maximizes work in given time at expense of easy/time efficiency
        """
        # TODO: arguments to this function should be part
        # of the tasklist __init__, not passed here
        if work_days is None:
            work_days = [0, 1, 2, 3, 4, 5, 6]
        if user_specified_days is None:
            user_specified_days = {}
        max_days_needed = (self.latest_task - datetime.date.today()).days + 1
        # plan_tasks should consist of tuples but they don't support assignment
        # those lists are mutable tuples... maybe that should be fixed for cleanliness
        # initialize with number of needed days
        plan_tasks = [
            self.init_bucket(day, max_hours, work_days, user_specified_days)
            for day in range(max_days_needed)
        ]
        plan_tasks = self._calc_agenda_fixed(plan_tasks)
        plan_tasks = self._calc_agenda_assignments(
            self.assignments.values(), work_today, max_days, plan_tasks
        )
        # change format of output data
        plan_tasks = self._format_for_app(plan_tasks)
        return plan_tasks

    def num_tasks(self):
        return len(self.assignments) + len(self.fixed)
