import datetime
import math

class Task(object): #recurring attribute here?
    def __init__(self,description,hours,hoursDone,due):
        self.description = description
        self.hours = hours
        self.hoursDone = hoursDone
        self.due = due #date object with relevant info
        #figure out recurring behavior (how do we know when to readd after
        #checking it off?)

    def __str__(self): #used to make ical
        return str(self.due.year) + str(self.due.month) + str(self.due.day)

    def __repr__(self):
        return str(self.description) + ", Hours Left: " + str(self.hours - \
            self.hoursDone) + ", Days Left: " + str((self.due - \
                datetime.date.today()).days)

class Assignment(Task): pass #same as Task?

class FixedTask(Task):
    def __init__(self,description,startTime,endTime,recurring=None):
        #this should be dealt with using time objects
        #done in make iCal as needed
        self.startTime = startTime
        self.endTime = endTime
        new = " " + str(startTime.hour) + ":" + "%02d" % startTime.minute \
        + "-" + str(endTime.hour) + ":" +  "%02d" % endTime.minute
        description += new
        #use actual timedelta to find hours
        hours = ((endTime - startTime).seconds)/3600
        due = startTime.date()
        hoursDone = 0 #can't have hours completed in advance on a fixed event
        self.recurring = recurring
        super(FixedTask, self).__init__(description,hours,hoursDone,due)

    def __repr__(self):
        return str(self.description) + ", Hours Left: " + str(self.hours \
            - self.hoursDone) + ", Days Left: " + str((self.due - \
                datetime.date.today()).days)

class TaskList(object):
    def __init__(self):
        self.fixed = [] #fixed tasks
        self.assignments = [] #assignments with due dates
        self.latestTask = datetime.date.today() #initialize last task date to today
        self.descriptionList = []
        #due dates written as month,day,year
        #calculate distance between two days

    def add(self,task):
        descriptionList = []
        for check in self.fixed:
            descriptionList += check.description
        for check in self.assignments:
            descriptionList += check.description
        if task.description in descriptionList: #make sure we don't have a duplicate assignment name
            #print "duped :("
            return
        #else:
        #    self.descriptionList += [task.description]
        if isinstance(task, FixedTask):
            self.fixed += [task]
            #print "Added fixed."
        elif isinstance(task, Task):
            self.assignments += [task]
        if task.due > self.latestTask: #due date > lastestTask
            self.latestTask = task.due

    def remove(self,description):
        for task in self.fixed: #find, remove, and return task from description
            if task.description[:len(description)] == description:
                self.fixed.remove(task)
                #self.descriptionList.remove(task.description)
                return task
        for task in self.assignments:
            if task.description[:len(description)] == description:
                self.assignments.remove(task)
                #self.descriptionList.remove(task.description)
                return task

    def addHours(self,description,hours):
        for task in self.fixed: #find, remove, and return task from description
            if task.description[:len(description)] == description:
                task.hoursDone += hours
                if task.hoursDone >= task.hours:
                    self.remove(description)
                return task
        for task in self.assignments:
            if task.description[:len(description)] == description:
                task.hoursDone += hours
                if task.hoursDone >= task.hours:
                    self.remove(description)
                return task

    def calcAgenda(self,maxHours,maxDays=False,workDays=None,workToday=True):
        """
        maxDays maximizes work in given time at expense of easy/time efficiency
        """
        if workDays is None:
            workDays = [0,1,2,3,4,5,6]
        start_day = datetime.date.today()
        if self.latestTask == start_day:
            plan_tasks = [[]]
            plan_hours = [0]
        else:
            plan_tasks = [[] for day in xrange((self.latestTask - start_day).days+1)] #[]*days until last assigned task
            plan_hours = [0]*((self.latestTask - start_day).days+1)
            self.assignments = sorted(self.assignments, key=lambda task: task.due)
        for task in self.fixed:
            days_away = (task.due - start_day).days
            if len(task.recurring) > 0:
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
                    if newtask.hours + plan_hours[i] <= maxHours:
                        plan_hours[i] += newtask.hours
                        plan_tasks[i] += [(newtask,newtask.hours)] #add tuple of task and hours allotted for that day
                    else:
                        return None
            else:
                if task.hours + plan_hours[days_away] <= maxHours:
                    plan_hours[days_away] += task.hours
                    plan_tasks[days_away] += [(task,task.hours)] #add tuple of task and hours allotted for that day
                else:
                    return None

        #cycle by index so we can check if we're on the last element
        for i in xrange(len(self.assignments)):
            task = self.assignments[i]
            print task.description
            if task.due < datetime.date.today(): continue
            #subtract one here to finish in advance
            days_away = (task.due - start_day).days
            hoursDone = task.hoursDone
            for day in xrange(days_away+1):
                hoursLeft = task.hours - hoursDone
                if hoursLeft == 0:
                    continue
                if day == 0 and workToday is False: continue
                dayOfWeek = datetime.date.weekday(datetime.date.today()+datetime.timedelta(day))
                if dayOfWeek not in workDays:
                    if day == days_away and hoursLeft != 0:
                        return None
                    else:
                        continue
                daysLeft = (days_away - day)
                workdaysremaining = 0
                for checkday in xrange(daysLeft):
                    if (dayOfWeek + checkday) % 7 in workDays:
                        workdaysremaining += 1
                if workdaysremaining == 0: return None
                if workdaysremaining == 1:
                    hoursPerDay = hoursLeft
                elif (i == (len(self.assignments) - 1) and maxDays is True):
                    hoursPerDay = min(maxHours - plan_hours[day],hoursLeft)
                else:
                    hoursPerDay = min(maxHours - plan_hours[day],int(math.ceil(float(hoursLeft)/(workdaysremaining))))
                if hoursPerDay == 0: continue
                if hoursPerDay + plan_hours[day] <= maxHours:
                    hoursDone += hoursPerDay
                    plan_hours[day] += hoursPerDay
                    plan_tasks[day] += [(task,hoursPerDay)]
                    #add tuple of task and hours allotted for that day
                elif day == days_away:
                    # if there are no days left, we can't
                    # complete this assignment
                    return None
        #print plan_hours
        return plan_tasks