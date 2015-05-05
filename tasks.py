import datetime
import math

class Task(object): #recurring attribute here?
    def __init__(self,description,hours,hoursDone,due):
        self.description = description
        self.hours = hours
        self.hoursDone = hoursDone
        self.due = due

    def __str__(self):
        return self.description

    def __repr__(self):
        return "{}, Hours Left: {}, Days Left: {}".format(self.description,
            self.hours - self.hoursDone, (self.due - datetime.date.today()).days)

class Assignment(Task):
    pass #same as Task?

class FixedTask(Task):
    def __init__(self,description,startTime,endTime,recurring=None):
        self.startTime = startTime
        self.endTime = endTime
        hours = ((endTime - startTime).seconds)/3600
        due = startTime.date()
        hoursDone = 0 #can't have hours completed in advance on a fixed event
        self.recurring = recurring
        super(FixedTask, self).__init__(description, hours, hoursDone, due)

    def __str__(self):
        return self.description + " {}:{:02d}-{}:{:02d}".format(self.startTime.hour,
            self.startTime.minute, self.endTime.hour, self.endTime.minute)

    def __repr__(self):
        return "{}, Hours Left: {}, Days Left: {}".format(self.description,
            self.hours - self.hoursDone, (self.due - datetime.date.today()).days)

class TaskList(object):
    def __init__(self):
        self.fixed = {} #fixed tasks
        self.assignments = {} #assignments with due dates
        self.latest_task = datetime.date.today() #initialize last task date to today

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

    def addHours(self, description, hours):
        if description in self.assignments:
            task = self.assignments[description]
            task.hoursDone += hours
            if task.hoursDone >= task.hours:
                self.remove(description)
                return task

    def calc_agenda_recurring(self, days_away, task, start_day, plan_tasks, max_hours):
        for i in xrange(days_away+1):
            dayOfWeek = datetime.date.weekday(datetime.date.today()+datetime.timedelta(i))
            if dayOfWeek not in task.recurring:
                continue
            due = start_day + datetime.timedelta(i)
            startHour = datetime.time(task.startTime.hour)
            endHour = datetime.time(task.endTime.hour)
            startTime = datetime.datetime.combine(due,startHour)
            endTime = datetime.datetime.combine(due,endHour)
            #4 extra chars, find length to chop before recalling constructor
            choplength = len(str(task.startTime.hour) + str(task.endTime.hour)) + 8
            newtask = FixedTask(task.description[:-choplength],startTime,endTime,True)
            if newtask.hours + self.plan_hours(plan_tasks[i]) <= max_hours:
                plan_tasks[i] += [(newtask,newtask.hours)] #add tuple of task and hours allotted for that day
            else:
                return None

    def calc_agenda_fixed(self, start_day, max_hours, plan_tasks):
        for task in self.fixed.values():
            days_away = (task.due - start_day).days
            if days_away < 0:
                continue
            if task.recurring is not None and len(task.recurring) > 0:
                return self.calc_agenda_recurring(days_away, task, start_day, plan_tasks, max_hours)
            if task.hours + self.plan_hours(plan_tasks[days_away]) > max_hours:
                return None
            plan_tasks[days_away] += [(task,task.hours)] #add tuple of task and hours allotted for that day
            return plan_tasks

    def plan_hours(self, day):
        return sum(x[1] for x in day)

    def ceil_div(x, y):
        return int(math.ceil(float(x)/(y)))

    def get_days_left(day, days_away, day_of_week, work_days):
        days_left = (days_away - day)
        workdays_remaining = 0
        for checkday in xrange(days_left):
            if (day_of_week + checkday) % 7 in work_days:
                workdays_remaining += 1
        return workdays_remaining

    def pick_hours_to_assign(self, plan_tasks, day, days_away, max_hours, day_of_week, work_days, task, last_task, max_days):
        hours_left_for_task = task.hours - task.hoursDone
        hours_available_to_schedule = max_hours - self.plan_hours(plan_tasks[day])
        workdays_remaining = self.get_days_left(day, days_away, day_of_week, work_days)
        if workdays_remaining == 0:
            #if no days left, we fail at scheduling
            return None
        elif workdays_remaining == 1:
            #if one day left, use the remaining hours because we have to
            return hours_left_for_task
        elif (task == last_task and max_days):
            #if last assignment and we're doing max_days, drop all hours possible on the task
            return min(hours_available_to_schedule, hours_left_for_task)
        else:
            return min(hours_available_to_schedule, self.ceil_div(hours_left_for_task, workdays_remaining))

    def calc_agenda_assignments(self, assignments, start_day, work_today, work_days, max_days, max_hours, plan_tasks):
        if len(assignments) == 0:
            return plan_tasks

        def get_due(task):
            return task.due
        assignments = sorted(assignments, key=get_due)

        last_task = assignments[-1]
        today_day_of_week = datetime.date.weekday(datetime.date.today())

        for task in assignments:
            #skip tasks due in the past
            if task.due < datetime.date.today():
                continue
            #subtract here if you want to finish things in advance
            days_away = (task.due - start_day).days
            for day in xrange(days_away+1):
                hours_left_for_task = task.hours - task.hoursDone
                if hours_left_for_task == 0:
                    continue
                if day == 0 and work_today is False:
                    continue
                day_of_week = (today_day_of_week + day) % 7
                if day_of_week not in work_days:
                    if day == days_away and hours_left_for_task != 0:
                        return None
                    else:
                        continue
                hours_per_day = self.pick_hours_to_assign(plan_tasks, day, days_away,
                    max_hours, day_of_week, work_days, task, last_task, max_days)
                if hours_per_day > 0 and hours_per_day + self.plan_hours(plan_tasks[day]) <= max_hours:
                    task.hoursDone += hours_per_day
                    plan_tasks[day] += [(task, hours_per_day)]
                    #add tuple of task and hours allotted for that day
                elif day == days_away:
                    return None
        return plan_tasks

    def calcAgenda(self,max_hours,max_days=False,work_days=None,work_today=True):
        """
        max_days maximizes work in given time at expense of easy/time efficiency
        """
        if work_days is None:
            work_days = [0,1,2,3,4,5,6]
        start_day = datetime.date.today()
        days_needed = (self.latest_task - start_day).days+1
        plan_tasks = [[] for day in xrange(days_needed)] #initialize with number of needed days
        plan_tasks = self.calc_agenda_fixed(start_day, max_hours, plan_tasks)
        plan_tasks = self.calc_agenda_assignments(self.assignments.values(), start_day, work_today, work_days, max_days, max_hours, plan_tasks)
        return plan_tasks
