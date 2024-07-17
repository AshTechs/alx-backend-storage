#!/usr/bin/env python3
"""Get_page function"""
import requests
import redis
import time
import functools

redis_client = redis.Redis()


def count_accesses(func):
    """
    Decorator to count the number of accesses to a function for each URL.
    """
    @functools.wraps(func)
    def wrapper(url):
        redis_client.incr(f"count:{url}")
        return func(url)
    return wrapper

def cache_content(func):
    """
    Decorator to cache the content of a function with a 10-second expiration time.
    """
    @functools.wraps(func)
    def wrapper(url):
        cached_content = redis_client.get(f"content:{url}")
        if cached_content:
            return cached_content.decode('utf-8')
        content = func(url)
        redis_client.setex(f"content:{url}", 10, content)
        return content
    return wrapper

@count_accesses
@cache_content
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a given URL and caches the result with a 10-second expiration time.

    Args:
        url (str): The URL to fetch HTML content from.

    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.example.com"
    content = get_page(url)
    print(content)
