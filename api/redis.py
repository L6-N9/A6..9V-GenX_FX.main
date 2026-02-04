import redis.asyncio as redis
import os

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

redis_client = None

async def init_redis():
    global redis_client
    try:
        redis_client = await redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        return redis_client
    except Exception:
        redis_client = None
        return None

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
