class NotEnoughTime(Exception):
    pass


class InvalidTask(Exception):
    pass


class ScheduleFailure(Exception):
    def __init__(self, title="Impossible to Schedule", msg="Unknown scheduling error."):
        self.title = title
        self.msg = msg


class TaskAlreadyExists(Exception):
    pass
