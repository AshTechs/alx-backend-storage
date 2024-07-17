#!/usr/bin/env python3
"""Implement this use case with decorators. """

import requests
import redis
import time
from typing import Optional

# Redis connection
redis_client = redis.Redis()

def get_page(url: str) -> Optional[str]:
    """
    Retrieve HTML content from a URL and cache the result with a 10-second expiration.

    Args:
        url (str): The URL to fetch HTML content from.

    Returns:
        Optional[str]: The HTML content of the URL or None if request fails.
    """
    # Check if the URL has been accessed before
    access_count_key = f"count:{url}"
    cached_html_key = f"html:{url}"

    # Check Redis cache for stored HTML
    cached_html = redis_client.get(cached_html_key)
    if cached_html:
        # Return cached HTML if available
        return cached_html.decode('utf-8')

    try:
        # Fetch HTML content from the URL
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.text

            # Cache the HTML content with expiration time of 10 seconds
            redis_client.setex(cached_html_key, 10, html_content)

            # Increment access count for the URL
            redis_client.incr(access_count_key)

            return html_content
        else:
            print(f"Failed to fetch URL: {url}, Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.example.com"
    html_content = get_page(url)
    if html_content:
        print(html_content)
    else:
        print(f"Failed to fetch HTML from {url}")
