#Edward Williamson
#Andrew: edwillia
#Recitation: Section F

from Tkinter import *
import datetime
import calendar
import math
import tkSimpleDialog
import tkMessageBox
import tkFileDialog
import pickle
import os
import tempfile
import urllib
import urllib2
#import pdb
from icalendar import Calendar, Event

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
    def __init__(self,description,startTime,endTime,recurring=False):
        self.startTime = startTime #this should be dealt with using time
                                   #objects -- done in make iCal as needed
        self.endTime = endTime
        new = " " + str(startTime.hour) + ":" + "%02d" % startTime.minute \
        + "-" + str(endTime.hour) + ":" +  "%02d" % endTime.minute
        description += new
        hours = ((endTime - startTime).seconds)/3600 #use actual timedelta 
                                                     #to find hours
        due = startTime.date()
        hoursDone = 0 #can't have hours completed in advance on a fixed event
        self.recurring = recurring
        super(FixedTask, self).__init__(description,hours,hoursDone,due)

    #def __str__(self): #used to make ical
        #startHour = self.startTime.hour
        #if startHour < 10:
        #    startHour = "0" + str(startHour)
        #else:
        #    startHour = str(startHour)
        #return str(item.due.year) + str(item.due.month) + str(item.due.day)
        #\+ "T" + str(startHour) +"0000" #last 4 are minutes and seconds

    def __repr__(self):
        return str(self.description) + ", Hours Left: " + str(self.hours \
            - self.hoursDone) + ", Days Left: " + str((self.due - \
                datetime.date.today()).days)

class TaskList(object):
    def __init__(self):
        self.fixed = [] #fixed tasks
        self.assignments = [] #assignments with due dates
        self.latestTask = datetime.date.today() #initialize last task date to
                                                #today
        self.descriptionList = []
        #due dates written as month,day,year
        #calculate distance between two days

    def add(self,task):
        #print self.descriptionList
        descriptionList = []
        #print task
        #print task.description,task.due
        for check in self.fixed:
            descriptionList += check.description
        for check in self.assignments:
            descriptionList += check.description
        if task.description in descriptionList: #make sure we don't have
                                                 #a duplicate assignment name
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
            #[:len(description)] allows us to quickly remove tasks by first
            #few letters
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
            #[:len(description)] allows us to quickly remove tasks by first
            #few letters
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

    def calcAgenda(self,maxHours,maxDays=False,workDays=[0,1,2,3,4,5,6],workToday=True): #maxDays maximizes work in
                             #given time at expense of easy/time efficiency
        #print (self.latestTask - startDay).days
        startDay = datetime.date.today()
        #print self.latestTask
        if self.latestTask == startDay:
            planTasks = [[]]
            planHours = [0]
        else:
            planTasks = [[] for day in xrange((self.latestTask -\
             startDay).days+1)] #[]*days until last assigned task
            planHours = [0]*((self.latestTask - startDay).days+1)
            self.assignments = sorted(self.assignments,
             key=lambda task: task.due) # sort assignments by due date --
                                        # earliest completed first
            #self.fixed = sorted(self.fixed, key=lambda task: task.due)
            # ^ irrelevant for fixed tasks
        for task in self.fixed:
            daysAway = (task.due - startDay).days
            #index is days away from today
            if task.recurring == True:
                for i in xrange(daysAway+1):
                    due = startDay + datetime.timedelta(i)
                    startHour = datetime.time(task.startTime.hour)
                    endHour = datetime.time(task.endTime.hour)
                    startTime = datetime.datetime.combine(due,startHour)
                    endTime = datetime.datetime.combine(due,endHour)
                    #new = " " + str(startTime.hour) + ":" + "%02d" %
                    #startTime.minute + "-" + str(endTime.hour) + ":" + 
                    #\"%02d" % endTime.minute
                    choplength = len(str(task.startTime.hour) + \
                    str(task.endTime.hour)) + 8 #4 extra chars #find length
                                                #to chop before recalling
                                                #constructor
                    newtask = FixedTask(task.description[:-choplength],
                        startTime,endTime,True)
                    if newtask.hours + planHours[i] <= maxHours:
                        planHours[i] += newtask.hours
                        planTasks[i] += [(newtask,newtask.hours)] #add tuple
                        #of task and hours allotted for that day
                    else:
                        return None
            else:
                if task.hours + planHours[daysAway] <= maxHours:
                    planHours[daysAway] += task.hours
                    planTasks[daysAway] += [(task,task.hours)] #add tuple of
                    #task and hours allotted for that day
                else:
                    return None

                #workdays date.weekday()

        for i in xrange(len(self.assignments)): #cycle by index so we can
                                      #check if we're on the last element
            task = self.assignments[i]
            if task.due < datetime.date.today(): continue
            daysAway = (task.due - startDay).days #- 1 #index is days #-1 to finish a day in advance
                                                             #away from today
            hoursDone = task.hoursDone
            for day in xrange(daysAway+1):
                hoursLeft = task.hours - hoursDone
                if hoursLeft == 0:
                    continue
                if day == 0 and workToday == False: continue
                dayOfWeek = datetime.date.weekday(datetime.date.today()+datetime.timedelta(day))
                if dayOfWeek not in workDays:
                    if day == daysAway and hoursLeft != 0:
                        return None
                    else:
                        continue
                daysLeft = (daysAway - day)
                if daysLeft == 0: return None
                if daysLeft == 1:
                    #print "last chance",
                    hoursPerDay = hoursLeft
                elif (i == (len(self.assignments) - 1) and maxDays == True):
                    #print "maxed",
                    hoursPerDay = min(maxHours - planHours[day],hoursLeft)
                else:
                    #print "divided " + str(hoursLeft) + " " + str(daysLeft)#str(maxHours - planHours[day]) + " " + str(int(math.ceil(float(hoursLeft)/daysLeft)))
                    hoursPerDay = min(maxHours - planHours[day],int(math.ceil(float(hoursLeft)/daysLeft)))
                #print task.description,task.hours,hoursDone,hoursLeft,hoursPerDay
                if hoursPerDay == 0: continue
                if hoursPerDay + planHours[day] <= maxHours:
                    hoursDone += hoursPerDay
                    planHours[day] += hoursPerDay
                    planTasks[day] += [(task,hoursPerDay)]
                    #add tuple of task and hours allotted for that day
                elif day == daysAway:
                    # if there are no days left, we can't
                    # complete this assignment
                    return None

        #print planHours
        return planTasks

