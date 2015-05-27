import datetime
from tasks import FixedTask, Task
from bucket_scheduler import bucket_scheduler, grow_buckets

class NotEnoughTime(Exception):
    pass

class TaskManager(object):
    def __init__(self):
        self.fixed = {} #fixed tasks
        self.assignments = {} #assignments with due dates
        self.latest_task = datetime.date.today() #initialize last task date to today
        self.today = datetime.date.today()

    def get_due_dict(self):
        d = {}
        for k, v in self.assignments.iteritems():
            d[k] = v.due
        for k, v in self.fixed.iteritems():
            assert k not in d
            d[k] = v.due
        return d

    def add(self, task):
        if isinstance(task, FixedTask):
            if task.description in self.fixed:
                return
            self.fixed[task.description] = task
        elif isinstance(task, Task):
            if task.description in self.assignments:
                return
            self.assignments[task.description] = task
        if task.due > self.latest_task: #due date > lastestTask
            self.latest_task = task.due

    #now removing goes by the exact string
    #we should have a function that does fuzzy matching
    def remove(self, description):
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
            task.hours_done += hours
            if task.hours_done >= task.hours:
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
                return None
            assert newtask.description not in plan_tasks[i][1]
            plan_tasks[i][1][newtask.description] = newtask.hours

    def _calc_agenda_fixed(self, plan_tasks):
        for task in self.fixed.values():
            days_away = (task.due - self.today).days
            if days_away < 0:
                continue
            if task.recurring is not None and len(task.recurring) > 0:
                return self._calc_agenda_recurring(days_away, task, plan_tasks)
            #plan_tasks[days_away] is (hours_remaining, {name: hours_scheduled})
            if task.hours > plan_tasks[days_away][0]:
                return None
            plan_tasks[days_away][0] -= task.hours
            assert plan_tasks[days_away][0] >= 0 #should have checked this already
            assert task.description not in plan_tasks[days_away][1] #why would it already be in there?
            plan_tasks[days_away][1][task.description] = task.hours
        return plan_tasks

    def _calc_agenda_assignments(self, assignments, work_today, work_days, max_days, plan_tasks):
        if len(assignments) == 0 or plan_tasks is None:
            return plan_tasks

        if not work_today:
            plan_tasks[0][0] = 0

        today_day_of_week = datetime.date.weekday(self.today)
        for day in range(len(plan_tasks)):
            day_of_week = (today_day_of_week + day) % 7
            if day_of_week not in work_days:
                plan_tasks[day_of_week][0] = 0

        #format tasks in bucket_scheduler way
        tasks = [(task.description, task.hours-task.hours_done, (task.due - self.today).days) for task in assignments]
        
        #get the schedule
        plan_tasks = bucket_scheduler(plan_tasks, tasks)
        if max_days:
            plan_tasks = grow_buckets(plan_tasks, tasks)

        return plan_tasks

    def calc_agenda(self, max_hours, max_days=False, work_days=None, work_today=True):
        """
        max_days maximizes work in given time at expense of easy/time efficiency
        """
        #TODO: arguments to this function should be part
        #of the tasklist __init__, not passed here
        if max_hours == 0:
            return None
        if work_days is None:
            work_days = [0, 1, 2, 3, 4, 5, 6]
        max_days_needed = (self.latest_task - self.today).days+1
        #plan_tasks should consist of tuples but they don't support assignment
        #those lists are mutable tuples... maybe that should be fixed for cleanliness
        plan_tasks = [[max_hours, {}] for _ in xrange(max_days_needed)] #initialize with number of needed days
        plan_tasks = self._calc_agenda_fixed(plan_tasks)
        plan_tasks = self._calc_agenda_assignments(self.assignments.values(), work_today,
            work_days, max_days, plan_tasks)
        return plan_tasks
