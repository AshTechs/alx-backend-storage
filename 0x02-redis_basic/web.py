#!/usr/bin/env python3
import requests
import redis
from typing import Callable

# Connect to Redis
r = redis.Redis()

class CacheWithExpiration:
    """Class-based decorator to cache function results with an expiration time."""
    
    def __init__(self, expiration: int):
        self.expiration = expiration

    def __call__(self, func: Callable[..., str]) -> Callable[..., str]:
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
            r.setex(url, self.expiration, result)
            return result
        return wrapper

@CacheWithExpiration(10)
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
