import asyncio
import redis.asyncio as redis
from app.core.config import settings
import json

async def check_redis():
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        data = await r.get("price:AAPL")
        print(f"price:AAPL = {data}")
    finally:
        await r.aclose()

if __name__ == "__main__":
    asyncio.run(check_redis())
