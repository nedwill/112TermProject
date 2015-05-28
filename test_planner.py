from hypothesis.stateful import GenericStateMachine
from hypothesis import strategy
from strategy import integers, strings
from hypothesis.specifiers import sampled_from, just
from hypothesis.extra.datetime import datetimes

class PlannerMachine(GenericStateMachine):
	def __init__(self):
		self.task_names = set()

	def steps(self):
		add_task_strategy = strategy((just("add_task"), strings(), integers(), integers(), datetimes()))
		delete_task_strategy = strategy((just("delete_task"), sampled_from(self.task_names)))
		if len(self.task_names) == 0:
			return add_task_strategy
		else:
			return add_task_strategy | delete_task_strategy

	def execute_step(self, step):
		action, data = step


