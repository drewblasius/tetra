import six
from typing import Callable
import uuid

from tetra.brokers import Broker
from tetra.tasks.executor import Executor
from tetra.tasks.retry import RetrySettings
from tetra.tools.__config__ import GLOBAL_NAMESPACE


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
        self.broker = broker
        self.run = self._wrap(function)  # direct execution
        self.run_async = self._wrap_async(function)  # queue based execution
        self.retry_settings = retry_settings

    def _wrap(self, f):
        @six.wraps(f)
        def wrapped_f(*args, **kwargs):
            task_id = uuid.uuid4()
            try:
                results = Executor.run(
                    task_id, self.namespace, self.function, *args, **kwargs, retry_settings=self.retry_settings
                )
            except Exception as e:
                self.mark_failed(task_id, e)
            self.store_results(task_id, results)
            return results

        return wrapped_f

    def _wrap_async(self, f):
        @six.wraps(f)
        def wrapped_f(*args, **kwargs):
            task_id = uuid.uuid4()
            results = Executor.run_async(
                task_id, self.namespace, self.function, self.broker, *args, **kwargs, retry_settings=self.retry_settings
            )
            return results

        return wrapped_f

    def mark_failed(self, task_id, exception):
        pass

    def store_results(self, task_id, results):
        pass

    def __repr__(self):
        return f"Task(name='{self.name}', namespace={self.namespace})"
