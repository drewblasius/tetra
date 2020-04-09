from typing import Any, Callable, Dict, Optional
import uuid

from tetra.brokers import Broker
from tetra.tasks.retry import RetrySettings
from tetra.tools.log import logger


class Executor:
    @staticmethod
    def run(
        task_id: uuid.UUID,
        namespace: str,
        function: Callable,
        *args: tuple,
        retry_settings: Optional[RetrySettings] = None,
        **kwargs: dict
    ):
        try:
            if retry_settings is None:
                results = function(*args, **kwargs)

            else:
                results = retry_settings.retry_wrapper_function(function(*args, **kwargs))
                return results
            # store results
            return results
        except Exception as e:
            logger.exception("ERROR")
            raise e

    @staticmethod
    def run_async(
        task_id: uuid.UUID,
        namespace: str,
        priority: int,
        function: Callable,
        broker: Broker,
        *args: tuple,
        retry_settings: Optional[RetrySettings] = None,
        **kwargs: dict
    ):
        retry_serializable: Optional[Dict[str, Any]] = None
        if retry_settings is not None:
            retry_serializable = retry_settings.to_serializable()
        received = broker.add_task(task_id, namespace, priority, function.__name__, args, kwargs, retry_serializable,)
        assert received, "Broker couldn't take up the task."
        return task_id
