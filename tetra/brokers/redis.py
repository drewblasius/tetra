from dataclasses import dataclass
import threading
import time
from typing import Any, Dict, Optional
import uuid

from tetra.tools.__config__ import TETRA_UNIT_TESTING

if TETRA_UNIT_TESTING:
    import fakeredis as redis  # type: ignore
else:
    import redis  # type: ignore


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
    broker_uuid: uuid.UUID
    broker_tasks: BrokerTaskMetricsColletion


class RedisBroker:
    """First Broker Type"""

    def __init__(
        self,
        role: str,
        *args,
        queue_database=13,
        result_database=14,
        management_databse=15,
        heartbeat_frequency=60,
        **kwargs
    ):
        self.uuid = uuid.uuid4()
        self.conn = None
        self.connection_args = args
        self.connection_kwargs = kwargs
        self.queue_database = queue_database
        self.queue_database = management_databse
        self.result_database = result_database
        self.heartbeat_frequency = 60
        self.__connect()
        self.alive = True
        self.pulse = self.__start_heartbeat()

    def __connect(self):
        self.queue_conn = redis.Redis(*self.connection_args, db=self.queue_database, **self.connection_kwargs)
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

    def __register_death(self):
        self.alive = False

    def __del__(self):
        self.__register_death()

    def get_work(self, namespace):
        # self.queue_conn
        pass

    def add_task(
        self,
        task_id: uuid.UUID,
        namespace: str,
        priority: int,
        signature: str,
        args: tuple,
        kwargs: Optional[Dict[str, Any]],
        retry_serializable: Optional[Dict[str, Any]],
    ):
        pass
