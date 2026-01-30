from pydantic import BaseModel
from typing import Literal, List
from uuid import UUID
from datetime import datetime

class OrderCreate(BaseModel):
    symbol: str
    qty: int
    side: Literal['BUY', 'SELL']
    order_type: Literal['MARKET'] = 'MARKET'

class OrderResponse(BaseModel):
    id: UUID
    status: str
    filled_price: float
    filled_qty: int
    fee: int
    timestamp: datetime

class HoldingSchema(BaseModel):
    symbol: str
    qty: int
    avg_cost_usd: float
    current_price_usd: float
    market_value_krw: int
    return_pct: float

class PortfolioResponse(BaseModel):
    cash_krw: int
    total_equity_krw: int
    holdings: List[HoldingSchema]
