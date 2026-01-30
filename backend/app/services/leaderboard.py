from sqlalchemy.orm import Session
from app.models.user import User
from app.models.holding import Holding
from app.core.config import settings
import redis.asyncio as redis
import json
import logging

logger = logging.getLogger(__name__)

FX_RATE = 1300

async def update_leaderboard(db: Session):
    logger.info("Updating leaderboard...")
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        # Get all prices
        keys = await r.keys("price:*")
        price_map = {}
        if keys:
            values = await r.mget(keys)
            for k, v in zip(keys, values):
                if v:
                    symbol = k.replace("price:", "")
                    price_map[symbol] = float(json.loads(v)['price'])
        
        # Get all users (optimize later to only active users?)
        # For MVP, iterate all users.
        users = db.query(User).all()
        
        pipeline = r.pipeline()
        
        for user in users:
            # Get holdings
            holdings = db.query(Holding).filter(Holding.user_id == user.id, Holding.qty > 0).all()
            total_equity = float(user.cash_krw)
            
            for h in holdings:
                price = price_map.get(h.symbol, 0)
                # Use avg_cost if price missing? No, 0.
                total_equity += (h.qty * price * FX_RATE)
            
            # Add to Sorted Set
            # ZADD leaderboard score member
            pipeline.zadd("leaderboard", {str(user.id): int(total_equity)})
            # Store nickname
            pipeline.hset("user_nicknames", str(user.id), user.nickname)
            
        await pipeline.execute()
        logger.info(f"Leaderboard updated for {len(users)} users.")
        
    except Exception as e:
        logger.error(f"Leaderboard update failed: {e}")
    finally:
        await r.aclose()
