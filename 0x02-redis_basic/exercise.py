#!/usr/bin/env python3
"""
Cache module for storing data in Redis.
"""

import redis
import uuid
import functools
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of calls to a method.

    Args:
        method (Callable): The method to decorate.

    Returns:
        Callable: The decorated method.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to increment the call count & call the original meth.
        """
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a method.

    Args:
        method (Callable): The method to decorate.

    Returns:
        Callable: The decorated method.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function to store inputs and outputs of the original method.
        """
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))

        output = method(self, *args, **kwargs)

        self._redis.rpush(output_key, str(output))

        return output

    return wrapper


def replay(method: Callable):
    """
    Display the history of calls of a particular function.

    Args:
        method (Callable): The method to display the history for.
    """
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"
    redis_instance = method.__self__._redis

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    print(f"{method.__qualname__} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print((f"{method.__qualname__}(*{inp.decode('utf-8')})
               -> {out.decode('utf-8')}"))


class Cache:
    """
    Cache class to interact with Redis for storing and retrieving data.
    """
    def __init__(self):
        """
        Initialize the Cache class and flushing the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
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

    def get((self, key: str, fn: Optional[Callable]=None)
            -> Union[str, bytes, int, float, None]):
        """
        Retrieve data from Redis using the given key.

        Args:
            key (str): The key to retrieve the data.
            fn (Optional[Callable]): A function to convert the data.

        Returns:
            Union: The retrieved data or None if the key does not exist.
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
            Optional: The retrieved string or None if the key does not exist.
        """
        return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis using the given key.

        Args:
            key (str): The key to retrieve the data.

        Returns:
            Optional: The retrieved integer or None if the key does not exist.
        """
        return self.get(key, lambda d: int(d))


if __name__ == "__main__":
    cache = Cache()

    cache.store("foo")
    cache.store("bar")
    cache.store(42)
    replay(cache.store)
