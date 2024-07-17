#!/usr/bin/env python3
"""
This module implements a Cache class with a replay function to display
the history of calls of a particular function using Redis.
"""

import redis
from typing import Callable, Union, Optional
import uuid
import functools


class Cache:
    """
    Cache class to store and retrieve data from Redis.
    Implements replay functionality to display call history.
    """
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis and return the key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get((self, key: str, fn: Optional[Callable]=None)
            -> Union[str, bytes, int, float]):
        """
        Retrieve data from Redis and optionally apply a conversion function.
        """
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> str:
        """
        Retrieve string data from Redis.
        """
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """
        Retrieve integer data from Redis.
        """
        return self.get(key, int)


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of calls to a method.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, output)

        return output

    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls to a method.
    """
    redis_instance = method.__self__._redis
    method_name = method.__qualname__

    input_key = f"{method_name}:inputs"
    output_key = f"{method_name}:outputs"

    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")
    for input_, output in zip(inputs, outputs):
        print((f"{method_name}(*{input_.decode('utf-8')},)
               -> {output.decode('utf-8')}"))


Cache.store = call_history(Cache.store)


if __name__ == "__main__":
    # Example usage
    cache = Cache()
    cache.store("foo")
    cache.store("bar")
    cache.store(42)
    replay(cache.store)
