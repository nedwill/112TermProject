#dead functions live here
from icalendar import Calendar, Event

def makeiCal(self):
    #myFormats = [('iCalendar File','*.ics')] #irrelevant on mac
    fileName = tkFileDialog.asksaveasfilename(parent=self.root,
        initialfile="mySchedule.ics",defaultextension=".ics",
        title="Save the iCalendar file...")
    if fileName is None or len(fileName) < 1: return
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
    if number is None: return
    self.userNumber = number

def getCarrier(self):
    self.carrier = None
    carrier = tkSimpleDialog.askstring("Cell Carrier",
     "Enter AT&T, Verizon, T-Mobile, or Sprint")
    if carrier is None: return
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
    if self.userNumber is not None and self.carrier is not None:
        check = tkMessageBox.askyesno("Phone number already saved.",
         "Do you want to use the number %s with carrier %s?" %\
          (self.userNumber,self.carrier))
        if check == False:
            self.getNumber()
            if self.userNumber is None: return
            self.getCarrier()
            if self.carrier is None: return
    else: #fix logic here?
        self.getNumber()
        if self.userNumber is None: return
        self.getCarrier()
        if self.carrier is None: return
    if self.carrier is None:
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