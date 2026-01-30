from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core import database
from app.models.user import User
from app.schemas import trade as trade_schemas
from app.api import deps
from app.services import trading

router = APIRouter()

@router.post("/orders", response_model=trade_schemas.OrderResponse)
async def create_order(
    order_in: trade_schemas.OrderCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(database.get_db)
) -> Any:
    return await trading.execute_order(db, current_user, order_in)
