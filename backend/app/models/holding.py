from sqlalchemy import Column, String, Integer, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Holding(Base):
    __tablename__ = "holdings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    symbol = Column(String, ForeignKey("tickers.symbol"), primary_key=True)
    qty = Column(Integer, default=0)
    avg_cost_usd = Column(Numeric, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
