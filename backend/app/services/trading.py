from sqlalchemy.orm import Session
from app.models.user import User
from app.models.order import Order, Fill
from app.models.holding import Holding
from app.schemas.trade import OrderCreate, OrderResponse
import redis.asyncio as redis
from app.core.config import settings
import json
from fastapi import HTTPException

FX_RATE = 1300

async def execute_order(db: Session, user: User, order_in: OrderCreate) -> OrderResponse:
    # 1. Get Price
    r = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        price_data = await r.get(f"price:{order_in.symbol}")
    finally:
        await r.aclose()
    
    if not price_data:
        raise HTTPException(status_code=400, detail="Price not available for symbol (or market closed/initializing)")
    
    price_info = json.loads(price_data)
    price_usd = float(price_info['price'])
    price_krw = price_usd * FX_RATE
    
    total_cost_krw = int(price_krw * order_in.qty)
    # Fee (0.05%)
    fee_krw = int(total_cost_krw * 0.0005)
    
    # 2. Validation
    if order_in.side == 'BUY':
        required_cash = total_cost_krw + fee_krw
        if user.cash_krw < required_cash:
             raise HTTPException(status_code=400, detail=f"Insufficient funds. Need {required_cash:,} KRW, Have {user.cash_krw:,} KRW")
    else:
        # SELL
        holding = db.query(Holding).filter(Holding.user_id == user.id, Holding.symbol == order_in.symbol).first()
        if not holding or holding.qty < order_in.qty:
            raise HTTPException(status_code=400, detail="Insufficient holdings")
            
    # 3. Execution (DB Transaction)
    order = Order(
        user_id=user.id,
        symbol=order_in.symbol,
        side=order_in.side,
        qty=order_in.qty,
        order_type=order_in.order_type,
        status="FILLED"
    )
    db.add(order)
    db.flush()
    
    fill = Fill(
        order_id=order.id,
        price_usd=price_usd,
        qty=order_in.qty,
        fee_krw=fee_krw
    )
    db.add(fill)
    
    # Update Balance and Holdings
    if order_in.side == 'BUY':
        user.cash_krw -= (total_cost_krw + fee_krw)
        
        holding = db.query(Holding).filter(Holding.user_id == user.id, Holding.symbol == order_in.symbol).first()
        if not holding:
            holding = Holding(user_id=user.id, symbol=order_in.symbol, qty=0, avg_cost_usd=0)
            db.add(holding)
        
        # Weighted Average Cost
        old_cost = float(holding.avg_cost_usd) * holding.qty
        new_cost = price_usd * order_in.qty
        new_qty = holding.qty + order_in.qty
        if new_qty > 0:
            holding.avg_cost_usd = (old_cost + new_cost) / new_qty
        holding.qty = new_qty
        
    else: # SELL
        total_proceeds = total_cost_krw - fee_krw
        user.cash_krw += int(total_proceeds)
        
        holding = db.query(Holding).filter(Holding.user_id == user.id, Holding.symbol == order_in.symbol).first()
        holding.qty -= order_in.qty
        if holding.qty == 0:
            holding.avg_cost_usd = 0
    
    db.commit()
    db.refresh(order)
    
    return OrderResponse(
        id=order.id,
        status="FILLED",
        filled_price=price_usd,
        filled_qty=order_in.qty,
        fee=fee_krw,
        timestamp=order.created_at
    )