class GraphicsElement(object): #basic graphical element
    def __init__(self,canvas,width,height):
        self.canvas = canvas #element must know how to access its canvas
        self.width = width #element must know its canvas
                           #size to position itself
        self.height = height
        self.elements = [] #keep track of canvas elements to clear

    def add(self,element): #add elements to a list so we have a list
                           #associated with each GraphicsElement
        self.elements += [element]

    def clear(self): #use the list of elements for this GraphicsElement to
                     #clear only this object from the canvas
        for element in self.elements: #most basic
            self.canvas.delete(element)

    def draw(self): pass #is this necessary?

class Agenda(GraphicsElement):
    def __init__(self,canvas,width,height,day,month,year):
        self.day = day
        self.month = month
        self.year = year
        self.left = (15./20)*width
        self.right = (19./20)*width
        self.top = (2./20)*height
        self.bottom = (19./20)*height
        super(Agenda, self).__init__(canvas,width,height)
        self.clear()

    def clear(self):
        super(Agenda, self).clear()
        self.add(self.canvas.create_rectangle(self.left,self.top,
        self.right,self.bottom)) #temp until we put the actual calendar
        self.add(self.canvas.create_text(self.left,self.top,
            text="Description",font=("Calibri", 10, "bold"),anchor=NW))
        self.add(self.canvas.create_text(self.left + ((self.right - \
            self.left) / 2),self.top,text="Hours",font=("Calibri", 10,
             "bold"),anchor=N))
        self.add(self.canvas.create_text(self.right,self.top,text="Due Date",
            font=("Calibri", 10, "bold"),anchor=NE))

    def draw(self,selectedAgenda):
        #loop to create rectangles
        #loop to create labels for calendar
        self.clear()
        for i in xrange(len(selectedAgenda)):
            item = selectedAgenda[i]
            tempDescription = item[0].description
            if len(tempDescription) > 15:
                tempDescription = tempDescription[:14] + "..."
            newTop = self.top + 20*(i+1)
            if newTop + 40 > self.bottom:
                self.add(self.canvas.create_text(self.left,newTop,
                    text="......",font=("Calibri", 10,),anchor=NW))
                break
            self.add(self.canvas.create_text(self.left,newTop,
                text=tempDescription,font=("Calibri", 10,),anchor=NW))
            self.add(self.canvas.create_text(self.left +\
             ((self.right - self.left) / 2),newTop,text=item[1],
             font=("Calibri", 10,),anchor=N))
            self.add(self.canvas.create_text(self.right,newTop,
                text=item[0].due,font=("Calibri", 10,),anchor=NE))

