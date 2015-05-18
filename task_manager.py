import datetime
from tasks import FixedTask, Task

class NotEnoughTime(Exception):
    pass

class TaskManager(object):
    def __init__(self):
        self.fixed = {} #fixed tasks
        self.assignments = {} #assignments with due dates
        self.latest_task = datetime.date.today() #initialize last task date to today
        self.today = datetime.date.today()

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

    #recurring tasks have an end
    def _calc_agenda_recurring(self, days_away, task, plan_tasks, max_hours):
        for i in xrange(days_away+1):
            dayOfWeek = datetime.date.weekday(self.today + datetime.timedelta(i))
            if dayOfWeek not in task.recurring:
                continue
            due = self.today + datetime.timedelta(i)
            startHour = datetime.time(task.startTime.hour)
            endHour = datetime.time(task.endTime.hour)
            startTime = datetime.datetime.combine(due,startHour)
            endTime = datetime.datetime.combine(due,endHour)
            #4 extra chars, find length to chop before recalling constructor
            choplength = len(str(task.startTime.hour) + str(task.endTime.hour)) + 8
            newtask = FixedTask(task.description[:-choplength],startTime,endTime,True)
            if newtask.hours + self._plan_hours(plan_tasks, i) <= max_hours:
                plan_tasks[i] += [(newtask,newtask.hours)] #add tuple of task and hours allotted for that day
            else:
                return None

    def _calc_agenda_fixed(self, max_hours, plan_tasks):
        for task in self.fixed.values():
            days_away = (task.due - self.today).days
            if days_away < 0:
                continue
            if task.recurring is not None and len(task.recurring) > 0:
                return self._calc_agenda_recurring(days_away, task, plan_tasks, max_hours)
            if task.hours + self._plan_hours(plan_tasks, days_away) > max_hours:
                return None
            plan_tasks[days_away] += [(task,task.hours)] #add tuple of task and hours allotted for that day
        return plan_tasks

    def _plan_hours_day(self, day_tasks):
        return sum(x[1] for x in day_tasks)

    def _plan_hours(self, plan_tasks, day):
        return self._plan_hours_day(plan_tasks[day])

    def _ceil_div(self, x, y):
        assert x >= 0 and y > 0
        return (x / y) + (1 if x % y > 0 else 0)

    #TODO: switch all of these functions to using dictionaries
    def _update_day_tasks(self, day_tasks, task, new_hours):
        #if already exists
        if any(task == x[0] for x in day_tasks):
            new_day_tasks = []
            for day_task, existing_hours in day_tasks:
                if day_task == task:
                    new_day_tasks.append((day_task, new_hours))
                else:
                    new_day_tasks.append((day_task, existing_hours))
            return new_day_tasks
        else:
            return day_tasks + [(task, new_hours)]

    #again, this could obviously be done so much better with a dict
    def _inc_day_task(self, day_tasks, task):
        #assume already exists
        new_day_tasks = []
        for day_task, existing_hours in day_tasks:
            if day_task == task:
                new_day_tasks.append((day_task, existing_hours+1))
            else:
                new_day_tasks.append((day_task, existing_hours))
        return new_day_tasks

    def _should_skip(self, task, assignments, day_tasks):
        "if another task with fewer hours assigned has more hours to add"
        hours_assigned = None
        for task_search, hours_assigned in day_tasks:
            if task_search == task:
                hours_used = hours_assigned
        tasks_with_fewer_hours = set()
        for task_search, hours_assigned in day_tasks:
            if task_search != task and hours_assigned < hours_used:
                tasks_with_fewer_hours.add(task_search.description)
        tasks_that_need_hours = set([task_search for (task_search, _) in assignments])
        return len(tasks_with_fewer_hours.intersection(tasks_that_need_hours)) > 0

    def _init_schedule_evenly(self, assignments, day_tasks, max_hours, start_day):
        """
        Given a list of assignments and a possibly pre-populated
        day_tasks, evenly assign work to be done as soon as possible.
        """
        assignments_new = []
        for task, hours_remaining in assignments:
            #assert (time.time() - start_time) < 2
            hours_used = self._plan_hours_day(day_tasks)
            days_remaining = (task.due - start_day).days
            if days_remaining <= 0:
                raise NotEnoughTime
            if hours_used < max_hours:
                hours_per_day = self._ceil_div(hours_remaining, days_remaining)
                hours_per_day = min(hours_per_day, max_hours - hours_used) #don't do too many hours
                #print "task",task,"day",start_day,"hours_per_day",hours_per_day
                if hours_remaining - hours_per_day > 0:
                    assignments_new.append((task, hours_remaining - hours_per_day))
                day_tasks = self._update_day_tasks(day_tasks, task, hours_per_day)
            else:
                if days_remaining == 0 and hours_remaining > 0:
                    raise NotEnoughTime #does this ever happen?
                assignments_new.append((task, hours_remaining))
        return day_tasks, assignments_new

    def _add_one_assignments(self, assignments, day_tasks, max_hours):
        """
        given a schedule of work for a day, try to add more hours to tasks
        to even out the amount done per day where possible
        e.g. Task 1: 4 hours, Task 2: 2 hours
        -> Task 1: 4 hours, Task 2: 4 hours if possible
        """
        assignments_new = []
        for task, hours_remaining in assignments:
            #try to make things even
            if self._should_skip(task, assignments, day_tasks):
                continue
            if self._plan_hours_day(day_tasks) < max_hours:
                if hours_remaining - 1 > 0:
                    assignments_new.append((task, hours_remaining - 1))
                day_tasks = self._inc_day_task(day_tasks, task)
            else:
                assignments_new.append((task, hours_remaining))
        return day_tasks, assignments_new

    def _fill_day_assignments(self, day_tasks, assignments, start_day, max_hours, max_days):
        day_tasks, assignments_new = self._init_schedule_evenly(assignments, day_tasks, max_hours, start_day)
        if max_days:
            while self._plan_hours_day(day_tasks) < max_hours and assignments != assignments_new:
                assignments = assignments_new
                day_tasks, assignments_new = self._add_one_assignments(assignments, day_tasks, max_hours)
        return day_tasks, assignments_new

    def _fill_day_trivially(self, day_tasks, assignments, start_day, max_hours, max_days):
        day_tasks, assignments_new = self._init_schedule_evenly(assignments, day_tasks, max_hours, start_day)
        assignments_new = []
        for task, hours_remaining in assignments:
            hours_used = self._plan_hours_day(day_tasks)
            days_remaining = (task.due - start_day).days
            if days_remaining <= 0:
                raise NotEnoughTime
            if hours_used < max_hours:
                hours_per_day = hours_remaining # don't divide evenly
                hours_per_day = min(hours_per_day, max_hours - hours_used) #don't do too many hours
                if hours_remaining - hours_per_day > 0:
                    assignments_new.append((task, hours_remaining - hours_per_day))
                day_tasks = self._update_day_tasks(day_tasks, task, hours_per_day)
            else:
                if days_remaining == 0 and hours_remaining > 0:
                    raise NotEnoughTime #does this ever happen?
                assignments_new.append((task, hours_remaining))
        return day_tasks, assignments_new

    def _calc_agenda_assignments(self, assignments, work_today,
        work_days, max_days, max_hours, plan_tasks, trivial):
        if len(assignments) == 0 or plan_tasks is None:
            return plan_tasks
        start_offset = 0 if work_today else 1
        start_day = self.today + datetime.timedelta(start_offset)
        #design choice: if we aren't working today and there is work due
        #tomorrow, we ignore it. maybe we should instead raise an exception
        #in this case
        max_days_needed = (self.latest_task - self.today).days+1
        assignments = sorted(assignments, key=lambda task: task.due)
        assignments_new = []
        for task in assignments:
            if task.due > start_day and task.hours - task.hours_done > 0:
                assignments_new.append((task, task.hours - task.hours_done))
        assignments = assignments_new
        #are we handling work_today right here?
        for day in range(max_days_needed):
            today_day_of_week = datetime.date.weekday(self.today)
            day_of_week = (today_day_of_week + day) % 7
            if day_of_week not in work_days:
                continue
            start_day = self.today + datetime.timedelta(day)
            try:
                if trivial:
                    plan_tasks[day], assignments = self._fill_day_trivially(plan_tasks[day],
                        assignments, start_day, max_hours, max_days)
                else:
                    plan_tasks[day], assignments = self._fill_day_assignments(plan_tasks[day],
                        assignments, start_day, max_hours, max_days)
            except NotEnoughTime:
                return None
        #if we couldn't plan out every assignment
        if len(assignments) > 0:
            return None
        return plan_tasks

    def calc_agenda(self, max_hours, max_days=False, work_days=None, work_today=True, trivial=False):
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
        plan_tasks = [[] for _ in xrange(max_days_needed)] #initialize with number of needed days
        plan_tasks = self._calc_agenda_fixed(max_hours, plan_tasks)
        plan_tasks = self._calc_agenda_assignments(self.assignments.values(), work_today,
            work_days, max_days, max_hours, plan_tasks, trivial)
        return plan_tasks