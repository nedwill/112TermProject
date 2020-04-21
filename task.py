"""
Task class
"""

# TODO(nedwill): migrate to using named members of this class
# while we expose the old tuple type for compatability
class Task:
    def __init__(self, name, hours_remaining, last_bucket_num):
        self.name = name
        self.hours_remaining = hours_remaining
        self.last_bucket_num = last_bucket_num

    def to_tuple(self):
        return (self.name, self.hours_remaining, self.last_bucket_num)
