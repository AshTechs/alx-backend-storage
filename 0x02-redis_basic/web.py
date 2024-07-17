#!/usr/bin/env python3
import requests
import redis

# Connect to Redis
r = redis.Redis()

class CacheManager:
    """Class to manage caching and counting of URL accesses."""
    
    def __init__(self, expiration: int):
        self.expiration = expiration

    def get_page(self, url: str) -> str:
        """Fetch the HTML content of a URL and cache it."""
        cache_key = f"count:{url}"
        # Increment the access count
        r.incr(cache_key)
        # Check if the result is cached
        cached_result = r.get(url)
        if cached_result:
            return cached_result.decode('utf-8')
        # Fetch the result and cache it
        response = requests.get(url)
        result = response.text
        r.setex(url, self.expiration, result)
        return result

# Example usage
if __name__ == "__main__":
    cache_manager = CacheManager(10)
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    print(cache_manager.get_page(url))
    print(cache_manager.get_page(url))
    print(cache_manager.get_page(url))
