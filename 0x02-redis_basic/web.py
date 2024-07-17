#!/usr/bin/env python3
import requests
import redis
from typing import Callable
from functools import wraps

# Connect to Redis
r = redis.Redis()

def cache_with_expiration(expiration: int):
    """Decorator to cache function results with an expiration time."""
    def decorator(func: Callable[..., str]) -> Callable[..., str]:
        @wraps(func)
        def wrapper(url: str) -> str:
            cache_key = f"count:{url}"
            # Increment the access count
            r.incr(cache_key)
            # Check if the result is cached
            cached_result = r.get(url)
            if cached_result:
                return cached_result.decode('utf-8')
            # Fetch the result and cache it
            result = func(url)
            r.setex(url, expiration, result)
            return result
        return wrapper
    return decorator

@cache_with_expiration(10)
def get_page(url: str) -> str:
    """Fetch the HTML content of a URL."""
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(get_page(url))
    print(get_page(url))
    print(get_page(url))
