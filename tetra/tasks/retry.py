from functools import partial
from tenacity import retry  # type: ignore

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

    def to_serializable(self):
        return None
