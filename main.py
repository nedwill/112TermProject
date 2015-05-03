#Edward Williamson
#Andrew: edwillia
#Recitation: Section F

import datetime
import calendar
import tkSimpleDialog
import tkMessageBox
import json
import os
from tasks import TaskList, FixedTask, Task
from Tkinter import Tk, FALSE, Canvas, Button
from graphics import gCalendar, Agenda

class CalendarPlanner(object):
    def __init__(self,width=900,height=600,selectedDayDistance=0,
        maxHours=8,maxDays=False):
        self.width = width
        self.height = height
        self.today = datetime.date.today()
        self.tasks = TaskList()
        self.selectedDayDistance = selectedDayDistance
        self.maxHours = maxHours
        self.maxDays = maxDays
        calendarPlanner = calendar.monthcalendar(self.today.year, self.today.month)
        self.dragTask = None
        self.taskDraw = None
        self.workDays = [0,1,2,3,4,5,6]
        self.workToday = True
        for row in xrange(len(calendarPlanner)):
            for col in xrange(7):
                if calendarPlanner[row][col] == self.today.day:
                    self.row = row
                    self.col = col

    def getAgendaDays(self):
        today = datetime.date.today()
        days = []
        for i in xrange(len(self.agendaCalc)):
            days += [today+datetime.timedelta(i)]
        return days

    def calSearch(self):
        #prompt user for name of task, all tasks with matching initial chars
        #are highlighted
        calSearch = "ECE" #temp
        self.cal.foundTask = False
        calSearch = tkSimpleDialog.askstring("Task Finder",
         "What is the name of your task?")
        if calSearch is None: return
        self.cal.draw(self,calSearch)
        if self.cal.foundTask is False:
            tkMessageBox.showinfo("Task Not Found",
             "The task you described is not present in this month.")

    def clearData(self):
        check = tkMessageBox.askyesno("Are you sure?",
         "Are you sure you want to clear all of your data?")
        if check is True:
            self.tasks = TaskList() #reinitialize
            self.saveData()
            self.createAgenda() #update agenda
            self.selectAgenda(self.row,self.col)
            self.agenda.draw(self.selectedAgenda)
            self.cal.draw(self)

    def saveData(self):
        with open("schedule.dat", "w") as f:
            data = {
                "tasks": self.tasks,
                "max_hours": self.maxHours,
                "max_days": self.maxDays,
                "work_days": self.workDays
            }
            f.write(json.dumps(data))

    def loadData(self):
        #try:
        with open("schedule.dat", "r") as f:
            data = json.loads(f.read())
            self.tasks = data["tasks"]
            self.maxHours = data["hours"]
            self.maxDays = data["max_days"]
            self.workDays = data["work_days"]
            self.createAgenda() #update agenda
            self.selectAgenda(self.row,self.col)
            self.agenda.draw(self.selectedAgenda)
            self.cal.draw(self)
        #except:
        #    tkMessageBox.showwarning("Couldn't Load Data",
        #     "The data file exists but it could not be loaded!")

    def createAgenda(self):
        self.agendaCalc = self.tasks.calcAgenda(self.maxHours,self.maxDays,self.workDays,self.workToday)

    def drawDragDrop(self,event):
        if self.taskDraw is not None:
            self.canvas.delete(self.taskDraw)
            x = event.x
            y = event.y
            self.taskDraw = self.canvas.create_text(x,y,
                text=self.dragTask[0].description,
                font=("Helvetica", 18, "bold"))

    def checkIfAgenda(self,event):
        x = event.x
        y = event.y
        left = int(self.agenda.left)
        top = int(self.agenda.top)
        right = int(self.agenda.right)
        bottom = int(self.agenda.bottom)
        if left < x < right and top + 20 < y < bottom:
            index = (y - top - 20) / 20 #get index
            if len(self.selectedAgenda) > index:
                self.dragTask = self.selectedAgenda[index]
                self.taskDraw = self.canvas.create_text(x,y,
                    text=self.dragTask[0].description,
                    font=("Helvetica", 18, "bold"))

    def placeTask(self,date):
        task = self.dragTask[0]
        originaldue = task.due
        task.due = date
        if hasattr(task,"recurring"):
            if task.recurring is True:
                tkMessageBox.showerror("Impossible to Schedule",
                 "You can't reschedule a recurring task!")
                return
        if date < datetime.date.today():
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't reschedule that task to the past!")
            return
        if date > self.tasks.latestTask:
            self.tasks.latestTask = date
        def failure():
            task.due = originaldue
        self.attempt_to_schedule(failure,
            "You can't finish that task in the given time per day!")

    def tryToPlace(self,event):
        x = event.x
        y = event.y
        left = int(self.cal.left) #take all information from calendar
                                  #class, no copy-paste
        top = int(self.cal.top)
        #right = int(self.cal.right)
        #bottom = int(self.cal.bottom)
        cellWidth = int(self.cal.cellWidth)
        cellHeight = int(self.cal.cellHeight)
        col = (x - left) / cellWidth
        row = (y - top) / cellHeight
        day = self.cal.monthArray
        if row >= 0 and col >= 0 and row < self.cal.weeks and col < 7:
            day = self.cal.monthArray[row][col]
            if day != 0:
                month = self.cal.month
                year = self.cal.year
                date = datetime.date(year,month,day)
                #self.row = row #used for new selected Agenda?
                #self.col = col
                self.placeTask(date)

    def mouseReleased(self,event):
        if self.dragTask is not None:
            self.tryToPlace(event)
            self.canvas.delete(self.taskDraw)
            self.dragTask = None
            self.taskDraw = None

    def mouseMotion(self,event):
        self.drawDragDrop(event)

    def mousePressed(self,event):
        x = event.x
        y = event.y
        #print x,y
        self.checkIfAgenda(event)
        if self.dragTask is not None:
            return
        left = int(self.cal.left) #take all information from calendar class,
                                  #no copy-paste
        top = int(self.cal.top)
        #right = int(self.cal.right)
        #bottom = int(self.cal.bottom)
        cellWidth = int(self.cal.cellWidth)
        cellHeight = int(self.cal.cellHeight)
        col = (x - left) / cellWidth
        row = (y - top) / cellHeight
        selectedAgenda = self.selectAgenda(row,col)
        if selectedAgenda is not None:
            self.agenda.draw(selectedAgenda)
            self.row = row
            self.col = col
        elif row >= 0 and col >= 0 and row < self.cal.weeks and col < 7:
            if self.cal.monthArray[row][col] != 0:
                self.agenda.clear()
                self.row = row
                self.col = col
            elif row > 0:
                self.nextMonth()
                row = 0
                self.row = row
                self.col = col
                selectedAgenda = self.selectAgenda(row,col)
                if selectedAgenda is not None:
                    self.agenda.draw(selectedAgenda)
                else:
                    self.agenda.clear()
            elif row == 0:
                self.previousMonth()
                row = len(self.cal.monthArray) - 1
                self.row = row
                self.col = col
                selectedAgenda = self.selectAgenda(row,col)
                if selectedAgenda is not None:
                    self.agenda.draw(selectedAgenda)
                else:
                    self.agenda.clear()

    def selectAgenda(self,row,col): #only run this after creating an agenda
                                    #first
        #check for self.agenda's existence/initialization
        if row >= 0 and col >= 0 and row < self.cal.weeks and col < 7 and\
         self.cal.monthArray[row][col] != 0:
            selectedDay = datetime.date(self.cal.year,self.cal.month,
                self.cal.monthArray[row][col])
            self.cal.selectedDay = selectedDay
            self.cal.clear()
            self.cal.draw(self)
            selectedDayDistance = (selectedDay - datetime.date.today()).days
            #if selectedDayDistance > 0 and selectedDayDistance < len(agenda):
            selectedAgenda = None
            if selectedDayDistance >= 0 and selectedDayDistance <\
             len(self.agendaCalc):
                selectedAgenda = self.agendaCalc[selectedDayDistance]
                self.selectedAgenda = selectedAgenda
            return selectedAgenda

    def getAgenda(self,row,col):
        if row >= 0 and col >= 0 and row < self.cal.weeks and col < 7 and\
         self.cal.monthArray[row][col] != 0:
            selectedDay = datetime.date(self.cal.year,self.cal.month,
                self.cal.monthArray[row][col])
            selectedDayDistance = (selectedDay - datetime.date.today()).days
            selectedAgenda = None
            if selectedDayDistance >= 0 and selectedDayDistance <\
             len(self.agendaCalc):
                selectedAgenda = self.agendaCalc[selectedDayDistance]
            return selectedAgenda

    def setMaxHours(self):
        original = self.maxHours
        maxHours = tkSimpleDialog.askinteger("Hour Set",
         "How many hours will you work per day? Currently " +\
          str(self.maxHours) + " hours.")
        if maxHours is None: return
        if maxHours > 24 or maxHours < 0:
            tkMessageBox.showerror("Impossible",
             "Please enter an integer 0-24.")
            return
        self.maxHours = maxHours
        def failure():
            self.maxHours = original
        self.attempt_to_schedule(failure, 
            "You can't finish your tasks in the given work hours per day!")
        self.canvas.delete(self.agendaTitle)
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,text="Agenda (" + str(self.maxHours) +\
             " hour days)",font=("Helvetica", 20, "bold"))

    def toggleMaxDays(self):
        self.maxDays = not self.maxDays
        def failure():
            self.maxDays = not self.maxDays
        self.attempt_to_schedule(failure,
            "You can't finish your tasks if you toggle your schedule optimization!")

    def addAssignment(self): #graphical implementation
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description is None: return
        hours = tkSimpleDialog.askinteger("Task Adder",
         "How many hours will it take to complete?")
        if hours is None: return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "When is it due? Enter MM/DD or MM/DD/YYYY")
        if dueString is None: return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year,month,day)
        except:
            tkMessageBox.showerror("Date Entry Error",
             "Invalid Date Entered!")
        if due < datetime.date.today():
            tkMessageBox.showerror("Date Entry Error",
             "You can't add something in the past!")
            return
        hoursDone = 0 #is this assumption safe?
        #due = parsed(dueString)
        task = Task(description,hours,hoursDone,due)
        self.tasks.add(task)
        #print task.description,task.hours,task.hoursDone,task.due
        def failure():
            self.tasks.remove(task.description)
        self.attempt_to_schedule(failure,
            "You can't finish that task in the given time per day!")

    def addFixedTask(self): #same, but with a fixed task
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description is None: return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "What day is it? Enter MM/DD or MM/DD/YYYY")
        if dueString is None: return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year,month,day)
        except:
            tkMessageBox.showerror("Date Entry Error",
             "Invalid Date Entered!")
        if due < datetime.date.today():
            tkMessageBox.showerror("Date Entry Error",
             "You can't add something in the past!")
            return
        timeString = tkSimpleDialog.askstring("Task Adder",
         "What time is it? Enter HH-HH or HH:MM-HH:MM")
        #print timeString
        if timeString is None:
            return
        if len(timeString) == 5 and timeString[2] == "-":
            startTime = int(timeString[0:2])
            endTime = int(timeString[3:5])
            if (startTime < 0 or endTime < 0 or startTime > 24 or\
             endTime > 24 or startTime > endTime):
                tkMessageBox.showerror("Time Entry Error",
                 "Invalid Time Range Entered!")
                return
            startTime = datetime.datetime(due.year,due.month,
            due.day,int(timeString[0:2])) #fix this for efficiency?
            endTime = datetime.datetime(due.year,due.month,
                due.day,int(timeString[3:5]))
        elif len(timeString) == 11 and timeString[2] == ":" and\
         timeString[5] == "-" and timeString[8] == ":":
            startHour = int(timeString[0:2])
            startMinutes = int(timeString[3:5])
            endHour = int(timeString[6:8])
            endMinutes = int(timeString[9:12])
            try:
                startTime = datetime.datetime(due.year,due.month,
                    due.day,startHour,startMinutes)
                endTime = datetime.datetime(due.year,due.month,
                    due.day,endHour,endMinutes)
            except:
                tkMessageBox.showerror("Time Entry Error",
                 "Invalid Time Range Entered!")
                return
        else:
            tkMessageBox.showerror("Time Entry Error",
             "Invalid Time Range Entered!")
            return
        task = FixedTask(description,startTime,endTime)
        self.tasks.add(task)
        def failure():
            self.tasks.remove(task.description)
        self.attempt_to_schedule(failure,
            "You can't finish that task in the given time per day!")

    def addRecurringTask(self):
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description is None: return
        recurringDays = tkSimpleDialog.askstring("Recurring Days","Enter comma separated days: e.g. \"0,1,2,3,4,5,6\"")
        if recurringDays is None: return
        recurring = []
        for i in xrange(0,len(recurringDays),2):
            recurring += [int(recurringDays[i])]
        if len(recurring) == 0 or min(recurring) < 0 or max(recurring) > 6:
            tkMessageBox.showerror("Invalid Entry",
             "Invalid Day List!")
            return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "Repeat until which day? Enter MM/DD or MM/DD/YYYY")
        if dueString is None: return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year,month,day)
        except:
            tkMessageBox.showerror("Date Entry Error",
             "Invalid Date Entered!")
            return
        if due < datetime.date.today():
            tkMessageBox.showerror("Date Entry Error",
             "You can't add something in the past!")
            return
        timeString = tkSimpleDialog.askstring("Task Adder",
         "What time is it? Enter HH-HH or HH:MM-HH:MM")
        #print timeString
        if timeString is None:
            return
        if len(timeString) == 5 and timeString[2] == "-":
            startTime = int(timeString[0:2])
            endTime = int(timeString[3:5])
            if (startTime < 0 or endTime < 0 or startTime > 24 or\
             endTime > 24 or startTime > endTime):
                tkMessageBox.showerror("Time Entry Error",
                 "Invalid Time Range Entered!")
                return
            startTime = datetime.datetime(due.year,due.month,due.day,
            int(timeString[0:2])) #fix this for efficiency?
            endTime = datetime.datetime(due.year,due.month,due.day,
                int(timeString[3:5]))
        elif len(timeString) == 11 and timeString[2] == ":" and\
         timeString[5] == "-" and timeString[8] == ":":
            startHour = int(timeString[0:2])
            startMinutes = int(timeString[3:5])
            endHour = int(timeString[6:8])
            endMinutes = int(timeString[9:12])
            try:
                startTime = datetime.datetime(due.year,due.month,due.day,
                    startHour,startMinutes)
                endTime = datetime.datetime(due.year,due.month,due.day,
                    endHour,endMinutes)
            except:
                tkMessageBox.showerror("Time Entry Error",
                 "Invalid Time Range Entered!")
                return
        else:
            tkMessageBox.showerror("Time Entry Error",
             "Invalid Time Range Entered!")
            return
        task = FixedTask(description,startTime,endTime,recurring)
        self.tasks.add(task)
        def failure():
            self.tasks.remove(task.description)
        self.attempt_to_schedule(failure,
            "You can't finish that task in the given time per day!")

    def removeTask(self):
        description = tkSimpleDialog.askstring("Task Remover",
         "What is the name of your task?")
        if description is None:
            return
            #tkMessageBox.showerror("Error", "You must provide a description!")
        removed = self.tasks.remove(description)
        if removed is None:
            tkMessageBox.showinfo("You Should Know...",
             "There was no task found matching that description!")
            return
        self.createAgenda() #update agenda
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def addHours(self):
        description = tkSimpleDialog.askstring("Task Completer",
         "What is the name of your task?")
        if description is None:
            return
            #tkMessageBox.showerror("Error", "You must provide a description!")
        hours = tkSimpleDialog.askinteger("Task Completer",
         "How many hours did you complete?")
        if hours is None:
            return
        added = self.tasks.addHours(description,hours)
        if added is None:
            tkMessageBox.showinfo("You Should Know...",
             "There was no task found matching that description!")
            return
        self.createAgenda() #update agenda
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    #@classmethod
    def testAgenda(self):
        tasks = [FixedTask("meeting",datetime.datetime(2012,11,28,17),
            datetime.datetime(2012,11,28,18)),
                Task("C@CM",1,0,datetime.date.today()),Task("ECE study",
                    5,0,datetime.date(2012,11,25)),
                Task("Calc WebAssign",2,0,datetime.date(2012,11,28)),
                Task("CS project",25,0,datetime.date(2012,12,03))]
        myTasks = TaskList()
        for task in tasks:
            myTasks.add(task)
        self.tasks = myTasks

    def previousMonth(self):
        if self.today.month > 1:
            self.today.month -= 1
        else:
            self.today.month = 12
            self.today.year -= 1
        self.cal.clear()
        self.cal = gCalendar(self.canvas,self.width,self.height,
            self.today.month,self.today.year)
        self.cal.draw(self)

    def nextMonth(self):
        if self.today.month < 12:
            self.today.month += 1
        else:
            self.today.month = 1
            self.today.year += 1
        self.cal.clear()
        self.cal = gCalendar(self.canvas,self.width,self.height,
            self.today.month,self.today.year)
        self.cal.draw(self)

    def toggleDayHelper(self,dayint):
        if dayint in self.workDays:
            self.workDays.remove(dayint)
        else:
            self.workDays.append(dayint)

    #call failure if we can't schedule
    def attempt_to_schedule(self, failure, err_msg):
        assert self.agendaCalc is not None #already working
        self.createAgenda()
        if self.agendaCalc is None:
            tkMessageBox.showerror("Impossible to Schedule", err_msg)
            failure()
            self.createAgenda()
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def toggleWorkDay(self):
        dayint = tkSimpleDialog.askinteger("Workday Toggler",
            "Which day do you want to toggle?")
        if dayint is None: return
        if not (0 <= dayint <= 6):
            tkMessageBox.showerror("Invalid Input", "Please enter a day 0-6.")
            return
        self.toggleDayHelper(dayint)
        def failure():
            self.toggleDayHelper(dayint)
        self.attempt_to_schedule(failure,
            "You can't finish your tasks if you toggle that day!")

    def toggleToday(self):
        self.workToday = not self.workToday
        def failure():
            self.workToday = not self.workToday
        self.attempt_to_schedule(failure,
            "You can't finish your tasks if you toggle that day!")

    def init(self):
        #draw calendar label
        self.cal = gCalendar(self.canvas,self.width,self.height,
            self.today.month,self.today.year)
        self.createAgenda()
        self.cal.draw(self)
        #draw agenda label
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,
            text="Agenda ({} hour days)".format(self.maxHours),
            font=("Helvetica", 20, "bold"))
        self.agenda = Agenda(self.canvas,self.width,self.height,1,1,2012)
        self.agenda.clear()
        #self.agenda.draw([0]) #draw today's agenda when initializing
        #TODO: this can be done waaaaay better
        b1 = Button(self.canvas, text="Previous Month",
         command=self.previousMonth) #initialize buttons
        b2 = Button(self.canvas, text="Next Month", command=self.nextMonth)
        b3 = Button(self.canvas, text="Add Assignment",
         command=self.addAssignment)
        b4 = Button(self.canvas, text="Add Fixed Task",
         command=self.addFixedTask)
        b5 = Button(self.canvas, text="Add Recurring Task/Class",
         command=self.addRecurringTask)
        b6 = Button(self.canvas, text="Remove Task", command=self.removeTask)
        b7 = Button(self.canvas, text="Clear All Data", command=self.clearData)
        b8 = Button(self.canvas, text="Set Work Hours",
         command=self.setMaxHours)
        b9 = Button(self.canvas, text="Toggle Schedule Optimization",
         command=self.toggleMaxDays)
        b10 = Button(self.canvas, text="Search Calendar",
         command=self.calSearch)
        b13 = Button(self.canvas, text="I've Done Work!",
         command=self.addHours)
        b14 = Button(self.canvas, text="Toggle Work Days", command=self.toggleWorkDay)
        b15 = Button(self.canvas, text="Toggle Today", command=self.toggleToday)
        calwidth = (self.cal.right + self.cal.left) / 2
        col1 = self.cal.left + 1*(calwidth / 2) - 60
        col2 = self.cal.left + 2*(calwidth / 2) - 30
        col3 = self.cal.left + 3*(calwidth / 2)
        self.canvas.create_text(col1,self.height*29./40,
            text="Tasks",font=("Helvetica", 20, "bold"))
        self.canvas.create_text(col2,self.height*29./40,
            text="Scheduling",font=("Helvetica", 20, "bold"))
        self.canvas.create_text(col3,self.height*29./40,
            text="Management",font=("Helvetica", 20, "bold"))
        self.canvas.create_window(self.width*5./40,
        self.height*1./20, window=b1) #3-6 tasks
        self.canvas.create_window(self.width*25./40,
        self.height*1./20, window=b2) #8-10 scheduling
        self.canvas.create_window(col1,self.height*29./40+30
        , window=b3) #7,11-12 To Go
        self.canvas.create_window(col1,self.height*29./40+60, window=b4)
        self.canvas.create_window(col1,self.height*29./40+90, window=b5)
        self.canvas.create_window(col1,self.height*29./40+120, window=b6)
        self.canvas.create_window(col2,self.height*29./40+30, window=b8)
        self.canvas.create_window(col2,self.height*29./40+60, window=b9)
        self.canvas.create_window(col2,self.height*29./40+90, window=b13)
        self.canvas.create_window(col2,self.height*29./40+120, window=b14)
        self.canvas.create_window(col2,self.height*29./40+150, window=b15)
        self.canvas.create_window(col3,self.height*29./40+30, window=b10)
        self.canvas.create_window(col3,self.height*29./40+120, window=b7)
        self.canvas.pack()

    def run(self):
        self.root = Tk()
        self.root.resizable(width=FALSE, height=FALSE)
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.init()
        if os.path.exists("schedule.dat"):
            self.loadData()
        self.canvas.delete(self.agendaTitle)
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,
            text="Agenda ({} hour days)".format(self.maxHours),
            font=("Helvetica", 20, "bold"))
        # set up events
        def mousePressedWrapper(event):
            self.mousePressed(event)
        def mouseMotionWrapper(event):
            self.mouseMotion(event)
        def mouseReleaseWrapper(event):
            self.mouseReleased(event)
        self.root.bind("<Button-1>", mousePressedWrapper)
        self.root.bind("<B1-Motion>", mouseMotionWrapper)
        self.root.bind("<ButtonRelease-1>", mouseReleaseWrapper)
        self.root.title("Ned's Intelligent Calendar Planner")
        self.root.mainloop()
        self.saveData()

app = CalendarPlanner(1000,700)
app.run()
