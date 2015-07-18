import datetime
from tasks import FixedTask, Task
from bucket_scheduler import bucket_scheduler, grow_buckets
from custom_exceptions import TaskAlreadyExists

class TaskManager(object):
    def __init__(self):
        self.fixed = {} #fixed tasks
        self.assignments = {} #assignments with due dates
        self.latest_task = datetime.date.today() #initialize last task date to today
        self.today = datetime.date.today()

    def add(self, task):
        if task.description in set.union(set(self.fixed), set(self.assignments)):
            raise TaskAlreadyExists
        if isinstance(task, FixedTask):
            self.fixed[task.description] = task
        elif isinstance(task, Task):
            self.assignments[task.description] = task
        if task.due > self.latest_task: #due date > lastestTask
            self.latest_task = task.due

    #now removing goes by the exact string
    #we should have a function that does fuzzy matching
    def remove(self, description):
        description = unicode(description) #super pernicious bug found with stateful testing
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

    #recurring tasks have an end
    def _calc_agenda_recurring(self, days_away, task, plan_tasks):
        assert plan_tasks is not None
        for i in xrange(days_away+1):
            dayOfWeek = datetime.date.weekday(self.today + datetime.timedelta(i))
            if dayOfWeek not in task.recurring:
                continue
            due = self.today + datetime.timedelta(i)
            startHour = datetime.time(task.startTime.hour)
            endHour = datetime.time(task.endTime.hour)
            startTime = datetime.datetime.combine(due,startHour)
            endTime = datetime.datetime.combine(due,endHour)
            #making a new task here might be wrong... we can design this better
            newtask = FixedTask(task.description, startTime, endTime, True)
            if newtask.hours > plan_tasks[i][0]:
                plan_tasks[i][0] = 0
            else:
                plan_tasks[i][0] -= newtask.hours
            assert newtask.description not in plan_tasks[i][1]
            plan_tasks[i][1][newtask.description] = newtask.hours
        return plan_tasks

    def _calc_agenda_fixed(self, plan_tasks):
        assert plan_tasks is not None
        for task in self.fixed.values():
            days_away = (task.due - self.today).days
            if days_away < 0:
                continue
            if task.recurring is not None and len(task.recurring) > 0:
                return self._calc_agenda_recurring(days_away, task, plan_tasks)
            #plan_tasks[days_away] is (hours_remaining, {name: hours_scheduled})
            if task.hours > plan_tasks[days_away][0]:
                plan_tasks[days_away][0] = 0
            else:
                plan_tasks[days_away][0] -= task.hours
            assert plan_tasks[days_away][0] >= 0 #should have checked this already
            assert task.description not in plan_tasks[days_away][1] #why would it already be in there?
            plan_tasks[days_away][1][task.description] = task.hours
        return plan_tasks

    def _calc_agenda_assignments(self, assignments, work_today, work_days, user_specified_days, max_days, plan_tasks):
        assert plan_tasks is not None
        if not work_today:
            plan_tasks[0][0] = 0

        today_day_of_week = datetime.date.weekday(self.today)
        for day in xrange(len(plan_tasks)):
            day_of_week = (today_day_of_week + day) % 7
            if day in user_specified_days:
                plan_tasks[day][0] = user_specified_days[day]
            elif day_of_week not in work_days:
                plan_tasks[day][0] = 0

        #format tasks in bucket_scheduler way
        tasks = []
        for task in assignments:
            if task.due > self.today:
                tasks.append((task.description, task.hours, (task.due - self.today).days))
        
        #get the schedule
        plan_tasks = bucket_scheduler(plan_tasks, tasks)

        if max_days:
            plan_tasks = grow_buckets(plan_tasks, tasks)

        return plan_tasks

    def _format_for_app(self, plan_tasks):
        "should be list of (task, hours)"
        assert plan_tasks is not None
        new_plan_tasks = []
        for _hours_remaining, plan_dict in plan_tasks:
            #plan_dict is description -> hours
            plan_dict_list = [(self.get_task(x), y) for (x, y) in plan_dict.items()]
            new_plan_tasks.append(list(sorted(plan_dict_list, key=lambda x: x[0].due)))
        return new_plan_tasks

    def calc_agenda(self, max_hours, max_days=False, work_days=None, work_today=True, user_specified_days={}):
        """
        max_days maximizes work in given time at expense of easy/time efficiency
        """
        #TODO: arguments to this function should be part
        #of the tasklist __init__, not passed here
        if work_days is None:
            work_days = [0, 1, 2, 3, 4, 5, 6]
        max_days_needed = (self.latest_task - self.today).days+1
        #plan_tasks should consist of tuples but they don't support assignment
        #those lists are mutable tuples... maybe that should be fixed for cleanliness
        plan_tasks = [[max_hours, {}] for _ in xrange(max_days_needed)] #initialize with number of needed days
        plan_tasks = self._calc_agenda_fixed(plan_tasks)
        plan_tasks = self._calc_agenda_assignments(self.assignments.values(), work_today, work_days, user_specified_days, max_days, plan_tasks)
        plan_tasks = self._format_for_app(plan_tasks) #change format of output data
        return plan_tasks
