from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import database
from app.models.ticker import Ticker
from app.core.config import settings
import redis.asyncio as redis
import json

router = APIRouter()

@router.get("/tickers")
def get_tickers(db: Session = Depends(database.get_db)) -> Any:
    tickers = db.query(Ticker).filter(Ticker.is_active == True).all()
    return [{"symbol": t.symbol, "name": t.name} for t in tickers]

@router.get("/prices")
async def get_prices() -> Any:
    # return all cached prices
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        keys = await r.keys("price:*")
        if not keys:
            return {}
        
        values = await r.mget(keys)
        # Map back to clean dict
        result = {}
        for k, v in zip(keys, values):
            if v:
                symbol = k.replace("price:", "")
                result[symbol] = json.loads(v)
        return result
    finally:
        await r.aclose()

@router.get("/prices/{symbol}")
async def get_price(symbol: str) -> Any:
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        data = await r.get(f"price:{symbol.upper()}")
        if not data:
             return {}
        return json.loads(data)
    finally:
        await r.aclose()

@router.get("/history/{symbol}")
async def get_history(symbol: str, resolution: str = "D", from_ts: int = None, to_ts: int = None) -> Any:
    # Use yfinance for history as it's more reliable for free tier
    import yfinance as yf
    from datetime import datetime
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Determine period or start/end
        if from_ts and to_ts:
            start_date = datetime.fromtimestamp(from_ts).strftime('%Y-%m-%d')
            end_date = datetime.fromtimestamp(to_ts).strftime('%Y-%m-%d')
            hist = ticker.history(start=start_date, end=end_date)
        else:
            # Default to 3 months if no range specified
             hist = ticker.history(period="3mo")
        
        # Format for frontend: [{date: ts, price: close}, ...]
        result = []
        for date, row in hist.iterrows():
            result.append({
                "time": int(date.timestamp()),
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
            })
        return result
    except Exception as e:
        print(f"Error fetching history for {symbol}: {e}")
        return []
