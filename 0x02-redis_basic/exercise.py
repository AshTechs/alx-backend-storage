#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional


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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve string data from Redis and decode it.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve integer data from Redis.
        """
        return self.get(key, int)


if __name__ == "__main__":
    # Example usage
    cache = Cache()

    # Test cases to verify the functionality
    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }

    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value
        print(f"Key: {key}, Retrieved value: {cache.get(key, fn=fn)}")
