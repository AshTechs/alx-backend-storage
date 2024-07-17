#!/usr/bin/env python3
import uuid
from typing import Any, Callable, List, Tuple

class Cache:
    """Cache class to store values with unique keys."""
    
    def __init__(self):
        self.data = {}
        self.call_history = []

    def store(self, value: Any) -> str:
        """Store a value and return a unique key."""
        key = str(uuid.uuid4())
        self.data[key] = value
        self.call_history.append((value, key))
        return key

def replay(func: Callable[..., Any]) -> None:
    """Display the history of calls of a particular function."""
    if not hasattr(func, 'call_history'):
        print(f"{func.__name__} has no call history.")
        return

    call_history: List[Tuple[Any, str]] = func.call_history
    print(f"{func.__name__} was called {len(call_history)} times:")
    for value, key in call_history:
        print(f"{func.__name__}(*({value!r},)) -> {key}")

# Example usage
if __name__ == "__main__":
    cache = Cache()
    cache.store("foo")
    cache.store("bar")
    cache.store(42)
    replay(cache.store)
