# Mock Stock Game (US) — MVP Spec

## Goal
- 미국 대표 주식으로 모의 주식 게임을 만든다.
- 실제 주가를 10분마다 반영한다(서버가 외부 API에서 가져와 캐시).
- 플레이어는 1,000,000원(₩1,000,000) 기본금으로 시작한다.
- 랭킹 시스템(총자산 기준)으로 다른 사람의 돈(총자산)을 볼 수 있다.
- 총자산이 많은 순으로 등수를 매긴다.

---

## Core Rules
### Assets
- Universe: US large-cap tickers (default 20~50)
- Default tickers (sample 20):
  AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA,
  JPM, BAC, V, MA, BRK.B, UNH,
  JNJ, PG, KO, PEP, COST,
  XOM, DIS

### Price Updates
- Source: Twelve Data (multi-symbol quote)
- Update interval: every 10 minutes
- Game uses latest cached prices only (no per-user external calls)

### Trading
- Order type (MVP): Market order only
- Execution price: latest cached price at order time
- Quantity: integer shares
- No short selling (MVP)
- Prevent invalid orders:
  - Buy: cash must be enough
  - Sell: holdings must be enough
- Optional (recommended): trading fee 0.05% applied on each trade

### Portfolio & Ranking
- Total Equity (총자산):
  cash + sum(qty(symbol) * latest_price(symbol))
- Ranking: total_equity desc
- Tie-breaker: higher cash, then earlier updated_at

---

## Pages / Screens (Frontend)
### 1) Login / Join
- Nickname setup
- Basic auth (email/password or anonymous token for MVP)
- On create user: set cash = 1,000,000 KRW

### 2) Market (Stock List)
- Search box
- List rows:
  - symbol, company name (optional), latest price (USD), 10-min updated timestamp
  - 10-min change (optional)
- Click symbol -> Stock Detail

### 3) Stock Detail
- Symbol header + current cached price
- Mini chart (optional in MVP)
- Trade panel:
  - Buy/Sell
  - Quantity input
  - Estimated cost/proceeds
  - Submit order -> show toast "executed"

### 4) Portfolio
- Cash (KRW)
- Holdings table:
  - symbol, qty, avg_cost(USD), latest_price(USD), market_value(USD), pnl (optional)
- Total equity (KRW) + overall return (optional)

### 5) Leaderboard
- Rank list:
  - rank, nickname, total_equity(KRW), return %
- Show top N (e.g., 50) + "my rank" pinned
- Clicking a user (optional):
  - show only total_equity, cash, top holdings summary (privacy-friendly)

### 6) Admin (optional)
- Manage tickers list
- Force refresh prices

---

## API Requirements (Backend)
### Auth/User
- POST /auth/register {nickname, email?, password?}
- POST /auth/login
- GET /me

### Market/Prices
- GET /tickers
- GET /prices/latest?symbols=AAPL,MSFT,...
- GET /prices/snapshot (all cached)

### Trading
- POST /orders {symbol, side, qty}
- GET /orders/mine

### Portfolio
- GET /portfolio (cash + holdings + total_equity)

### Leaderboard
- GET /leaderboard?limit=50
- GET /leaderboard/me (rank + total_equity)

---

## Non-functional
- External price calls must be server-side only.
- Cache prices in Redis; persist snapshots in DB (optional but recommended).
- Rate limit orders per user (e.g., 10/min) to prevent spam.
