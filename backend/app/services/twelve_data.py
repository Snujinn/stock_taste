import httpx
from app.core.config import settings

BASE_URL = "https://api.twelvedata.com/quote"

async def fetch_prices(symbols: list[str]) -> dict:
    if not settings.TWELVEDATA_API_KEY:
        raise ValueError("TWELVEDATA_API_KEY is not set.")

    symbol_str = ",".join(symbols)
    params = {
        "symbol": symbol_str,
        "apikey": settings.TWELVEDATA_API_KEY
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
    # API Error check
    if "code" in data and data["code"] != 200:
        raise Exception(f"Twelve Data API Error: {data.get('message')}")

    # Standardize output for single symbol case
    if len(symbols) == 1 and "symbol" in data:
         return {data["symbol"]: data}
    
    return data
