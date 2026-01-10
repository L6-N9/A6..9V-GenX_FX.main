from datetime import datetime, timedelta

# ⚡ Bolt: A simple in-memory cache to store frequently accessed data.
# This avoids expensive operations, like database queries, on every request.
_cache = {}
_DEFAULT_TTL = 300  # 5 minutes

def set(key: str, value, ttl: int = _DEFAULT_TTL):
    """
    Stores a value in the cache with a specific time-to-live (TTL).

    Args:
        key: The key to store the value under.
        value: The value to be cached.
        ttl: The time-to-live in seconds.
    """
    # ⚡ Bolt: Caching with a clear expiration time prevents stale data.
    expires_at = datetime.now() + timedelta(seconds=ttl)
    _cache[key] = {"value": value, "expires_at": expires_at}

def get(key: str):
    """
    Retrieves a value from the cache if it exists and has not expired.

    Args:
        key: The key of the value to retrieve.

    Returns:
        The cached value if it's valid, otherwise None.
    """
    item = _cache.get(key)
    if item and datetime.now() < item["expires_at"]:
        # ⚡ Bolt: Cache hit! Serving data from memory is much faster.
        return item["value"]
    # ⚡ Bolt: Cache miss or expired. The application will need to fetch fresh data.
    return None

def clear():
    """
    Clears the entire cache.
    """
    _cache.clear()
