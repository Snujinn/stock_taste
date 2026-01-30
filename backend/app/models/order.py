from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, func, BigInteger
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    symbol = Column(String, ForeignKey("tickers.symbol"))
    side = Column(String) # BUY, SELL
    qty = Column(Integer)
    order_type = Column(String, default="MARKET")
    status = Column(String, default="FILLED") 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Fill(Base):
    __tablename__ = "fills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    price_usd = Column(Numeric)
    qty = Column(Integer)
    fee_krw = Column(BigInteger, default=0)
    filled_at = Column(DateTime(timezone=True), server_default=func.now())
