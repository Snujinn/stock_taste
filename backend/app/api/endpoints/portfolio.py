from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import database
from app.models.user import User
from app.models.holding import Holding
from app.schemas import trade as trade_schemas
from app.api import deps
from app.core.config import settings
import redis.asyncio as redis
import json

router = APIRouter()

FX_RATE = 1300

@router.get("/", response_model=trade_schemas.PortfolioResponse)
async def get_portfolio(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(database.get_db)
) -> Any:
    holdings = db.query(Holding).filter(Holding.user_id == current_user.id, Holding.qty > 0).all()
    
    # Fetch current prices
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    portfolio_holdings = []
    total_equity = current_user.cash_krw
    
    try:
        keys = [f"price:{h.symbol}" for h in holdings]
        if keys:
            values = await r.mget(keys)
            price_map = {k.replace("price:", ""): v for k, v in zip(keys, values) if v}
        else:
            price_map = {}
            
        for h in holdings:
            current_price_data = price_map.get(h.symbol)
            current_price = 0.0
            if current_price_data:
                current_price = float(json.loads(current_price_data)['price'])
            
            market_value_krw = int(h.qty * current_price * FX_RATE)
            total_equity += market_value_krw
            
            # ROI
            avg_cost = float(h.avg_cost_usd)
            ret = 0.0
            if avg_cost > 0:
                ret = (current_price - avg_cost) / avg_cost * 100
                
            portfolio_holdings.append(trade_schemas.HoldingSchema(
                symbol=h.symbol,
                qty=h.qty,
                avg_cost_usd=avg_cost,
                current_price_usd=current_price,
                market_value_krw=market_value_krw,
                return_pct=ret
            ))
            
    finally:
         await r.aclose()

    return {
        "cash_krw": current_user.cash_krw,
        "total_equity_krw": total_equity,
        "holdings": portfolio_holdings
    }
