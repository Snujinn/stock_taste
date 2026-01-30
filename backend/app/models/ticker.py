from sqlalchemy import Column, String, Boolean
from app.core.database import Base

class Ticker(Base):
    __tablename__ = "tickers"

    symbol = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
