import redis
import redis.exceptions

from redis import StrictRedis, Redis
from typing import Union
from tenacity import retry, retry_if_exception_type


@retry(retry=retry_if_exception_type(redis.exceptions.ConnectionError))
def blpop(redis_conn: Union[StrictRedis, Redis], *args, **kwargs) -> bytes:
    """
    A wrapped version of BLPOPRPUSH commands with attached retries, used in the case that 
    network equipment interrupts the long-poll.
    """
    return redis_conn.blpop(*args, **kwargs)
