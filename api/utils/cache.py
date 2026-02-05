import asyncio
import functools
import logging
import weakref
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

def async_cache(ttl: timedelta = timedelta(minutes=5)):
    """
    Thread-safe asynchronous caching decorator with thundering herd prevention.

    This decorator caches the results of asynchronous functions in memory.
    It uses a per-key locking mechanism to ensure that if multiple concurrent
    requests for the same uncached key arrive, only one execution of the
    underlying function is performed, while others wait for the result.

    Args:
        ttl (timedelta): Time-to-live for the cached results.
    """
    # In-memory storage for cache: {key: (result, expiry_timestamp)}
    _cache: Dict[Tuple, Tuple[Any, datetime]] = {}

    # Per-key locks to prevent thundering herds
    # WeakValueDictionary ensures locks are garbage collected when not in use
    _locks = weakref.WeakValueDictionary()

    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate a cache key. We include all args and kwargs to ensure
            # unique cache entries for different instances or parameters.

            # Simple hashable key generation
            try:
                # We try to use the raw args and kwargs
                cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))
                hash(cache_key)
            except TypeError:
                # Fallback: if arguments are not hashable (e.g. lists, dicts),
                # we use their string representation.
                cache_key = (func.__name__, str(args), str(sorted(kwargs.items())))

            # 1. Check if value is in cache and still valid (Fast path)
            if cache_key in _cache:
                result, expiry = _cache[cache_key]
                if datetime.now() < expiry:
                    return result
                else:
                    # Clear expired entry
                    _cache.pop(cache_key, None)

            # 2. Acquire a lock for this specific key to prevent thundering herd
            lock = _locks.get(cache_key)
            if lock is None:
                lock = asyncio.Lock()
                _locks[cache_key] = lock

            async with lock:
                # 3. Double-check cache after acquiring lock
                if cache_key in _cache:
                    result, expiry = _cache[cache_key]
                    if datetime.now() < expiry:
                        return result

                # 4. Perform the actual (slow) operation
                try:
                    logger.debug(f"Cache miss for {func.__name__}. Executing...")
                    result = await func(*args, **kwargs)

                    # 5. Store in cache with expiry
                    _cache[cache_key] = (result, datetime.now() + ttl)
                    return result
                except Exception as e:
                    logger.error(f"Error in cached function {func.__name__}: {e}")
                    raise

        return wrapper
    return decorator
