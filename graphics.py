import datetime
from Tkinter import N, NE, NW
import calendar
import platform

if platform.system() == "Darwin":
    FONT = "Helvetica"
    SMALLFONT = (FONT, 10, "bold")
    MEDIUMFONT = (FONT, 18, "bold")
    FONT12 = (FONT, 12, "bold")
    BIGFONT = (FONT, 20, "bold")
    HUGEFONT = (FONT, 26, "bold")
else: #assume linux
    print "case2"
    FONT = "Ubuntu"
    SMALLFONT = (FONT, 5, "bold")
    MEDIUMFONT = (FONT, 9, "bold")
    FONT12 = (FONT, 6, "bold")
    BIGFONT = (FONT, 10, "bold")
    HUGEFONT = (FONT, 13, "bold")

class GraphicsElement(object): #basic graphical element
    def __init__(self,canvas,width,height):
        self.canvas = canvas #element must know how to access its canvas
        self.width = width #element must know its canvas size to position itself
        self.height = height
        self.elements = set() #keep track of canvas elements to clear

    #add elements to a list so we have a list
    #associated with each GraphicsElement
    def add(self, element):
        self.elements.add(element)

    def clear(self): #use the list of elements for this GraphicsElement to clear only this object from the canvas
        for element in self.elements: #most basic
            self.canvas.delete(element)

    def draw(self, selectAgenda):
        pass #is this necessary?

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
            text="Description",font=SMALLFONT,anchor=NW))
        self.add(self.canvas.create_text(self.left + ((self.right - \
            self.left) / 2),self.top,text="Hours",font=SMALLFONT,anchor=N))
        self.add(self.canvas.create_text(self.right,self.top,text="Due Date",
            font=SMALLFONT,anchor=NE))

    def draw(self, selectedAgenda):
        #loop to create rectangles
        #loop to create labels for calendar
        self.clear()
        for i in xrange(len(selectedAgenda)):
            item = selectedAgenda[i]
            tempDescription = str(item[0])
            if len(tempDescription) > 15:
                tempDescription = tempDescription[:14] + "..."
            newTop = self.top + 20*(i+1)
            if newTop + 40 > self.bottom:
                self.add(self.canvas.create_text(self.left,newTop,
                    text="......",font=MEDIUMFONT,anchor=NW))
                break
            self.add(self.canvas.create_text(self.left,newTop,
                text=tempDescription,font=MEDIUMFONT,anchor=NW))
            self.add(self.canvas.create_text(self.left +\
             ((self.right - self.left) / 2),newTop,text=item[1],
             font=MEDIUMFONT,anchor=N))
            self.add(self.canvas.create_text(self.right,newTop,
                text=item[0].due,font=MEDIUMFONT,anchor=NE))

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

    def draw(self, planner, calSearch=None):
        self.clear()
        self.add(self.canvas.create_text(self.width*15./40,
            self.height*1./20,text=self.months[self.month-1] + " " + \
            str(self.year),font=HUGEFONT))
        for row in xrange(self.weeks):
            for col in xrange(7):
                newLeft = self.left+self.cellWidth*col
                newRight = newLeft + self.cellWidth
                newTop = self.top+self.cellHeight*row
                newBottom = newTop+self.cellHeight
                if row == 0: #create day of week labels on first pass
                    self.add(self.canvas.create_text((newLeft+newRight)/2,
                        self.height*7./80,text=self.days[col],
                        font=FONT12))
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
                    if selectedAgenda is not None and len(selectedAgenda) > 0 \
                    and calSearch is not None:
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
                        font=FONT12))
                    if selectedAgenda is not None:
                        for i in xrange(len(selectedAgenda)):
                            item = selectedAgenda[i]
                            newTop2 = newTop + 15*(i+1)
                            tempDescription = item[0].description
                            if newTop2 + 30 > newBottom:
                                self.add(self.canvas.create_text(newLeft,
                                    newTop2,text="......",font=SMALLFONT,anchor=NW))
                                break
                            if len(tempDescription) > 15:
                                tempDescription = tempDescription[:11] +\
                                 "..." + tempDescription[-3:]
                            self.add(self.canvas.create_text(newLeft,newTop2,
                                text=tempDescription,font=MEDIUMFONT,
                                anchor=NW))
                else:
                    self.add(self.canvas.create_rectangle(newLeft,newTop,
                    newRight,newBottom,fill="gray")) #day box