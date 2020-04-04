import redis
import uuid
from dataclasses import dataclass

@dataclass
class BrokerTaskMetricsItem:
    task_name: str  # task name
    completed: int  # number of tasks completed
    elapsed: float  # seconds elapsed total


@dataclass
class BrokerMetrics:
    broker_uuid: uuid.uuid4
    broker_tasks: BrokerTaskMetricsItem


class RedisBroker:
    """First Broker Type"""

    def __init__(self, *args, **kwargs):
        self.uuid = uuid.uuid4()
        self.conn = None
        self.connection_args = args
        self.connection_kwargs = kwargs
        self.connect()

    def connect(self):
        self.conn = redis.Redis(*self.connection_args, **self.connection_kwargs)

    def beat(self):
        self.conn.setex(self.uuid, )