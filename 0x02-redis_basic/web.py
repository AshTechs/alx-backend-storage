#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import redis
import requests


redis_store = redis.Redis()
'''The module-level Redis instance.
'''


def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    # Increment the access count for the URL
    redis_store.incr(f'count:{url}')
    
    # Check if the result is already cached
    cached_result = redis_store.get(f'result:{url}')
    if cached_result:
        return cached_result.decode('utf-8')
    
    # Fetch the content from the URL
    response = requests.get(url)
    result = response.text
    
    # Cache the result with a 10-second expiration
    redis_store.setex(f'result:{url}', 10, result)
    
    return result

# Example usage:
if __name__ == '__main__':
    url = 'http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.example.com'
    print(get_page(url))
    print(get_page(url))  # This call should return the cached result
    print(redis_store.get(f'count:{url}').decode('utf-8'))  # Should print the number of times the URL was accessed
