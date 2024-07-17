#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class to store and retrieve data from Redis.
    """
    def __init__(self):
        """
        Initialize the Cache class.
        Store an instance of the Redis client as a private variable named _redis.
        Flush the instance using flushdb.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis and return the generated random key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key


if __name__ == "__main__":
    # Example usage
    cache = Cache()

    data = b"hello"
    key = cache.store(data)
    print(key)

    local_redis = redis.Redis()
    print(local_redis.get(key))
