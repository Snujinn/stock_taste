import httpx
import asyncio
from app.core.config import settings

BASE_URL = "https://finnhub.io/api/v1/quote"

async def fetch_prices(symbols: list[str]) -> dict:
    if not settings.FINNHUB_API_KEY:
        raise ValueError("FINNHUB_API_KEY is not set.")

    async def fetch_one(symbol):
        params = {"symbol": symbol, "token": settings.FINNHUB_API_KEY}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                # Finnhub returns {'c': current_price, 'd': change, 'dp': percent_change ...}
                # If symbol invalid, it might return 0s.
                return symbol, data
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                return symbol, None

    # Finnhub doesn't support batch quote, so we parallelize
    results = await asyncio.gather(*[fetch_one(s) for s in symbols])
    
    price_map = {}
    for symbol, data in results:
        if data and data.get("c", 0) > 0:
            price_map[symbol] = {
                "price": data["c"],
                "change": data["d"],
                "percent_change": data["dp"],
                "timestamp": data["t"], # Unix timestamp
                "symbol": symbol 
            }
            
    return price_map

async def fetch_candles(symbol: str, resolution: str, from_ts: int, to_ts: int) -> dict:
    url = "https://finnhub.io/api/v1/stock/candle"
    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": from_ts,
        "to": to_ts,
        "token": settings.FINNHUB_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching candles for {symbol}: {e}")
            return {}
