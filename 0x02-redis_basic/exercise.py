#!/usr/bin/env python3
"""
Cache module for storing data in Redis.
"""

import redis
import uuid
import functools
from typing import Union, Callable, Optional

def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs of a function.

    Args:
        method (Callable): The method to decorate.

    Returns:
        Callable: The decorated method with history tracking.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store input and output history and call the original method.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store input arguments in Redis
        self._redis.rpush(input_key, str(args))

        # Call the original method
        result = method(self, *args, **kwargs)

        # Store output result in Redis
        self._redis.rpush(output_key, result)

        return result

    return wrapper

class Cache:
    """
    Cache class to interact with Redis for storing and retrieving data.
    """
    def __init__(self):
        """
        Initialize the Cache class by creating a Redis client and flushing the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis using the given key and an optional conversion function.

        Args:
            key (str): The key to retrieve the data.
            fn (Optional[Callable]): A function to convert the data.

        Returns:
            Union[str, bytes, int, float, None]: The retrieved data or None if the key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string from Redis using the given key.

        Args:
            key (str): The key to retrieve the data.

        Returns:
            Optional[str]: The retrieved string or None if the key does not exist.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis using the given key.

        Args:
            key (str): The key to retrieve the data.

        Returns:
            Optional[int]: The retrieved integer or None if the key does not exist.
        """
        return self.get(key, lambda d: int(d))

if __name__ == "__main__":
    cache = Cache()

    s1 = cache.store("first")
    print(s1)
    s2 = cache.store("secont")
    print(s2)
    s3 = cache.store("third")
    print(s3)

    inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
    outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

    print("inputs: {}".format(inputs))
    print("outputs: {}".format(outputs))
