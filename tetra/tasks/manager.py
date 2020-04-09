from typing import Callable, Dict, Optional

from tetra.brokers import Broker
from tetra.tasks.retry import RetrySettings
from tetra.tasks.task import Task
from tetra.tools.__config__ import GLOBAL_NAMESPACE

# from tetra.tools.serializers import is_serializable


class TaskManager:
    def __init__(self, broker: Broker, namespace: str = GLOBAL_NAMESPACE) -> None:
        self.namespace = namespace
        self.broker = broker
        self.tasks: Dict[str, Task] = {}

    def register(self, *op_args, retry_settings: Optional[RetrySettings] = None, **op_kwargs) -> Callable:
        # @taskmanager.register
        if len(op_args) == 1 and callable(op_args[0]):
            task = Task(op_args[0], self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self.tasks[task.name] = task
            return self.tasks[task.name].run

        # @taskmanager.register()
        def wrap(f):
            task = Task(f, self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self.tasks[task.name] = task
            return self.tasks[f.__name__].run

        return wrap

    def work(self):
        self.broker.get_work(self.namespace)

    def get_task_by_name(self, name):
        return self.tasks.get(name)

    def __repr__(self):
        return f"TaskManager(namespace={self.namespace}, broker={self.broker}, tasks={list(self.tasks.values())})"
