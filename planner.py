from tasks import FixedTask, Task
from task_manager import TaskManager
import datetime

class ScheduleFailure(Exception):
    def __init__(self, title="Impossible to Schedule", msg="Unknown scheduling error."):
        self.title = title
        self.msg = msg

class Planner(object):
    def __init__(self, tasks=None, max_hours=8, max_days=False, debug=False):
        if tasks is None:
            self.tasks = TaskManager()
        else:
            self.tasks = tasks
        self.work_today = True
        self.workDays = set(range(7))
        self.max_hours = max_hours
        self.max_days = max_days
        self.debug = debug

    def _attempt_to_schedule(self, modification=None, failure=None, err_msg="Unknown scheduling error."):
        if self.debug:
            modification()
            return
        assert self.current_agenda is not None  # already working
        if modification is None:
            def modification():
                pass
        if failure is None:
            def failure():
                pass
        modification()
        agenda = self.create_agenda_safe()
        if agenda is None:
            failure()
            raise ScheduleFailure(msg=err_msg)
        self.current_agenda = agenda

    def create_agenda_safe(self):
        return self.tasks.calc_agenda(self.max_hours, self.max_days, self.workDays, self.work_today, trivial=False)

    def create_agenda_trivial(self):
        "for testing"
        return self.tasks.calc_agenda(self.max_hours, self.max_days, self.workDays, self.work_today, trivial=True)

    def createAgenda(self):
        self.current_agenda = self.create_agenda_safe()

    def _add_task_and_schedule(self, task):
        def modification():
            self.tasks.add(task)
        def failure():
            self.tasks.remove(task)
        err_msg = "You can't finish that task in the given time per day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def add_task(self, description, hours, hoursDone, due):
        task = Task(description, hours, hoursDone, due)
        self._add_task_and_schedule(task)

    def add_fixed_task(self, description, startTime, endTime, recurring=None):
        days = (endTime - startTime).days
        if days > 0 or endTime.day != startTime.day:
            raise ScheduleFailure(title="Invalid Task",
                msg="Your task cannot be longer than 24 hours or span multiple days.")
        task = FixedTask(description, startTime, endTime, recurring)
        self._add_task_and_schedule(task)

    def remove_task(self, description):
        if description not in self.tasks.fixed and description not in self.tasks.assignments:
            raise ScheduleFailure(title="Invalid Task", msg="There was no assignment or task found matching that description!")
        def modification():
            self.tasks.remove(description)
        def failure(): #this can't fail as there are less things in the schedule
            pass
        self._attempt_to_schedule(modification, failure)

    def add_hours(self, description, hours):
        if hours < 1:
            raise ScheduleFailure(title="Invalid Hours", msg="Hours completed must be at least 1.")
        if description not in self.tasks.assignments:
            raise ScheduleFailure(title="Invalid Task", msg="There was no assignment found matching that description!")
        def modification():
            self.tasks.add_hours(description, hours)
        def failure():
            pass #cannot cause failure by adding hours
        self._attempt_to_schedule(modification, failure)

    def get_latest_task(self):
        return self.tasks.latest_task

    def set_latest_task(self, date):
        self.tasks.latest_task = date

    def init_schedule(self):
        self._attempt_to_schedule()

    def toggle_work_day(self, day):
        if not (0 <= day <= 6):
            raise ScheduleFailure(title="Invalid Input", msg="Please enter a day 0-6.")
        def modification():
            if day in self.workDays:
                self.workDays.remove(day)
            else:
                self.workDays.add(day)
        failure = modification
        err_msg = "You can't finish your tasks if you toggle that day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def toggle_work_today(self):
        def modification():
            self.work_today = not self.work_today
        failure = modification
        err_msg = "You can't finish your tasks if you toggle today!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def reschedule_task(self, task, date):
        if hasattr(task, "recurring") and task.recurring:
            raise ScheduleFailure(msg="You can't reschedule a recurring task!")
        if date < datetime.date.today():
            raise ScheduleFailure(msg="You can't reschedule that task to the past!")
        if date > self.tasks.latest_task:
            self.tasks.latest_task = date

        originaldue = task.due
        def modification():
            task.due = date
        def failure():
            task.due = originaldue
        err_msg = "You can't finish that task in the given time per day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def set_max_hours(self, new_max_hours):
        if new_max_hours > 24 or new_max_hours < 0:
            raise ScheduleFailure(title="Invalid Input", msg="Please enter an integer 0-24.")
        original = self.max_hours
        def modification():
            self.max_hours = new_max_hours
        def failure():
            self.max_hours = original
        err_msg = "You can't finish your tasks in the given work hours per day!"

        self._attempt_to_schedule(modification, failure, err_msg)

    def toggle_max_days(self):
        def modification():
            self.max_days = not self.max_days
        failure = modification
        err_msg = "You can't finish your tasks if you toggle your schedule optimization!"
        self._attempt_to_schedule(modification, failure, err_msg)
