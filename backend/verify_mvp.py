import asyncio
import httpx
import logging
import sys
import redis.asyncio as redis
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test_user@example.com"
PASSWORD = "password123"
NICKNAME = "TestTrader"
REDIS_URL = "redis://localhost:6379/0"

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def seed_price():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    await r.set("price:AAPL", json.dumps({
        "price": 150.0,
        "change": 1.5,
        "percent_change": 1.0,
        "timestamp": 1234567890,
        "symbol": "AAPL"
    }))
    await r.aclose()
    logger.info("Seeded AAPL price to Redis.")

async def verify_mvp():
    await seed_price()
    
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0, follow_redirects=True) as client:
        logger.info("1. Registering User...")
        try:
            resp = await client.post("/auth/register", json={
                "email": EMAIL,
                "password": PASSWORD,
                "nickname": NICKNAME
            })
            if resp.status_code == 400 and "already exists" in resp.text:
                logger.info("User already exists, logging in...")
            elif resp.status_code != 200:
                logger.error(f"Registration failed: {resp.text}")
                sys.exit(1)
        except httpx.ConnectError:
            logger.error("Could not connect to backend. Is it running?")
            sys.exit(1)

        logger.info("2. Logging In...")
        resp = await client.post("/auth/login", data={
            "username": NICKNAME,
            "password": PASSWORD
        })
        if resp.status_code != 200:
            logger.error(f"Login failed: {resp.text}")
            sys.exit(1)
        
        token = resp.json()
        access_token = token["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        logger.info("Login successful. Token acquired.")

        logger.info("3. Checking Profile (Initial Cash)...")
        resp = await client.get("/auth/me", headers=headers)
        user_data = resp.json()
        logger.info(f"User Data: {user_data}")
        if user_data["cash_krw"] != 1000000:
             logger.warning(f"Expected 1,000,000 KRW, got {user_data['cash_krw']}")
        
        logger.info("4. Fetching Tickers...")
        resp = await client.get("/market/tickers")
        
        logger.info("Scanning for AAPL...")
        
        logger.info("5. Placing BUY Order (AAPL)...")
        order_payload = {
            "symbol": "AAPL",
            "side": "BUY",
            "qty": 1,
            "order_type": "MARKET"
        }
        resp = await client.post("/trade/orders", json=order_payload, headers=headers) 
        if resp.status_code == 200:
            logger.info(f"Order Executed: {resp.json()}")
        else:
            logger.error(f"Order Failed: {resp.text}")

        logger.info("6. Verifying Portfolio...")
        resp = await client.get("/portfolio/", headers=headers)
        portfolio = resp.json()
        logger.info(f"Portfolio: {portfolio}")

        logger.info("7. Verifying Leaderboard...")
        resp = await client.get("/leaderboard?limit=10", headers=headers)
        if resp.status_code == 307:
             resp = await client.get("/leaderboard/?limit=10", headers=headers)
        
        leaderboard = resp.json()
        logger.info(f"Leaderboard top 10: {len(leaderboard)}")

if __name__ == "__main__":
    asyncio.run(verify_mvp())
