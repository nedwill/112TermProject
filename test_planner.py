from hypothesis.stateful import GenericStateMachine
from hypothesis import strategy
from hypothesis.strategies import integers, text, tuples, just
from hypothesis.specifiers import sampled_from
from hypothesis.extra.datetime import datetimes
from planner import Planner
import unittest

class PlannerMachine(GenericStateMachine):
	def __init__(self):
		self.task_names = set()
		self.planner = Planner()

	def steps(self):
		add_task_strategy = strategy(tuples(just("add_task"), tuples(text(), integers(), integers(), datetimes())))
		delete_task_strategy = strategy(tuples(just("delete_task"), tuples(sampled_from(self.task_names))))
		#TODO: support recurring tasks
		add_fixed_task_strategy = strategy(tuples(just("add_fixed_task"), tuples(text(), datetimes(), datetimes())))
		add_hours_strategy = strategy(tuples(just("add_hours"), tuples(sampled_from(self.task_names), integers())))
		toggle_work_day_strategy = strategy(tuples(just("toggle_work_day"), tuples(sampled_from(range(7)))))
		reschedule_task_strategy = strategy(tuples(just("reschedule_task"), tuples(sampled_from(self.task_names), datetimes())))
		set_max_hours_strategy = strategy(tuples(just("set_max_hours"), tuples(integers())))
		toggle_max_days_strategy = strategy(tuples(just("toggle_max_days"), tuples(just(None)))) #just a toggle, filler here
		always_available = add_task_strategy | add_fixed_task_strategy | set_max_hours_strategy | toggle_max_days_strategy
		if len(self.task_names) == 0:
			return always_available
		else:
			return always_available | delete_task_strategy | add_hours_strategy | toggle_work_day_strategy | reschedule_task_strategy

	def execute_step(self, step):
		action, data = step
		if action == "add_task":
			name = data[0]
			if name in self.task_names:
				return
			assert self.planner.get_task(name) is None
			self.planner.add_task(*data)
			assert self.planner.get_task(name) is not None
		elif action == "delete_task":
			name = data[0]
			assert name in self.task_names
			assert self.planner.get_task(name) is not None
			self.planner.remove_task(name)
			assert self.planner.get_task(name) is None
		elif action == "add_fixed_task":
			name = data[0]
			if name in self.task_names:
				return
			assert self.planner.get_task(name) is None
			self.planner.add_fixed_task(name)
			assert self.planner.get_task(name) is not None
		elif action == "add_hours":
			name = data[0]
			assert name in self.task_names
			self.planner.add_hours(*data)
		elif action == "toggle_work_day":
			self.planner.toggle_work_day(*data)
		elif action == "reschedule_task":
			self.planner.reschedule_task(*data)
		elif action == "set_max_hours":
			self.planner.set_max_hours(*data)
		elif action == "toggle_max_days":
			self.planner.toggle_max_days()
		#try to make schedule after doing action?
		#catch it trying to make the new schedule and don't include the new task if it fails

TestPlanner = PlannerMachine.TestCase

if __name__ == '__main__':
	unittest.main()

