from tasks import TaskList, FixedTask, Task

class ScheduleFailure(Exception):
    pass

class Planner(object):
    def __init__(self, tasks=None, max_hours=8):
        if tasks is None:
            self.tasks = TaskList()
        else:
            self.tasks = tasks
        self.work_today = True
        self.workDays = range(7)
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

    def attempt_to_schedule(self, modification=None, failure=None):
        assert self.current_agenda is not None  # already working
        if modification is None:
            def modification():
                pass
        if failure is None:
            def failure():
                pass
        modification()
        agenda = self.planner.create_agenda_safe()
        if agenda is None:
            failure()
            raise ScheduleFailure
        self.current_agenda = agenda

    def reschedule_task():
        pass
