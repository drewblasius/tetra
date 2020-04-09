from typing import Any, Callable, Dict, List, Optional

from tetra.brokers import Broker
from tetra.tasks.retry import RetrySettings
from tetra.tasks.task import Task
from tetra.tools.__config__ import GLOBAL_NAMESPACE

# from tetra.tools.serializers import is_serializable


class TaskManager:
    """Tetra's task management class.
    Args:
        broker (Broker): a tetra broker object to subscribe.
        namespace (str): the queue namespace of which the task manager is a member.
    Attributes:
        namespace (str): the queue namespace of which the task manager is a member.
        broker (Broker): a tetra broker object to subscribe.
    """

    def __init__(self, broker: Broker, namespace: str = GLOBAL_NAMESPACE) -> None:
        self.namespace = namespace
        self.broker = broker
        self._tasks: Dict[str, Task] = {}

    def register(self, *op_args, retry_settings: Optional[RetrySettings] = None, **op_kwargs) -> Callable:
        """Register a function to the queue and namespace
        Args:
            op_args (tuple): a Callable followed by the callable's positional arguments
            retry_settings (Optional[RetrySettings]): A retry settings object for the tetra queue.
            op_kwargs (dict): the Callable's keyword arguments

        Returns:
            Callable: the wrapped function that is now a member of the TaskManager.
        """
        # @taskmanager.register
        if len(op_args) == 1 and callable(op_args[0]):
            task = Task(op_args[0], self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self._tasks[task.name] = task
            return self._tasks[task.name].run

        # @taskmanager.register()
        def wrap(f) -> Callable:
            task = Task(f, self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self._tasks[task.name] = task
            return self._tasks[f.__name__].run

        return wrap

    def work(self) -> None:
        task: Dict[str, Any] = self.broker.get_work(self.namespace)
        print(task)

    def get_task_by_name(self, signature):
        """Get the Task object by it's signature.
        Args:
            signature (str): the signature of a registered function
        Returns:
            Task: the Tetra task object corresponding to a registered callable.
        """
        return self._tasks.get(signature)

    def list_tasks(self) -> List[str]:
        """List the task managers current tasks by signature.
        Returns:
            List[str]: the signatures of the TaskManager's registered tasks.
        """
        return list(self._tasks.keys())

    def __repr__(self):
        return f"TaskManager(namespace={self.namespace}, broker={self.broker}, tasks={list(self._tasks.values())})"
