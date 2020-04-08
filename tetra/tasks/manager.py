from functools import partial
from tenacity import retry
import uuid
from typing import Callable, Dict, List, Optional
import six
from tetra.brokers import Broker
from tetra.tools.log import logger
from tetra.tools.serializers import is_serializable
import logging

logger = logging.getLogger(__name__)

GLOBAL_NAMESPACE = "global"


class RetrySettings:
    def __init__(self, **kwargs):
        kwargs["retry_error_callback"] = self.retry_callback
        self.retry_wrapper_function = partial(retry, **kwargs)
        self.parent = None

    def retry_callback(self, retry_state):
        if self.parent is not None and hasattr(self.parent, "__retry_count"):
            self.parent.__retry_count += 1
        logger.error(
            'Retrying {0}: attempt {1} ended with: {2}'.format(
                retry_state.fn, retry_state.attempt_number, retry_state.outcome
            )
        )

    def assign_parent(self, parent):
        self.parent = parent

    def to_serializable(self):
        return None


class TaskRunner:
    @staticmethod
    def run(function, *args, retry_settings=None, **kwargs):
        task_id = uuid.uuid4()
        try:
            if retry_settings is None:
                results = function(*args, **kwargs)

            else:
                results = retry_settings.retry_wrapper_function(function(*args, **kwargs))
                return results
            return results
        except Exception as e:
            logger.exception("ERROR")
            raise e

    @staticmethod
    def run_async(function, broker, *args, retry_settings=None, **kwargs):
        task_id = uuid.uuid4()
        if retry_settings is None:
            received = broker.add_task(task_id, function.__name__, function, args, kwargs, retry_settings=None)
            assert received, "Broker couldn't take up the task."
        else:
            received = broker.add_task(
                task_id, function.__name__, args, kwargs, retry_settings=retry_settings.to_serializable()
            )
            assert received, "Broker couldn't take up the task."
        return task_id


class Task:
    def __init__(
        self,
        function: Callable,
        broker: Broker,
        namespace: str = GLOBAL_NAMESPACE,
        retry_settings: RetrySettings = None,
    ):
        self.namespace = namespace
        self.name = function.__name__
        self.function = function
        self.run = self._wrap(function)
        self.run_async = self._wrap_async(function)
        self.retry_settings = retry_settings

    def _wrap(self, f):
        @six.wraps(f)
        def wrapped_f(*args, **kwargs):
            results = TaskRunner.run(self.function, *args, **kwargs, retry_settings=self.retry_settings)
            return results

        return wrapped_f

    def _wrap_async(self, f):
        @six.wraps(f)
        def wrapped_f(*args, **kwargs):
            results = TaskRunner.run_async(
                self.function, self.broker, *args, **kwargs, retry_settings=self.retry_settings
            )
            return results

        return wrapped_f

    def mark_failed(self, task_id, exception):
        pass

    def store_results(self, task_id, results):
        pass

    def __repr__(self):
        return f"Task(name='{self.name}', namespace={self.namespace})"


class TaskManager:
    def __init__(self, broker: Broker, namespace: str = GLOBAL_NAMESPACE):
        self.namespace = namespace
        self.broker = broker
        self.__retry_count = 0
        self.tasks = {}

    def register(self, *op_args, retry_settings: Optional[RetrySettings] = None, **op_kwargs):
        if len(op_args) == 1 and callable(op_args[0]):
            task = Task(op_args[0], self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self.tasks[task.name] = task
            return self.tasks[task.name].run

        # argument wrap with callable
        def wrap(f):
            task = Task(f, self.broker, namespace=self.namespace, retry_settings=retry_settings)
            self.tasks[task.name] = task
            return self.tasks[f.__name__].run

        return wrap

    def get_task_by_name(self, name):
        return self.tasks.get(name)

    def __repr__(self):
        return f"TaskManager(namespace={self.namespace}, broker={self.broker}, tasks={list(self.tasks.values())})"
