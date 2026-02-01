from functools import wraps
from datetime import datetime, timedelta
import asyncio
from fastapi import Request
import weakref

# ⚡ Bolt: Create a thread-safe, in-memory cache and a reusable decorator.
# This avoids duplicating caching logic across multiple endpoints.
cache = {}

# ⚡ Bolt: Use a WeakValueDictionary for locks to provide granular, per-key locking
# while avoiding memory leaks. Locks are automatically removed when no longer in use.
# This prevents the "thundering herd" problem for a single key while allowing
# concurrent processing of different keys.
locks = weakref.WeakValueDictionary()

# ⚡ Bolt: Restored the module-level lock for backward compatibility.
cache_lock = asyncio.Lock()

def async_cache(ttl: timedelta):
    """
    A decorator for caching the results of an async function in memory.

    Args:
        ttl (timedelta): The time-to-live for the cache entry.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # ⚡ Bolt: Generate a stable cache key by excluding the Request object
            # from both args and kwargs, as it's unique for each call.
            filtered_args = [arg for arg in args if not isinstance(arg, Request)]
            filtered_kwargs = {
                k: v for k, v in kwargs.items() if not isinstance(v, Request)
            }
            # Sort kwargs to ensure the key is consistent.
            sorted_kwargs = sorted(filtered_kwargs.items())
            cache_key = f"{func.__name__}:{filtered_args}:{sorted_kwargs}"
            now = datetime.now()

            # ⚡ Bolt: Fast path - check if a valid cache entry exists without locking.
            cache_entry = cache.get(cache_key)
            if cache_entry and (now - cache_entry["timestamp"]) < ttl:
                return cache_entry["data"]

            # ⚡ Bolt: Get or create a lock for this specific cache key.
            # In asyncio, this sequence is atomic as it contains no 'await' points.
            lock = locks.get(cache_key)
            if lock is None:
                lock = asyncio.Lock()
                locks[cache_key] = lock

            # ⚡ Bolt: Use the granular lock to prevent redundant work for this key.
            async with lock:
                # Double-check the cache in case it was populated while waiting for the lock
                cache_entry = cache.get(cache_key)
                if cache_entry and (datetime.now() - cache_entry["timestamp"]) < ttl:
                    return cache_entry["data"]

                # Execute the function and cache the result
                result = await func(*args, **kwargs)
                cache[cache_key] = {"timestamp": datetime.now(), "data": result}
                return result
        return wrapper
    return decorator
