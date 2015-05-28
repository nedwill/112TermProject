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
		#TODO: support recurring tasks
		add_fixed_task_strategy = strategy((just("add_fixed_task"), strings, datetimes(), datetimes()))
		add_hours_strategy = strategy((just("add_hours"), sampled_from(self.task_names, integers())))
		toggle_work_day_strategy = strategy((just("toggle_work_day"), sampled_from(range(7))))
		reschedule_task_strategy = strategy((just("reschedule_task"), sampled_from(self.task_names), datetimes()))
		set_max_hours_strategy = strategy((just("set_max_hours"), integers()))
		toggle_max_days_strategy = strategy((just("toggle_max_days"), just(None))) #just a toggle, filler here
		always_available = add_task_strategy | add_fixed_task_strategy | set_max_hours_strategy | toggle_max_days_strategy
		if len(self.task_names) == 0:
			return always_available
		else:
			return always_available | delete_task_strategy | add_hours_strategy | toggle_work_day_strategy | reschedule_task_strategy

	def execute_step(self, step):
		action, data = step
		#try to make schedule after doing action?
		#catch it trying to make the new schedule and don't include the new task if it fails
