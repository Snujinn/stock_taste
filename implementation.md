# Implementation Guide — Mock Stock Game (10-min prices, Twelve Data)

## Stack (recommended)
- Frontend: Next.js (App Router)
- Backend: FastAPI
- DB: Postgres
- Cache: Redis
- Scheduler: APScheduler (simple) or Celery Beat (scalable)

---

## Environment Variables
### Backend (.env)
- DATABASE_URL=postgresql+psycopg://...
- REDIS_URL=redis://...
- TWELVEDATA_API_KEY=...
- PRICE_UPDATE_CRON="*/10 * * * *"  (document only; APScheduler uses interval)

---

## Architecture
### Price Service (server-side only)
- Every 10 minutes:
  1) fetch quotes for all tickers in one request (multi-symbol)
  2) store to Redis: price:{SYMBOL} = {price, as_of}
  3) store snapshot to DB (optional): prices table
- Game endpoints only read from Redis (fast) and fallback to DB if cache miss.

### Trading Flow (Market order)
- On POST /orders:
  1) validate symbol exists
  2) get latest price from Redis
  3) compute total cost/proceeds
  4) apply fee (optional)
  5) transaction in DB:
     - update users.cash
     - update holdings qty & avg_cost
     - insert order + fill record
  6) return updated portfolio summary

### Leaderboard
- Compute total_equity using cached prices (Redis) + holdings from DB.
- For scale:
  - compute leaderboard every 10 minutes after price update
  - store ranks in Redis sorted set:
    ZADD leaderboard {total_equity_krw} {user_id}
  - API reads top N quickly.

---

## Data Model (Postgres)
### users
- id (uuid pk)
- nickname (text unique)
- cash_krw (bigint) default 1000000
- created_at, updated_at

### tickers
- symbol (text pk)
- name (text) optional
- is_active (bool) default true

### holdings
- user_id (uuid fk)
- symbol (text fk -> tickers.symbol)
- qty (int) default 0
- avg_cost_usd (numeric) default 0
- updated_at
- pk: (user_id, symbol)

### orders
- id (uuid pk)
- user_id
- symbol
- side ('BUY'|'SELL')
- qty (int)
- order_type ('MARKET') default MARKET
- created_at

### fills
- id (uuid pk)
- order_id (uuid fk)
- price_usd (numeric)
- qty (int)
- fee_krw (bigint) default 0
- filled_at

### price_snapshots (optional but recommended)
- symbol
- price_usd
- as_of (timestamp)
- pk: (symbol, as_of)

### leaderboard_snapshots (optional)
- user_id
- total_equity_krw
- as_of
- rank (int)

---

## Currency Handling
- Prices from US stocks are USD.
- Keep cash in KRW.
- Choose a fixed USDKRW rate for MVP (e.g., 1300) OR fetch FX rate on schedule too.
- Store USDKRW in Redis: fx:USDKRW
- total_equity_krw = cash_krw + Σ(qty * price_usd * fx)

(If you want simplicity: fix fx=1300 in MVP; upgrade later.)

---

## Twelve Data API (multi-symbol quote)
- Endpoint concept:
  GET /quote?symbol=AAPL,MSFT,AMZN&apikey=...
- Parse response into {symbol: price, datetime/as_of}

Implementation notes:
- Some symbols like BRK.B might need mapping per provider (e.g., BRK.B -> BRK.B or BRK-B). Keep a provider_symbol field in tickers if needed.
- Always treat external API as best-effort:
  - if one symbol fails, keep last cached price and log.

---

## Backend Endpoints (FastAPI)
### Auth (MVP-simple)
- POST /auth/register
- POST /auth/login
- GET /me

### Market
- GET /tickers
- GET /prices/snapshot
- GET /prices/latest?symbols=...

### Trading
- POST /orders
- GET /orders/mine

### Portfolio
- GET /portfolio

### Leaderboard
- GET /leaderboard?limit=50
- GET /leaderboard/me

---

## Leaderboard Computation Strategy (recommended)
### After each price update job
1) Load all active tickers prices from Redis into a dict.
2) Fetch all holdings aggregated by user from DB.
3) Compute each user's equity.
4) ZADD into Redis sorted set "leaderboard".
5) Also store user_equity:{user_id} = equity_krw for quick /me.

Read:
- Top N: ZREVRANGE leaderboard 0 N-1 WITHSCORES
- My rank: ZREVRANK leaderboard {user_id}

---

## Frontend (Next.js) Pages
- /login
- /market
- /stock/[symbol]
- /portfolio
- /leaderboard

State updates:
- Poll backend every 30~60s for prices/leaderboard (UI만) — 실제 가격 업데이트는 10분이라 과한 폴링 필요 없음.
- Show "last updated at" timestamp.

---

## MVP Add-ons (recommended)
- Trading fee 0.05% (fee_krw = round(cost_krw * 0.0005))
- Order rate limit (per user)
- Season reset (manual)
- Friend league (later)

---

## Milestones
1) DB schema + auth + tickers seed
2) Price updater job (10-min) + Redis cache
3) Market list + detail page showing cached price
4) Trading + portfolio valuation
5) Leaderboard (Redis sorted set) + UI
6) Add fee + rate limit + polish
