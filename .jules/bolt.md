## 2025-01-30 - Granular Locking for Async Cache

**Learning:** Using a single global `asyncio.Lock` in a caching decorator serializes ALL cache-miss processing across the entire application. This negates the benefits of `asyncio.gather` for independent tasks that happen to miss the cache simultaneously.

**Action:** Implement granular, per-key locking using `weakref.WeakValueDictionary` to manage `asyncio.Lock` objects. This allows concurrent processing for different keys while still preventing redundant work for the same key, without causing memory leaks from an ever-growing lock dictionary.
