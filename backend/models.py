from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime, timezone

class TickerOverview(Base):
    __tablename__ = "ticker_overview"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    change = Column(Float)
    changePercent = Column(Float)
    marketCap = Column(Float)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "changePercent": self.changePercent,
            "marketCap": self.marketCap
        }
        
'''
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from database import Base
from datetime import datetime, timezone
import enum

class MarketType(enum.Enum):
    US_STOCK = "us_stock"
    IN_STOCK = "in_stock"  # Indian stock
    CRYPTO = "crypto"

class TickerOverview(Base):
    __tablename__ = "ticker_overview"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    price = Column(Float)
    change = Column(Float)
    changePercent = Column(Float)
    marketCap = Column(Float)
    market = Column(Enum(MarketType))  # New field for market type
    currency = Column(String, default="USD")
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "changePercent": self.changePercent,
            "marketCap": self.marketCap,
            "market": self.market.value if self.market else None,
            "currency": self.currency
        }
'''