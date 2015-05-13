# Edward Williamson
# Andrew: edwillia
# Recitation: Section F

import datetime
import calendar
import tkSimpleDialog
import tkMessageBox
import os
import pickle
from Tkinter import Tk, FALSE, Canvas, Button
from graphics import gCalendar, Agenda, MEDIUMFONT, BIGFONT
from planner import Planner

SAVEFILE = "schedule.dat"

class Day(object):

    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


class Controller(object):

    def __init__(self, width=900, height=600):
        self.width = width
        self.height = height
        today = datetime.date.today()
        self.selected_day = Day(today.year, today.month, today.day)
        self.dragTask = None
        self.taskDraw = None
        self.agenda_title = None
        self.planner = Planner()
        this_month_cal = calendar.monthcalendar(self.selected_day.year, self.selected_day.month)
        weeks = len(this_month_cal)
        for week in xrange(weeks):
            for day in xrange(7):
                if this_month_cal[week][day] == self.selected_day.day:
                    self.week = week
                    self.day = day

    def getAgendaDays(self):
        today = datetime.date.today()
        days = []
        for i in xrange(len(self.planner.current_agenda)):
            days += [today + datetime.timedelta(i)]
        return days

    def clearData(self):
        check = tkMessageBox.askyesno("Are you sure?",
                                      "Are you sure you want to clear all of your data?")
        if check:
            self.planner = Planner()
            self.saveData()
            self.attempt_to_schedule()

    def saveData(self):
        data = [self.planner,self.planner.max_hours,self.maxDays,self.workDays]
        with open(SAVEFILE, "wb") as f:
            pickle.dump(data, f)

    def loadData(self):
        try:
            with open(SAVEFILE, "rb") as f:
                data = pickle.load(f)
            self.planner.tasks.today = datetime.date.today() #this shouldn't be here
            self.planner.max_hours = data[1]
            self.maxDays = data[2]
            self.workDays = data[3]
            self.attempt_to_schedule(err_msg="Couldn't load data.")
        except EOFError:
            return
        #except:
        #    tkMessageBox.showwarning("Couldn't Load Data",
        #     "The data file exists but it could not be loaded!")

    """
    def saveData(self):
        with open(SAVEFILE, "w") as f:
            data = {
                "tasks": self.planner.tasks,
                "max_hours": self.planner.max_hours,
                "max_days": self.maxDays,
                "work_days": self.workDays
            }
            f.write(json.dumps(data))

    def loadData(self):
        try:
            with open(SAVEFILE, "r") as f:
                data = json.loads(f.read())
                self.planner.tasks = data["tasks"]
                self.planner.max_hours = data["hours"]
                self.maxDays = data["max_days"]
                self.workDays = data["work_days"]
                self.createAgenda()  # update agenda
                self.selectAgenda(self.week, self.day)
                self.agenda.draw(self.selectedAgenda)
                self.cal.draw(self)
        except:
            tkMessageBox.showwarning("Couldn't Load Data",
                                     "The data file exists but it could not be loaded!")
            exit()
    """

    def drawDragDrop(self, event):
        if self.taskDraw is not None:
            self.canvas.delete(self.taskDraw)
            x = event.x
            y = event.y
            self.taskDraw = self.canvas.create_text(x, y,
                                                    text=self.dragTask[
                                                        0].description,
                                                    font=MEDIUMFONT)

    def checkIfAgenda(self, event):
        x = event.x
        y = event.y
        left = int(self.agenda.left)
        top = int(self.agenda.top)
        right = int(self.agenda.right)
        bottom = int(self.agenda.bottom)
        if left < x < right and top + 20 < y < bottom:
            index = (y - top - 20) / 20  # get index
            if len(self.selectedAgenda) > index:
                self.dragTask = self.selectedAgenda[index]
                self.taskDraw = self.canvas.create_text(x, y,
                                                        text=self.dragTask[
                                                            0].description,
                                                        font=MEDIUMFONT)

    def placeTask(self, date):
        task = self.dragTask[0]
        originaldue = task.due
        task.due = date
        if hasattr(task, "recurring") and task.recurring:
            tkMessageBox.showerror("Impossible to Schedule",
                                   "You can't reschedule a recurring task!")
            return
        if date < datetime.date.today():
            tkMessageBox.showerror("Impossible to Schedule",
                                   "You can't reschedule that task to the past!")
            return
        if date > self.planner.tasks.latest_task:
            self.planner.tasks.latest_task = date

        def failure():
            task.due = originaldue
        self.attempt_to_schedule(failure,
                                 "You can't finish that task in the given time per day!")

    def tryToPlace(self, event):
        x = event.x
        y = event.y
        left = int(self.cal.left)  # take all information from calendar
        # class, no copy-paste
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
                date = datetime.date(year, month, day)
                # self.week = row #used for new selected Agenda?
                #self.day = col
                self.placeTask(date)

    def mouseReleased(self, event):
        if self.dragTask is not None:
            self.tryToPlace(event)
            self.canvas.delete(self.taskDraw)
            self.dragTask = None
            self.taskDraw = None

    def mouseMotion(self, event):
        self.drawDragDrop(event)

    def mousePressed(self, event):
        self.checkIfAgenda(event)
        if self.dragTask is not None:
            return
        left = int(self.cal.left)  # take all information from calendar class,
        # no copy-paste
        top = int(self.cal.top)
        #right = int(self.cal.right)
        #bottom = int(self.cal.bottom)
        cellWidth = int(self.cal.cellWidth)
        cellHeight = int(self.cal.cellHeight)
        col = (event.x - left) / cellWidth
        row = (event.y - top) / cellHeight
        selectedAgenda = self.selectAgenda(row, col)
        if selectedAgenda is not None:
            self.agenda.draw(selectedAgenda)
            self.week = row
            self.day = col
        elif row >= 0 and col >= 0 and row < self.cal.weeks and col < 7:
            if self.cal.monthArray[row][col] != 0:
                self.agenda.clear()
                self.week = row
                self.day = col
            elif row > 0:
                self.nextMonth()
                row = 0
                self.week = row
                self.day = col
                selectedAgenda = self.selectAgenda(row, col)
                if selectedAgenda is not None:
                    self.agenda.draw(selectedAgenda)
                else:
                    self.agenda.clear()
            elif row == 0:
                self.previousMonth()
                row = len(self.cal.monthArray) - 1
                self.week = row
                self.day = col
                selectedAgenda = self.selectAgenda(row, col)
                if selectedAgenda is not None:
                    self.agenda.draw(selectedAgenda)
                else:
                    self.agenda.clear()

    def selectAgenda(self, row, col):
        # only run this after creating an agenda first
        # check for self.agenda's existence/initialization
        if row >= 0 and col >= 0 and row < self.cal.weeks and col < 7 and self.cal.monthArray[row][col] != 0:
            selectedDay = datetime.date(self.cal.year, self.cal.month,
                                        self.cal.monthArray[row][col])
            self.cal.selectedDay = selectedDay
            self.cal.clear()
            self.cal.draw(self)
            selectedDayDistance = (selectedDay - datetime.date.today()).days
            # if selectedDayDistance > 0 and selectedDayDistance < len(agenda):
            selectedAgenda = None
            if selectedDayDistance >= 0 and selectedDayDistance < len(self.planner.current_agenda):
                selectedAgenda = self.planner.current_agenda[selectedDayDistance]
                self.selectedAgenda = selectedAgenda
            return selectedAgenda

    def getAgenda(self, row, col):
        if row >= 0 and col >= 0 and row < self.cal.weeks and col < 7 and\
                self.cal.monthArray[row][col] != 0:
            selectedDay = datetime.date(self.cal.year, self.cal.month,
                                        self.cal.monthArray[row][col])
            selectedDayDistance = (selectedDay - datetime.date.today()).days
            selectedAgenda = None
            if selectedDayDistance >= 0 and selectedDayDistance < len(self.planner.current_agenda):
                selectedAgenda = self.planner.current_agenda[selectedDayDistance]
            return selectedAgenda

    def update_agenda_title(self):
        self.canvas.delete(self.agenda_title)
        self.agenda_title = self.canvas.create_text(self.width * 17. / 20,
                                                    self.height * 1. / 20,
                                                    text="Agenda ({} hour days)".format(
                                                        self.planner.max_hours),
                                                    font=BIGFONT)

    def setMaxHours(self):
        original = self.planner.max_hours
        maxHours = tkSimpleDialog.askinteger("Hour Set",
                                             "How many hours will you work per day? Currently {} hours.".format(self.planner.max_hours))
        if maxHours is None:
            return
        if maxHours > 24 or maxHours < 0:
            tkMessageBox.showerror("Invalid Input",
                                   "Please enter an integer 0-24.")
            return
        self.planner.max_hours = maxHours

        def failure():
            self.planner.max_hours = original
        self.attempt_to_schedule(failure,
                                 "You can't finish your tasks in the given work hours per day!")
        self.update_agenda_title()

    def toggleMaxDays(self):
        self.maxDays = not self.maxDays

        def failure():
            self.maxDays = not self.maxDays
        self.attempt_to_schedule(failure,
                                 "You can't finish your tasks if you toggle your schedule optimization!")

    def addAssignment(self):  # graphical implementation
        description = tkSimpleDialog.askstring("Task Adder",
                                               "What is the name of your task?")
        if description is None:
            return
        hours = tkSimpleDialog.askinteger("Task Adder",
                                          "How many hours will it take to complete?")
        if hours is None:
            return
        dueString = tkSimpleDialog.askstring("Task Adder",
                                             "When is it due? Enter MM/DD or MM/DD/YYYY")
        if dueString is None:
            return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year, month, day)
        except:
            tkMessageBox.showerror("Date Entry Error",
                                   "Invalid Date Entered!")
        if due < datetime.date.today():
            tkMessageBox.showerror("Date Entry Error",
                                   "You can't add something in the past!")
            return
        hoursDone = 0  # is this assumption safe?
        self.planner.add_task(description, hours, hoursDone, due)

        def failure():
            self.planner.remove_task(description)
        self.attempt_to_schedule(failure,
                                 "You can't finish that task in the given time per day!")

    def addFixedTask(self):  # same, but with a fixed task
        description = tkSimpleDialog.askstring("Task Adder",
                                               "What is the name of your task?")
        if description is None:
            return
        dueString = tkSimpleDialog.askstring("Task Adder",
                                             "What day is it? Enter MM/DD or MM/DD/YYYY")
        if dueString is None:
            return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year, month, day)
        except:
            tkMessageBox.showerror("Date Entry Error",
                                   "Invalid Date Entered!")
        if due < datetime.date.today():
            tkMessageBox.showerror("Date Entry Error",
                                   "You can't add something in the past!")
            return
        timeString = tkSimpleDialog.askstring("Task Adder",
                                              "What time is it? Enter HH-HH or HH:MM-HH:MM")
        # print timeString
        if timeString is None:
            return
        if len(timeString) == 5 and timeString[2] == "-":
            startTime = int(timeString[0:2])
            endTime = int(timeString[3:5])
            if (startTime < 0 or endTime < 0 or startTime > 24 or
                    endTime > 24 or startTime > endTime):
                tkMessageBox.showerror("Time Entry Error",
                                       "Invalid Time Range Entered!")
                return
            startTime = datetime.datetime(due.year, due.month,
                                          due.day, int(timeString[0:2]))  # fix this for efficiency?
            endTime = datetime.datetime(due.year, due.month,
                                        due.day, int(timeString[3:5]))
        elif len(timeString) == 11 and timeString[2] == ":" and\
                timeString[5] == "-" and timeString[8] == ":":
            startHour = int(timeString[0:2])
            startMinutes = int(timeString[3:5])
            endHour = int(timeString[6:8])
            endMinutes = int(timeString[9:12])
            try:
                startTime = datetime.datetime(due.year, due.month,
                                              due.day, startHour, startMinutes)
                endTime = datetime.datetime(due.year, due.month,
                                            due.day, endHour, endMinutes)
            except:
                tkMessageBox.showerror("Time Entry Error",
                                       "Invalid Time Range Entered!")
                return
        else:
            tkMessageBox.showerror("Time Entry Error",
                                   "Invalid Time Range Entered!")
            return
        self.planner.add_fixed_task(description, startTime, endTime)

        def failure():
            self.planner.tasks.remove(description)
        self.attempt_to_schedule(failure,
                                 "You can't finish that task in the given time per day!")

    def addRecurringTask(self):
        description = tkSimpleDialog.askstring("Task Adder",
                                               "What is the name of your task?")
        if description is None:
            return
        recurringDays = tkSimpleDialog.askstring(
            "Recurring Days", "Enter comma separated days: e.g. \"0,1,2,3,4,5,6\"")
        if recurringDays is None:
            return
        recurring = []
        for i in xrange(0, len(recurringDays), 2):
            recurring += [int(recurringDays[i])]
        if len(recurring) == 0 or min(recurring) < 0 or max(recurring) > 6:
            tkMessageBox.showerror("Invalid Entry",
                                   "Invalid Day List!")
            return
        dueString = tkSimpleDialog.askstring("Task Adder",
                                             "Repeat until which day? Enter MM/DD or MM/DD/YYYY")
        if dueString is None:
            return
        month = int(dueString[0:2])
        day = int(dueString[3:5])
        if len(dueString) == 10:
            year = int(dueString[6:10])
        else:
            year = datetime.date.today().year
        try:
            due = datetime.date(year, month, day)
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
        # print timeString
        if timeString is None:
            return
        if len(timeString) == 5 and timeString[2] == "-":
            startTime = int(timeString[0:2])
            endTime = int(timeString[3:5])
            if (startTime < 0 or endTime < 0 or startTime > 24 or endTime > 24 or startTime > endTime):
                tkMessageBox.showerror("Time Entry Error",
                                       "Invalid Time Range Entered!")
                return
            startTime = datetime.datetime(due.year, due.month, due.day,
                                          int(timeString[0:2]))  # fix this for efficiency?
            endTime = datetime.datetime(due.year, due.month, due.day,
                                        int(timeString[3:5]))
        elif len(timeString) == 11 and timeString[2] == ":" and timeString[5] == "-" and timeString[8] == ":":
            startHour = int(timeString[0:2])
            startMinutes = int(timeString[3:5])
            endHour = int(timeString[6:8])
            endMinutes = int(timeString[9:12])
            try:
                startTime = datetime.datetime(due.year, due.month, due.day,
                                              startHour, startMinutes)
                endTime = datetime.datetime(due.year, due.month, due.day,
                                            endHour, endMinutes)
            except:
                tkMessageBox.showerror("Time Entry Error",
                                       "Invalid Time Range Entered!")
                return
        else:
            tkMessageBox.showerror("Time Entry Error",
                                   "Invalid Time Range Entered!")
            return
        
        self.planner.add_fixed_task(description, startTime, endTime, recurring)

        def failure():
            self.planner.tasks.remove(description)
        self.attempt_to_schedule(failure,
                                 "You can't finish that task in the given time per day!")

    def removeTask(self):
        description = tkSimpleDialog.askstring("Task Remover",
                                               "What is the name of your task?")
        if description is None:
            return
        removed = self.planner.tasks.remove(description)
        if removed is None:
            tkMessageBox.showinfo("You Should Know...",
                                  "There was no task found matching that description!")
            return
        self.attempt_to_schedule()

    def add_hours(self):
        description = tkSimpleDialog.askstring("Task Completer",
                                               "What is the name of your task?")
        if description is None:
            return
        hours = tkSimpleDialog.askinteger("Task Completer",
                                          "How many hours did you complete?")
        if hours is None:
            return
        added = self.planner.tasks.add_hours(description, hours)
        if added is None:
            tkMessageBox.showinfo("You Should Know...",
                                  "There was no task found matching that description!")
            return
        self.attempt_to_schedule()

    def redraw_calendar(self):
        self.cal.clear()
        self.cal = gCalendar(self.canvas, self.width, self.height,
                             self.selected_day.month, self.selected_day.year)
        self.cal.draw(self)

    def previousMonth(self):
        if self.selected_day.month > 1:
            self.selected_day.month -= 1
        else:
            self.selected_day.month = 12
            self.selected_day.year -= 1
        self.redraw_calendar()

    def nextMonth(self):
        if self.selected_day.month < 12:
            self.selected_day.month += 1
        else:
            self.selected_day.month = 1
            self.selected_day.year += 1
        self.redraw_calendar()

    def toggleDayHelper(self, dayint):
        if dayint in self.workDays:
            self.workDays.remove(dayint)
        else:
            self.workDays.append(dayint)

    # call failure if we can't schedule
    def attempt_to_schedule(self, failure=None, err_msg="Unknown scheduling error."):
        assert self.planner.current_agenda is not None  # already working
        if failure is None:
            def failure():
                pass
        agenda = self.planner.create_agenda_safe()
        if agenda is None:
            tkMessageBox.showerror("Impossible to Schedule", err_msg)
            failure()
            return
        self.planner.current_agenda = agenda
        self.selectAgenda(self.week, self.day)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def toggleWorkDay(self):
        dayint = tkSimpleDialog.askinteger("Workday Toggler",
                                           "Which day do you want to toggle?")
        if dayint is None:
            return
        if not (0 <= dayint <= 6):
            tkMessageBox.showerror("Invalid Input", "Please enter a day 0-6.")
            return
        self.toggleDayHelper(dayint)

        def failure():
            self.toggleDayHelper(dayint)
        self.attempt_to_schedule(failure,
                                 "You can't finish your tasks if you toggle that day!")

    def toggle_today(self):
        self.work_today = not self.work_today

        def failure():
            self.work_today = not self.work_today
        self.attempt_to_schedule(failure,
                                 "You can't finish your tasks if you toggle that day!")

    def init(self):
        # draw calendar label
        self.cal = gCalendar(self.canvas, self.width, self.height,
                             self.selected_day.month, self.selected_day.year)
        self.planner.createAgenda()
        self.cal.draw(self)
        # draw agenda label
        self.update_agenda_title()
        self.agenda = Agenda(self.canvas, self.width, self.height, 1, 1, 2012)
        self.agenda.clear()
        # self.agenda.draw([0]) #draw today's agenda when initializing
        # TODO: this can be done waaaaay better
        b1 = Button(self.canvas, text="Previous Month",
                    command=self.previousMonth)  # initialize buttons
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
        b13 = Button(self.canvas, text="I've Done Work!",
                     command=self.add_hours)
        b14 = Button(
            self.canvas, text="Toggle Work Days", command=self.toggleWorkDay)
        b15 = Button(
            self.canvas, text="Toggle Today", command=self.toggle_today)
        calwidth = (self.cal.right + self.cal.left) / 2
        col1 = self.cal.left + 1 * (calwidth / 2) - 60
        col2 = self.cal.left + 2 * (calwidth / 2) - 30
        col3 = self.cal.left + 3 * (calwidth / 2)
        self.canvas.create_text(col1, self.height * 29. / 40,
                                text="Tasks", font=BIGFONT)
        self.canvas.create_text(col2, self.height * 29. / 40,
                                text="Scheduling", font=BIGFONT)
        self.canvas.create_text(col3, self.height * 29. / 40,
                                text="Management", font=BIGFONT)
        self.canvas.create_window(self.width * 5. / 40,
                                  self.height * 1. / 20, window=b1)  # 3-6 tasks
        self.canvas.create_window(self.width * 25. / 40,
                                  self.height * 1. / 20, window=b2)  # 8-10 scheduling
        self.canvas.create_window(
            col1, self.height * 29. / 40 + 30, window=b3)  # 7,11-12 To Go
        self.canvas.create_window(col1, self.height * 29. / 40 + 60, window=b4)
        self.canvas.create_window(col1, self.height * 29. / 40 + 90, window=b5)
        self.canvas.create_window(
            col1, self.height * 29. / 40 + 120, window=b6)
        self.canvas.create_window(col2, self.height * 29. / 40 + 30, window=b8)
        self.canvas.create_window(col2, self.height * 29. / 40 + 60, window=b9)
        self.canvas.create_window(
            col2, self.height * 29. / 40 + 90, window=b13)
        self.canvas.create_window(
            col2, self.height * 29. / 40 + 120, window=b14)
        self.canvas.create_window(
            col2, self.height * 29. / 40 + 150, window=b15)
        self.canvas.create_window(
            col3, self.height * 29. / 40 + 120, window=b7)
        self.canvas.pack()

    def run(self):
        self.root = Tk()
        self.root.resizable(width=FALSE, height=FALSE)
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        self.init()
        if os.path.exists(SAVEFILE):
            self.loadData()
        self.canvas.delete(self.agenda_title)
        self.update_agenda_title()

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

if __name__ == "__main__":
    app = Controller(1000, 700)
    app.run()
