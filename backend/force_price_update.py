import asyncio
import logging
from app.services.price_updater import update_prices

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Forcing price update (Finnhub)...")
    asyncio.run(update_prices())
    print("Done.")
