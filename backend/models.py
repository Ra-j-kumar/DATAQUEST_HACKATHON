from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime, timezone

class TickerOverview(Base):
    __tablename__ = "ticker_overview"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)  # Base symbol (e.g., "AAPL")
    market = Column(String, index=True)  # Market type (e.g., "US", "INDIA", "CRYPTO")
    full_symbol = Column(String)  # Full symbol (e.g., "AAPL", "RELIANCE.NS", "BTC-USD")
    name = Column(String)
    price = Column(Float)
    change = Column(Float)
    changePercent = Column(Float)
    marketCap = Column(Float)
    currency = Column(String, default="USD")
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "market": self.market,
            "full_symbol": self.full_symbol,
            "name": self.name,
            "price": self.price,
            "change": self.change,
            "changePercent": self.changePercent,
            "marketCap": self.marketCap,
            "currency": self.currency
        }