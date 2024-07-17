#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests
from functools import wraps
from typing import Callable


class Cache:
    '''A class to handle caching and tracking of requests.
    '''
    def __init__(self):
        self.redis_store = redis.Redis()

    def data_cacher(self, method: Callable) -> Callable:
        '''Caches the output of fetched data.
        '''
        @wraps(method)
        def invoker(url) -> str:
            '''The wrapper function for caching the output.
            '''
            self.redis_store.incr(f'count:{url}')
            result = self.redis_store.get(f'result:{url}')
            if result:
                return result.decode('utf-8')
            result = method(url)
            self.redis_store.setex(f'result:{url}', 10, result)
            return result
        return invoker

    def get_count(self, url: str) -> int:
        '''Returns the count of how many times a URL was accessed.
        '''
        count = self.redis_store.get(f'count:{url}')
        return int(count) if count else 0


cache = Cache()

@cache.data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text


if __name__ == '__main__':
    # Example usage
    url = 'http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com'
    print(get_page(url))
    print(f"URL accessed {cache.get_count(url)} times")
