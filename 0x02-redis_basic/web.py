#!/usr/bin/env python3
"""
Module web.py for fetching and caching HTML content from URLs using Redis.
"""

import requests
import redis
import functools
from typing import Callable, Optional

# Redis connection
redis_client = redis.Redis()

def cache_page(url: str, expiration: int = 10) -> Callable:
    """
    Decorator to cache the HTML content of a URL with expiration time.

    Args:
        url (str): The URL to cache.
        expiration (int, optional): Expiration time in seconds. Defaults to 10.

    Returns:
        Callable: Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[str]:
            cached_html_key = f"html:{url}"

            # Check Redis cache for stored HTML
            cached_html = redis_client.get(cached_html_key)
            if cached_html:
                # Return cached HTML if available
                return cached_html.decode('utf-8')

            # Call the original function
            html_content = func(*args, **kwargs)

            # Cache the HTML content with expiration time
            redis_client.setex(cached_html_key, expiration, html_content)

            return html_content
        return wrapper
    return decorator

def count_accesses(url: str) -> Callable:
    """
    Decorator to count the number of accesses to a URL.

    Args:
        url (str): The URL to count accesses for.

    Returns:
        Callable: Decorator function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[str]:
            access_count_key = f"count:{url}"

            # Increment access count for the URL
            redis_client.incr(access_count_key)

            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

@cache_page(url="http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com")
@count_accesses(url="http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com")
def get_page(url: str) -> Optional[str]:
    """
    Retrieve HTML content from a URL.

    Args:
        url (str): The URL to fetch HTML content from.

    Returns:
        Optional[str]: The HTML content of the URL or None if request fails.
    """
    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch URL: {url}, Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    html_content = get_page("http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com")
    if html_content:
        print(html_content)
    else:
        print("Failed to fetch HTML")
