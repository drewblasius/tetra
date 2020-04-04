from dataclasses import dataclass
import redis
import threading
import time
from typing import Dict
import uuid


@dataclass
class BrokerTaskMetricsItem:
    task_name: str  # task name
    succeeded: int  # number of tasks with a success status
    retried: int  # number of tasks that had entered a retry status
    failed: int  # number of tasks that failed
    elapsed: float  # seconds elapsed total


class BrokerTaskMetricsColletion:
    tasks: Dict[str, BrokerTaskMetricsItem]


@dataclass
class BrokerMetrics:
    broker_uuid: uuid.uuid4
    broker_tasks: BrokerTaskMetricsColletion


class RedisBroker:
    """First Broker Type"""

    def __init__(self, role: str, *args, result_database=14, management_databse=15, heartbeat_frequency=60, **kwargs):
        self.uuid = uuid.uuid4()
        self.conn = None
        self.connection_args = args
        self.connection_kwargs = kwargs
        self.management_databse = management_databse
        self.result_database = result_database
        self.heartbeat_frequency = 60
        self.connect()
        self.alive = True
        self.pulse = self.__start_heartbeat()

    def connect(self):
        self.result_conn = redis.Redis(*self.connection_args, db=self.result_database, **self.connection_kwargs)
        self.management_conn = redis.Redis(*self.connection_args, db=self.management_conn, **self.connection_kwargs)

    def __beat(self):
        self.management_conn.setex(self.uuid, self.heartbeat_frequency + 1, self.management_conn)

    def __heartbeat(self):
        while self.alive:
            self.__beat()
            time.sleep(self.heartbeat_frequency)

    def __start_heartbeat(self):
        pulse = threading.Thread(target=self.__heartbeat)
        pulse.start()
        return pulse

    def register_death(self):
        self.alive = False
