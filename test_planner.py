from hypothesis.stateful import GenericStateMachine
from hypothesis import strategy
from hypothesis.strategies import integers, text, tuples, just, sampled_from
from hypothesis.extra.datetime import datetimes
from planner import Planner
import unittest
from custom_exceptions import ScheduleFailure
import datetime

def test_set_max_hours():
	planner = Planner()
	planner.set_max_hours(0)

def test_add_task():
	planner = Planner()
	data = (u'', 0, 0, datetime.date(2000, 1, 1))
	planner.add_task(*data)

def test_add_same_name():
	"unicode bug"
	machine = PlannerMachine()
	steps = [('add_task', (u'', 8388608, 0, datetime.datetime(4455, 7, 13, 15, 55, 23, 881576))),
		('add_fixed_task', (u'', datetime.datetime(2464, 9, 1, 22, 0, 6, 681778), datetime.datetime(8725, 7, 10, 16, 10, 0, 564361)))]
	for step in steps:
		machine.execute_step(step)

class PlannerMachine(GenericStateMachine):
	def __init__(self):
		self.task_names = set()
		self.planner = Planner()

	def steps(self):
		add_task_strategy = strategy(tuples(just("add_task"), tuples(text(), integers(), integers(), datetimes())))
		#TODO: support recurring tasks
		add_fixed_task_strategy = strategy(tuples(just("add_fixed_task"), tuples(text(), datetimes(), datetimes())))
		set_max_hours_strategy = strategy(tuples(just("set_max_hours"), tuples(integers(min_value=0, max_value=24))))
		toggle_max_days_strategy = strategy(tuples(just("toggle_max_days"), tuples(just(None)))) #just a toggle, filler here
		always_available = add_task_strategy | add_fixed_task_strategy | set_max_hours_strategy | toggle_max_days_strategy
		if len(self.task_names) == 0:
			return always_available
		else:
			add_hours_strategy = strategy(tuples(just("add_hours"), tuples(sampled_from(self.task_names), integers())))
			toggle_work_day_strategy = strategy(tuples(just("toggle_work_day"), tuples(sampled_from(range(7)))))
			reschedule_task_strategy = strategy(tuples(just("reschedule_task"), tuples(sampled_from(self.task_names), datetimes())))
			delete_task_strategy = strategy(tuples(just("delete_task"), tuples(sampled_from(self.task_names))))
			return always_available | delete_task_strategy | add_hours_strategy | toggle_work_day_strategy | reschedule_task_strategy

	def execute_step(self, step):
		action, data = step
		if action == "add_task":
			(name, hours, hours_done, due) = data
			if name in self.task_names:
				return
			due = due.date() #make a date, not a datetime...
			assert self.planner.get_task(name) is None
			try:
				self.planner.add_task(name, hours, hours_done, due)
			except ScheduleFailure:
				return
			self.task_names.add(name)
			assert self.planner.get_task(name) is not None
		elif action == "add_fixed_task":
			name = data[0]
			if name in self.task_names:
				return
			assert name not in self.task_names
			assert self.planner.get_task(name) is None
			try:
				self.planner.add_fixed_task(*data)
			except ScheduleFailure:
				return
			self.task_names = self.task_names.add(name)
			assert self.planner.get_task(name) is not None
		elif action == "delete_task":
			name = data[0]
			assert name in self.task_names
			assert self.planner.get_task(name) is not None
			self.planner.remove_task(name)
			self.task_names.remove(name)
			assert self.planner.get_task(name) is None
		elif action == "add_hours":
			name = data[0]
			assert name in self.task_names
			self.planner.add_hours(*data)
		elif action == "toggle_work_day":
			self.planner.toggle_work_day(*data)
		elif action == "reschedule_task":
			name, date = data
			try:
				self.planner.reschedule_task(name, date.date())
			except ScheduleFailure:
				return
		elif action == "set_max_hours":
			try:
				self.planner.set_max_hours(*data)
			except ScheduleFailure:
				return
		elif action == "toggle_max_days":
			try:
				self.planner.toggle_max_days()
			except ScheduleFailure:
				return
		else:
			assert False
		#try to make schedule after doing action?
		#catch it trying to make the new schedule and don't include the new task if it fails

TestPlanner = PlannerMachine.TestCase

if __name__ == '__main__':
	test_set_max_hours()
	test_add_task()
	test_add_same_name()
	unittest.main()
