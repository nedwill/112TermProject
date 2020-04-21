import datetime
from custom_exceptions import InvalidTask

# whoever is maintaining this when I'm dead, please increase as necessary
# this is how we used to deal with Big(O) problems in 2015.. make the problem
# smaller
MAX_YEAR = 2100


class Task(object):  # recurring attribute here?
    def __init__(self, description, hours, due):
        if hours <= 0:
            raise InvalidTask
        if due.year > MAX_YEAR:
            raise InvalidTask
        self.description = description
        self.hours = hours
        self.due = due

    def set_due_date(self, date):
        if date.year > MAX_YEAR:
            raise InvalidTask
        self.due = date

    def bucket_num(self):
        return (self.due - datetime.date.today()).days

    def __str__(self):
        return self.description

    def __repr__(self):
        return "{}, Hours Left: {}, Days Left: {}".format(
            self.description,
            self.hours - self.hours_done,
            (self.due - datetime.date.today()).days,
        )


class FixedTask(Task):
    def __init__(self, description, hours, due, recurring=None):
        # self.startTime = startTime
        # self.endTime = endTime
        # if endTime <= startTime:
        #    raise InvalidTask
        # hours = ((endTime - startTime).seconds)/3600
        # due = startTime.date()
        self.recurring = recurring
        super(FixedTask, self).__init__(description, hours, due)

    # def __str__(self):
    #    return self.description + " {}:{:02d}-{}:{:02d}".format(self.startTime.hour,
    #        self.startTime.minute, self.endTime.hour, self.endTime.minute)

    # def __repr__(self):
    #    return "{}, Hours Left: {}, Days Left: {}".format(self.description,
    #        self.hours - self.hours_done, (self.due - datetime.date.today()).days)

class BackgroundTask(Task):
    # TODO(nedwill): support tasks that we think about in the background
    pass


class RecurringMultiHour(Task):
    # TODO(nedwill): recurring tasks that can be worked on freely over some
    # time period i.e. laundry or other chores that must be done regularly
    # but not at a fixed time
    pass


class UnstructuredTime(Task):
    # TODO(nedwill): support scheduled unstructured time
    pass
