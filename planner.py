from tasks import TaskList, FixedTask, Task
import datetime

class ScheduleFailure(Exception):
    def __init__(self, title="Impossible to Schedule", msg="Unknown scheduling error."):
        self.msg = msg

class Planner(object):
    def __init__(self, tasks=None, max_hours=8):
        if tasks is None:
            self.tasks = TaskList()
        else:
            self.tasks = tasks
        self.work_today = True
        self.workDays = set(range(7))
        self.max_hours = max_hours
        self.maxDays = False

    def create_agenda_safe(self):
        return self.tasks.calc_agenda(self.max_hours, self.maxDays, self.workDays, self.work_today)

    def createAgenda(self):
        self.current_agenda = self.create_agenda_safe()

    def add_task(self, description, hours, hoursDone, due):
        task = Task(description, hours, hoursDone, due)
        self.tasks.add(task)

    def add_fixed_task(self, description, startTime, endTime, recurring=None):
        task = FixedTask(description, startTime, endTime, recurring)
        self.tasks.add(task)

    def remove_task(self, description):
        self.tasks.remove(description)

    def get_latest_task(self):
        return self.tasks.latest_task

    def set_latest_task(self, date):
        self.tasks.latest_task = date

    def _attempt_to_schedule(self, modification=None, failure=None, err_msg="Unknown scheduling error."):
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

    def init_schedule(self):
        self._attempt_to_schedule()

    def toggleDayHelper(self, day):
        if day in self.workDays:
            self.workDays.remove(day)
        else:
            self.workDays.add(day)

    def toggle_work_day(self, day):
        if not (0 <= day <= 6):
            raise ScheduleFailure(title="Invalid Input", msg="Please enter a day 0-6.")
        def modification():
            self.toggleDayHelper(day)
        failure = modification
        err_msg = "You can't finish your tasks if you toggle that day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def toggle_work_today(self):
        def modification():
            self.work_today = not self.work_today
        failure = modification
        err_msg = "You can't finish your tasks if you toggle that day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def reschedule_task(self, task, date):
        if hasattr(task, "recurring") and task.recurring:
            raise ScheduleFailure(msg="You can't reschedule a recurring task!")
        if date < datetime.date.today():
            raise ScheduleFailure(msg="You can't reschedule that task to the past!")
        if date > self.planner.tasks.latest_task:
            self.tasks.latest_task = date

        originaldue = task.due
        def modification():
            task.due = date
        def failure():
            task.due = originaldue
        err_msg = "You can't finish that task in the given time per day!"
        self._attempt_to_schedule(modification, failure, err_msg)

    def set_max_hours(self, new_max_hours):
        original = self.planner.max_hours
        if new_max_hours > 24 or new_max_hours < 0:
            raise ScheduleFailure(title="Invalid Input", msg="Please enter an integer 0-24.")
        
        def modification():
            self.planner.max_hours = new_max_hours
        def failure():
            self.planner.max_hours = original
        err_msg = "You can't finish your tasks in the given work hours per day!"

        self._attempt_to_schedule(modification, failure, err_msg)

    def toggle_max_days(self):
        def modification():
            self.maxDays = not self.maxDays
        failure = modification
        err_msg = "You can't finish your tasks if you toggle your schedule optimization!"
        self._attempt_to_schedule(modification, failure, err_msg)
