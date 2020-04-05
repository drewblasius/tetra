from functools import partial
from tenacity import retry
from typing import Callable, Dict, List, Optional

from tetra.tools.log import logger


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


class Task:
    def __init__(self):
        pass

    def register(self, target: Callable, args: List, kwargs: Dict, retry_settings: Optional[RetrySettings] = None):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.retry_settings = retry_settings
        self.__retry_count = 0
        if self.retry_settings:
            self.retry_settings.assign_parent(self)

    def run(self):
        try:
            if not self.retry_settings:
                results = self.target(*self.args, **self.kwargs)

            else:
                results = self.retry_settings.retry_wrapper_function(self.target(*self.args, **self.kwargs))
            self.store_results(results)
        except Exception:
            self.mark_failed()

    def retry(self):
        pass

    def mark_failed(self):
        pass

    def store_results(self):
        pass