class gCalendar(GraphicsElement): #draw calendar with given specs
    def __init__(self,canvas,width,height,month,year):
        self.month = month
        self.year = year
        self.currentDay = datetime.date.today()
        self.selectedDay = self.currentDay
        self.left = (1./20)*width
        self.right = (14./20)*width
        self.top = (2./20)*height
        self.bottom = (14./20)*height
        self.monthArray = calendar.monthcalendar(self.year,self.month)
        self.weeks = len(self.monthArray)
        self.cellWidth = (self.right - self.left) / 7
        self.cellHeight = (self.bottom - self.top) / self.weeks
        self.months = ["January","February","March","April","May","June",
        "July","August","September","October","November","December"]
        self.days = ["Monday","Tuesday","Wednesday","Thursday","Friday",
        "Saturday","Sunday"]
        super(gCalendar, self).__init__(canvas,width,height)

    def widthHeight(self,width,height):
        self.width = width
        self.height = height

    def calendarTable(self,month,year):
        pass
        #use calendar to get 2d view, parse into 2d list

    def drawCell(self,left,top,right,bottom):
        pass #draw calendar rectangle with label

    def dragMouse(self): #necessary?
        for i in xrange(len(selectedAgenda)):
            item = selectedAgenda[i]
            tempDescription = item[0].description
            if len(tempDescription) > 15:
                tempDescription = tempDescription[:11] + "..."
            newTop = self.top + 20*(i+1)
            self.add(self.canvas.create_text(self.left,newTop,
                text=tempDescription,font=("Calibri", 10,),anchor=NW))
            self.add(self.canvas.create_text(self.left + ((self.right - \
                self.left) / 2),newTop,text=item[1],font=("Calibri", 10,),
            anchor=N))
            self.add(self.canvas.create_text(self.right,newTop,
                text=item[0].due,font=("Calibri", 10,),anchor=NE))

    def draw(self,planner,calSearch=None):
        self.clear()
        self.add(self.canvas.create_text(self.width*15./40,
            self.height*1./20,text=self.months[self.month-1] + " " + \
            str(self.year),font=("Calibri", 26, "bold")))
        for row in xrange(self.weeks):
            for col in xrange(7):
                newLeft = self.left+self.cellWidth*col
                newRight = newLeft + self.cellWidth
                newTop = self.top+self.cellHeight*row
                newBottom = newTop+self.cellHeight
                if row == 0: #create day of week labels on first pass
                    self.add(self.canvas.create_text((newLeft+newRight)/2,
                        self.height*7./80,text=self.days[col],
                        font=("Calibri", 12, "bold")))
                if self.monthArray[row][col] != 0:
                    selectedAgenda = planner.getAgenda(row,col)
                    self.add(self.canvas.create_rectangle(newLeft,newTop,
                    newRight,newBottom)) #day box
                    if self.monthArray[row][col] == self.selectedDay.day and \
                    self.month == self.selectedDay.month and self.year == \
                    self.selectedDay.year:
                        self.add(self.canvas.create_rectangle(newLeft,newTop,
                        newRight,newBottom,fill="yellow")) #selected box
                    #if self.monthArray[row][col] == self.selectedDay.day and\
                    #self.month == self.selectedDay.month and\
                    #self.year == self.selectedDay.year:
                    if selectedAgenda != None and len(selectedAgenda) > 0 \
                    and calSearch != None:
                        for task in selectedAgenda:
                            if task[0].description[:len(calSearch)] ==\
                             calSearch:
                                self.add(self.canvas.create_rectangle(newLeft,
                                newTop,newRight,newBottom,fill="orange"))
                                #search found! paint box
                                self.foundTask = True
                                continue
                    if self.monthArray[row][col] == self.currentDay.day\
                     and self.month == self.currentDay.month and self.year\
                      == self.currentDay.year:
                        self.add(self.canvas.create_rectangle(newLeft,newTop,
                        newRight,newBottom,fill="green")) #today box
                    self.add(self.canvas.create_text(newLeft+2,newTop+1,
                        anchor=NW,text=self.monthArray[row][col],
                        font=("Calibri", 12, "bold")))
                    if selectedAgenda != None:
                        for i in xrange(len(selectedAgenda)):
                            item = selectedAgenda[i]
                            newTop2 = newTop + 15*(i+1)
                            tempDescription = item[0].description
                            if newTop2 + 30 > newBottom:
                                self.add(self.canvas.create_text(newLeft,
                                    newTop2,text="......",font=("Calibri",
                                     10,),anchor=NW))
                                break
                            if len(tempDescription) > 15:
                                tempDescription = tempDescription[:11] +\
                                 "..." + tempDescription[-3:]
                            self.add(self.canvas.create_text(newLeft,newTop2,
                                text=tempDescription,font=("Calibri", 10,),
                                anchor=NW))
                else:
                    self.add(self.canvas.create_rectangle(newLeft,newTop,
                    newRight,newBottom,fill="gray")) #day box

