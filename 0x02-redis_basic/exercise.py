#!/usr/bin/env python3
"""
Cache module for storing data in Redis.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class to interact with Redis for storing and retrieving data.
    """
    def __init__(self):
        """
        Initialize Cache class by creating a Redis client & flushing database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis using a randomly generated key.

        Args:
            data (Union[str, bytes, int, float]): The data to store in Redis.

        Returns:
            str: The generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
