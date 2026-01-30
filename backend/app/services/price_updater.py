import logging
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ticker import Ticker
from app.services import finnhub_client
from app.services import leaderboard
from app.core.config import settings
import redis.asyncio as redis
import json

logger = logging.getLogger(__name__)

async def update_prices():
    logger.info("Starting price update (Finnhub)...")
    db = SessionLocal()
    
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    try:
        # Get active tickers
        tickers = db.query(Ticker).filter(Ticker.is_active == True).all()
        symbols = [t.symbol for t in tickers]
        if not symbols:
            logger.warning("No active tickers to update.")
            return

        # Fetch from Finnhub
        try:
            data = await finnhub_client.fetch_prices(symbols)
        except Exception as e:
            logger.error(f"Failed to fetch prices: {e}")
            return

        # Update Redis
        count = 0
        for symbol, quote in data.items():
            # finnhub_client already standardizes the output
            await r.set(f"price:{symbol}", json.dumps(quote), ex=700)
            count += 1
            count += 1
            
        logger.info(f"Updated prices for {count} symbols.")
        
        # Update Leaderboard
        await leaderboard.update_leaderboard(db)

    except Exception as e:
        logger.error(f"Error in price update job: {e}")
    finally:
        db.close()
        await r.aclose()