class CalendarPlanner(object):
    def __init__(self,width=900,height=600,selectedDayDistance=0,
        maxHours=8,maxDays=False):
        self.width = width
        self.height = height
        self.month = datetime.date.today().month #current month
        self.year = datetime.date.today().year #current year
        self.day = datetime.date.today().day #current days
        self.tasks = TaskList()
        self.selectedDayDistance = selectedDayDistance
        self.maxHours = maxHours
        self.maxDays = maxDays
        calendarPlanner = calendar.monthcalendar(self.year,self.month)
        self.userNumber = None
        self.carrier = None
        self.dragTask = None
        self.taskDraw = None
        self.workDays = [0,1,2,3,4,5,6]
        self.workToday = True
        for row in xrange(len(calendarPlanner)):
            for col in xrange(7):
                if calendarPlanner[row][col] == self.day:
                    self.row = row
                    self.col = col

    def getAgendaDays(self):
        today = datetime.date.today()
        days = []
        for i in xrange(len(self.agendaCalc)):
            days += [today+datetime.timedelta(i)]
        return days

    def makeiCal(self):
        #myFormats = [('iCalendar File','*.ics')] #irrelevant on mac
        fileName = tkFileDialog.asksaveasfilename(parent=self.root,
            initialfile="mySchedule.ics",defaultextension=".ics",
            title="Save the iCalendar file...")
        if fileName == None or len(fileName) < 1: return
        days = self.getAgendaDays()
        ical = Calendar()
        for i in xrange(len(self.agendaCalc)):
            dayAgenda = self.agendaCalc[i]
            for item in dayAgenda:
                event = Event()
                #print item
                event.add('summary', item[0].description + " - " + \
                str(item[1]) + " hours") #item[0] is task, item[1] is
                                         #hours for that day
                if isinstance(item[0], FixedTask):
                    #print item[0].startTime
                    #start = datetime.datetime.combine(days[i],
                        #datetime.time(item[0].startTime))
                    #end = datetime.datetime.combine(days[i],
                        #datetime.time(item[0].endTime))
                    #print item[0] # fix recurring ical #done
                    event.add('dtstart',item[0].startTime)
                    event.add('dtend',item[0].endTime)
                else:
                    event.add('dtstart', days[i]) #datetime(2005,4,4,8,0,0,
                                                  #tzinfo=pytz.utc)
                ical.add_component(event)
            f = open(fileName, 'wb') #these 3 lines adapted from
                                     #package documentation
            f.write(ical.to_ical())
            f.close()
            #ical['dtstart'] = str(item) #heavy lifting done in __str__
            #methods of Task() and FixedTask() classes #these have been
            #replaced with better code making use of library functions
            #ical['summary'] = item[0].description + " - " + str(item[1])\
            # + " hours" #item[0] is task, item[1] is hours for that day

    def getNumber(self):
        self.userNumber = None
        number = tkSimpleDialog.askstring("Phone Number",
         "Please enter your phone number.")
        if number == None: return
        self.userNumber = number

    def getCarrier(self):
        self.carrier = None
        carrier = tkSimpleDialog.askstring("Cell Carrier",
         "Enter AT&T, Verizon, T-Mobile, or Sprint")
        if carrier == None: return
        carriers = ["AT&T","Verizon","T-Mobile","Sprint"]
        if carrier in carriers:
            self.carrier = carrier
        else:
            tkMessageBox.showerror("Carrier Not Found",
             "That carrier isn't available.")

    def sendText(self): #form submission code adapted from
    #http://null-byte.wonderhowto.com/how-to/send-sms-messages-with-python-\
    #0132938/, modified to automatically use user data and store the number
    #for reuse between saves within this class
        if len(self.selectedAgenda) < 1:
            tkMessageBox.showerror("No Agenda",
             "There is no agenda to send on the selected day!")
            return
        check = False
        if self.userNumber != None and self.carrier != None:
            check = tkMessageBox.askyesno("Phone number already saved.",
             "Do you want to use the number %s with carrier %s?" %\
              (self.userNumber,self.carrier))
            if check == False:
                self.getNumber()
                if self.userNumber == None: return
                self.getCarrier()
                if self.carrier == None: return
        else: #fix logic here?
            self.getNumber()
            if self.userNumber == None: return
            self.getCarrier()
            if self.carrier == None: return
        if self.carrier == None:
            tkMessageBox.showerror("Carrier Not Found",
             "There is no assigned carrier.")
            return
        self.saveData()
        #enter user provider manually AT&T/Verizon/Sprint/T-Mobile
        message = " "
        for item in self.selectedAgenda:
            message += "Do " + item[0].description
            if item[1] == 1:
                message += " for " + str(item[1]) + " hour. "
            else:
                message += " for " + str(item[1]) + " hours. "
        message = message[:-1] #remove extra space (compulsive, I know.)
        prov = ''
        url = 'http://www.onlinetextmessage.com/send.php'
        provider = self.carrier
        if self.carrier == "Sprint":
            prov = '175'
        if self.carrier == "T-Mobile":
            prov = '182'
        if self.carrier == "Verizon":
            prov = '203'
        if self.carrier == "AT&T":
            prov = '41'
        #print prov
        if prov == 0:
            tkMessageBox.showerror("Carrier Not Found",
             "There is no assigned carrier.")
        values = {'code' : '',
                  'number' : self.userNumber,
                  'from' : 'nedscalendarplanner@gmail.com',
                  'remember' : 'n',
                  'subject' : 'Your Requested Schedule',
                  'carrier' : prov,
                  'quicktext' : '',
                  'message' : message,
                  's' : 'Send Message'}
        data = urllib.urlencode(values)  ##text sender
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()

    def calSearch(self):
        #prompt user for name of task, all tasks with matching initial chars
        #are highlighted
        calSearch = "ECE" #temp
        self.cal.foundTask = False
        calSearch = tkSimpleDialog.askstring("Task Finder",
         "What is the name of your task?")
        if calSearch == None: return
        self.cal.draw(self,calSearch)
        if self.cal.foundTask == False:
            tkMessageBox.showinfo("Task Not Found",
             "The task you described is not present in this month.")

    def clearData(self):
        check = tkMessageBox.askyesno("Are you sure?",
         "Are you sure you want to clear all of your data?")
        if check == True:
            self.tasks = TaskList() #reinitialize
            self.saveData()
            self.createAgenda() #update agenda
            #if self.agendaCalc == None:
            #    tkMessageBox.showerror("Impossible to Schedule",
                    #"You can't finish that task in the given time per day!")
            #    self.tasks.remove(task.description)
            #    self.createAgenda()
            #    #return
            self.selectAgenda(self.row,self.col)
            self.agenda.draw(self.selectedAgenda)
            self.cal.draw(self)
        #with open("cal.pkl","w"): #from EFFbot's website on the "with"
        #statement #http://effbot.org/zone/python-with-statement.htm
        #pass #this can be done other ways, but I like this efficient
        #implementation because it ensures that the file is closed

    def saveData(self):
        data = [self.tasks,self.maxHours,self.maxDays,self.userNumber,
        self.carrier,self.workDays]
        pickle.dump( data, open( "cal.pkl", "wb" ) )

    def loadData(self):
        try:
            data = pickle.load( open( "cal.pkl", "rb" ) )
            self.tasks = data[0]
            self.maxHours = data[1]
            self.maxDays = data[2]
            self.userNumber = data[3]
            self.carrier = data[4]
            self.workDays = data[5]
            self.createAgenda() #update agenda
            #if self.agendaCalc == None:
            #    tkMessageBox.showerror("Impossible to Schedule",
                    #"You can't finish that task in the given time per day!")
            #    self.tasks.remove(task.description)
            #    self.createAgenda()
            #    #return
            self.selectAgenda(self.row,self.col)
            self.agenda.draw(self.selectedAgenda)
            self.cal.draw(self)
        except:
            tkMessageBox.showwarning("Couldn't Load Data",
             "The data file exists but it could not be loaded!")

    def createAgenda(self):
        self.agendaCalc = self.tasks.calcAgenda(self.maxHours,self.maxDays,self.workDays,self.workToday)

    def drawDragDrop(self,event):
        if self.taskDraw != None:
            self.canvas.delete(self.taskDraw)
            x = event.x
            y = event.y
            self.taskDraw = self.canvas.create_text(x,y,
                text=self.dragTask[0].description,
                font=("Calibri", 18, "bold"))
            pass #use this to draw the thing under the mouse if
                 #mousePressed is true and we have an element

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
                    font=("Calibri", 18, "bold"))

    def placeTask(self,date):
        task = self.dragTask[0]
        originaldue = task.due
        task.due = date
        if hasattr(task,"recurring"):
            if task.recurring == True:
                tkMessageBox.showerror("Impossible to Schedule",
                 "You can't reschedule a recurring task!")
                return
        if date < datetime.date.today():
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't reschedule that task to the past!")
            return
        if date > self.tasks.latestTask:
            self.tasks.latestTask = date
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish that task in the given time per day!")
            task.due = originaldue
            self.createAgenda()
            #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def tryToPlace(self,event):
        x = event.x
        y = event.y
        left = int(self.cal.left) #take all information from calendar
                                  #class, no copy-paste
        top = int(self.cal.top)
        right = int(self.cal.right)
        bottom = int(self.cal.bottom)
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
        if self.dragTask != None:
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
        if self.dragTask != None:
            return
        left = int(self.cal.left) #take all information from calendar class,
                                  #no copy-paste
        top = int(self.cal.top)
        right = int(self.cal.right)
        bottom = int(self.cal.bottom)
        cellWidth = int(self.cal.cellWidth)
        cellHeight = int(self.cal.cellHeight)
        col = (x - left) / cellWidth
        row = (y - top) / cellHeight
        selectedAgenda = self.selectAgenda(row,col)
        if selectedAgenda != None:
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
                if selectedAgenda != None:
                    self.agenda.draw(selectedAgenda)
                else:
                    self.agenda.clear()
            elif row == 0:
                self.previousMonth()
                row = len(self.cal.monthArray) - 1
                self.row = row
                self.col = col
                selectedAgenda = self.selectAgenda(row,col)
                if selectedAgenda != None:
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
        if maxHours == None: return
        if maxHours > 24 or maxHours < 0:
            tkMessageBox.showerror("Impossible",
             "Please enter an integer 0-24.")
            return
        self.maxHours = maxHours
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish your tasks in the given work hours per day!")
            self.maxHours = original
            self.createAgenda()
            #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()
        self.canvas.delete(self.agendaTitle)
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,text="Agenda (" + str(self.maxHours) +\
             " hour days)",font=("Calibri", 20, "bold"))

    def toggleMaxDays(self):
        self.maxDays = not self.maxDays
        self.createAgenda() #update agenda
        #if self.agendaCalc == None:
        #    tkMessageBox.showerror("Impossible to Schedule",
        #     "You can't finish your tasks if you toggle your schedule optimization!")
        #    self.maxDays = not self.maxDays
        #    self.createAgenda()
        #    #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def addAssignment(self): #graphical implementation
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description == None: return
        hours = tkSimpleDialog.askinteger("Task Adder",
         "How many hours will it take to complete?")
        if hours == None: return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "When is it due? Enter MM/DD or MM/DD/YYYY")
        if dueString == None: return
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
        #pdb.set_trace()
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish that task in the given time per day!")
            self.tasks.remove(task.description)
            self.createAgenda()
            #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def addFixedTask(self): #same, but with a fixed task
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description == None: return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "What day is it? Enter MM/DD or MM/DD/YYYY")
        if dueString == None: return
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
        if timeString == None:
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
        #print task
        self.tasks.add(task)
        #print self.tasks.fixed
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish that task in the given time per day!")
            self.tasks.remove(task.description)
            self.createAgenda()
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def addRecurringTask(self):
        description = tkSimpleDialog.askstring("Task Adder",
         "What is the name of your task?")
        if description == None: return
        dueString = tkSimpleDialog.askstring("Task Adder",
         "Repeat until which day? Enter MM/DD or MM/DD/YYYY")
        if dueString == None: return
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
        if timeString == None:
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
        task = FixedTask(description,startTime,endTime,True)
        self.tasks.add(task)
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish that task in the given time per day!")
            self.tasks.remove(task.description)
            self.createAgenda()
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def removeTask(self):
        description = tkSimpleDialog.askstring("Task Remover",
         "What is the name of your task?")
        if description == None:
            return
            #tkMessageBox.showerror("Error", "You must provide a description!")
        removed = self.tasks.remove(description)
        if removed == None:
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
        if description == None:
            return
            #tkMessageBox.showerror("Error", "You must provide a description!")
        hours = tkSimpleDialog.askinteger("Task Completer",
         "How many hours did you complete?")
        if hours == None:
            return
        added = self.tasks.addHours(description,hours)
        if added == None:
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
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        self.cal.clear()
        self.cal = gCalendar(self.canvas,self.width,self.height,
            self.month,self.year)
        self.cal.draw(self)

    def nextMonth(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
        self.cal.clear()
        self.cal = gCalendar(self.canvas,self.width,self.height,
            self.month,self.year)
        self.cal.draw(self)

    def toggleDayHelper(self,dayint):
        if dayint in self.workDays: self.workDays.remove(dayint)
        else: self.workDays.append(dayint)

    def toggleWorkDay(self):
        dayint = tkSimpleDialog.askinteger("Workday Toggler","Which day do you want to toggle?")
        if dayint == None: return
        if (0 <= dayint <= 6) == False:
            tkMessageBox.showerror("Invalid Input","Which day do you want to toggle?")
        self.toggleDayHelper(dayint)
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish your tasks if you toggle that day!")
            self.toggleDayHelper(dayint)
            self.createAgenda()
            #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def toggleToday(self):
        self.workToday = not self.workToday
        self.createAgenda() #update agenda
        if self.agendaCalc == None:
            tkMessageBox.showerror("Impossible to Schedule",
             "You can't finish your tasks if you toggle that day!")
            self.workToday = not self.workToday
            self.createAgenda()
            #return
        self.selectAgenda(self.row,self.col)
        self.agenda.draw(self.selectedAgenda)
        self.cal.draw(self)
        self.saveData()

    def init(self):
        #draw calendar label
        self.cal = gCalendar(self.canvas,self.width,self.height,
        self.month,self.year) #gCalendar(month,year)
        self.createAgenda()
        self.cal.draw(self)
        #draw agenda label
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,text="Agenda (" + str(self.maxHours) +\
             " hour days)",font=("Calibri", 20, "bold"))
        self.agenda = Agenda(self.canvas,self.width,self.height,1,1,2012)
        self.agenda.clear()
        #self.agenda.draw([0]) #draw today's agenda when initializing
        b1 = Button(self.canvas, text="Previous Month",
         command=self.previousMonth) #initialize buttons
        b2 = Button(self.canvas, text="Next Month", command=self.nextMonth)
        b3 = Button(self.canvas, text="Add Assignment",
         command=self.addAssignment)
        b4 = Button(self.canvas, text="Add Fixed Task",
         command=self.addFixedTask)
        b5 = Button(self.canvas, text="Add Recurring Task",
         command=self.addRecurringTask)
        b6 = Button(self.canvas, text="Remove Task", command=self.removeTask)
        b7 = Button(self.canvas, text="Clear All Data", command=self.clearData)
        b8 = Button(self.canvas, text="Set Work Hours",
         command=self.setMaxHours)
        b9 = Button(self.canvas, text="Toggle Schedule Optimization",
         command=self.toggleMaxDays)
        b10 = Button(self.canvas, text="Search Calendar",
         command=self.calSearch)
        b11 = Button(self.canvas, text="Send Text", command=self.sendText)
        b12 = Button(self.canvas, text="Make iCal File", command=self.makeiCal)
        b13 = Button(self.canvas, text="I've Done Work!",
         command=self.addHours)
        b14 = Button(self.canvas, text="Toggle Work Days", command=self.toggleWorkDay)
        b15 = Button(self.canvas, text="Toggle Today", command=self.toggleToday)
        calwidth = (self.cal.right + self.cal.left) / 2
        #print calwidth
        col1 = self.cal.left + 1*(calwidth / 2) - 60
        col2 = self.cal.left + 2*(calwidth / 2) - 30
        col3 = self.cal.left + 3*(calwidth / 2)
        self.canvas.create_text(col1,self.height*29./40,
            text="Tasks",font=("Calibri", 20, "bold"))
        self.canvas.create_text(col2,self.height*29./40,
            text="Scheduling",font=("Calibri", 20, "bold"))
        self.canvas.create_text(col3,self.height*29./40,
            text="Management",font=("Calibri", 20, "bold"))
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
        self.canvas.create_window(col3,self.height*29./40+60, window=b11)
        self.canvas.create_window(col3,self.height*29./40+90, window=b12)
        self.canvas.create_window(col3,self.height*29./40+120, window=b7)
        self.canvas.pack()

    def run(self):
        # create the root and the canvas
        #global canvas
        self.root = Tk()
        self.root.resizable(width=FALSE, height=FALSE) #from kosbie
        self.canvas = Canvas(self.root, width=self.width, height=self.height)
        # Set up canvas data and call init
        self.init()
        if os.path.exists("cal.pkl"):
            self.loadData()
        self.canvas.delete(self.agendaTitle)
        self.agendaTitle = self.canvas.create_text(self.width*17./20,
            self.height*1./20,text="Agenda (" + str(self.maxHours) +\
             " hour days)",font=("Calibri", 20, "bold"))
        # set up events
        def mousePressedWrapper(event):
            self.mousePressed(event)
        def mouseMotionWrapper(event):
            self.mouseMotion(event)
        def mouseReleaseWrapper(event):
            self.mouseReleased(event)
        self.root.bind("<Button-1>", mousePressedWrapper) #wrappers needed
        self.root.bind("<B1-Motion>", mouseMotionWrapper)
        self.root.bind("<ButtonRelease-1>", mouseReleaseWrapper)
        #root.bind("<Key>", keyPressed)
        #timerFired()
        # and launch the app
        self.root.title("Ned's Intelligent Calendar Planner")
        self.root.mainloop()
        self.saveData()

app = CalendarPlanner(1000,700) #1000x700 canvas, default is 900x600
#app = CalendarPlanner()
#app.testAgenda() #run this to fill with test data
app.run()
