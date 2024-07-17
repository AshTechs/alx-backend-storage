#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
'''The module-level Redis instance.
'''


def cache_request(expiration: int = 10):
    '''Decorator to cache the output of fetched data.
    '''
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(url: str) -> str:
            '''The wrapper function for caching the output.
            '''
            redis_store.incr(f'count:{url}')
            cached_result = redis_store.get(f'result:{url}')
            if cached_result:
                return cached_result.decode('utf-8')
            result = method(url)
            redis_store.setex(f'result:{url}', expiration, result)
            return result
        return wrapper
    return decorator


@cache_request(expiration=10)
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text


def get_access_count(url: str) -> int:
    '''Returns the count of how many times a URL was accessed.
    '''
    count = redis_store.get(f'count:{url}')
    return int(count) if count else 0


if __name__ == '__main__':
    # Example usage
    url = 'http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com'
    print(get_page(url))
    print(f"URL accessed {get_access_count(url)} times")
