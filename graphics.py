import datetime
from Tkinter import N, NE, NW
import calendar
import platform

if platform.system() == "Darwin":
    FONT = "Helvetica"
    SMALLFONT = (FONT, 10, "bold")
    MEDIUMFONT = (FONT, 18, "bold")
    FONT12 = (FONT, 12,)
    BIGFONT = (FONT, 20, "bold")
    HUGEFONT = (FONT, 26, "bold")
else: #assume linux
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
        self.elements = set()

    def draw(self, selectAgenda):
        raise Exception("Cannot draw generic class.")

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
        self.add(self.canvas.create_text(self.left + ((self.right - self.left) / 2),self.top,text="Hours",font=SMALLFONT,anchor=N))
        self.add(self.canvas.create_text(self.right,self.top,text="Due Date",
            font=SMALLFONT,anchor=NE))

    def draw(self, selectedAgenda):
        self.clear()
        for i in xrange(len(selectedAgenda)):
            item = selectedAgenda[i]
            tempDescription = str(item[0])
            if len(tempDescription) > 15:
                tempDescription = tempDescription[:14] + "..."
            newTop = self.top + 20*(i+1)
            if newTop + 40 > self.bottom:
                self.add(self.canvas.create_text(self.left,newTop,
                    text="......",font=FONT12,anchor=NW))
                break
            left = self.left + 4
            self.add(self.canvas.create_text(left,newTop,
                text=tempDescription,font=FONT12,anchor=NW))
            self.add(self.canvas.create_text(left + ((self.right - self.left) / 2),newTop,text=item[1],
             font=FONT12,anchor=N))
            self.add(self.canvas.create_text(self.right,newTop,
                text=item[0].due,font=FONT12,anchor=NE))

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

    def _day_matches(self, row, col, this_day):
        "if the given day is in the montharray at (row, col)"
        cond1 = self.monthArray[row][col] == this_day.day
        cond2 = self.month == this_day.month
        cond3 = self.year == this_day.year
        return all([cond1, cond2, cond3])

    def _get_coordinates(self, row, col):
        newLeft = self.left + self.cellWidth * col
        newRight = newLeft + self.cellWidth
        newTop = self.top + self.cellHeight * row
        newBottom = newTop + self.cellHeight
        return (newLeft, newRight, newTop, newBottom)

    def _draw_agenda_if_possible(self, planner, row, col):
        (newLeft, newRight, newTop, newBottom) = self._get_coordinates(row, col)
        selected_agenda = planner.getAgenda(row, col)
        if selected_agenda is not None:
            for i, item in enumerate(selected_agenda):
                #lots of hardcoded values here... bad
                newTop2 = newTop + 15*(i+1)
                tempDescription = item[0].description
                if newTop2 + 30 > newBottom:
                    self.add(self.canvas.create_text(newLeft+4,
                        newTop2,text="......",font=FONT12,anchor=NW))
                    break
                if len(tempDescription) > 15:
                    tempDescription = tempDescription[:11] + "..." + tempDescription[-3:]
                self.add(self.canvas.create_text(newLeft+4,newTop2,
                    text=tempDescription,font=FONT12,
                    anchor=NW))

    def _process_row_col(self, planner, row, col):
        (newLeft, newRight, newTop, newBottom) = self._get_coordinates(row, col)
        if row == 0: #create day of week labels on first pass
            self.add(self.canvas.create_text((newLeft+newRight)/2, self.height*7./80,text=self.days[col], font=FONT12))
        if self.monthArray[row][col] != 0:
            self.add(self.canvas.create_rectangle(newLeft, newTop, newRight, newBottom)) #day box
            if self._day_matches(row, col, self.selectedDay):
                self.add(self.canvas.create_rectangle(newLeft, newTop, newRight, newBottom, fill="yellow")) #selected box
            if self._day_matches(row, col, self.currentDay):
                self.add(self.canvas.create_rectangle(newLeft, newTop, newRight, newBottom, fill="green")) #today box
            self.add(self.canvas.create_text(newLeft+2,newTop+1,
                anchor=NW,text=self.monthArray[row][col],
                font=FONT12))
            self._draw_agenda_if_possible(planner, row, col)
        else:
            self.add(self.canvas.create_rectangle(newLeft, newTop, newRight, newBottom, fill="gray")) #day box

    def draw(self, planner):
        self.clear()
        self.add(self.canvas.create_text(self.width*15./40, self.height*1./20,
            text="{} {}".format(self.months[self.month-1], self.year), font=HUGEFONT))
        for row in xrange(self.weeks):
            for col in xrange(7):
                self._process_row_col(planner, row, col)
