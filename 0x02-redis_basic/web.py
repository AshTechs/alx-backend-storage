#!/usr/bin/env python3
"""
requests module to obtain the HTML content of a particular URL and returns it.
"""
import redis
import requests
from typing import Callable
from functools import wraps


cache_client = redis.Redis()
""" module-level REDIS instance"""


def cache_data(func: Callable) -> Callable:
    """ caches the fetched data output"""
    @wraps(func)
    def output_cacher(url: str) -> str:
        """ Wrapper function to cache output """
        cache_client.incr(f'count:{url}')
        cached_page = cache_client.get(f'{url}')
        if cached_page:
            return cached_page.decode('utf-8')
        cache_client.set(f'count:{url}', 0)
        cache_client.setex(f'func(url):{url}', 10, func(url))
        return func(url)
    return output_cacher


@cache_data
def get_page(url: str) -> str:
    """tracks request and returns it;s URL's contents after caching its respnse"""
    return requests.get(url).text
