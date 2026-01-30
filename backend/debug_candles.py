import asyncio
import httpx
import time
from app.core.config import settings

async def fetch_candles():
    symbol = "AAPL"
    resolution = "D"
    to_ts = int(time.time())
    from_ts = to_ts - (90 * 24 * 60 * 60)
    
    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_ts,
        "to": to_ts,
        "token": settings.FINNHUB_API_KEY
    }
    print(f"Requesting: {url} with params {params}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_candles())
