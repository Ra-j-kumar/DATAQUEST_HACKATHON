from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from market_config import MARKET_CONFIG, POPULAR_TICKERS
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from ai_processor import generate_insights
import random

# Import from our new files
from database import get_db, news_collection, engine  # Fixed import
from models import TickerOverview, Base

# Create tables in the database (if they don't exist)
Base.metadata.create_all(bind=engine)  # Fixed reference

app = FastAPI(title="TickerTracker API", description="API for financial data and insights", version="0.1")
app.add_middleware( CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"] )

# Pydantic model for response
class TickerOverviewResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    marketCap: float

    class Config:
        from_attributes = True # This allows conversion from SQLAlchemy model

# Keep the root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Welcome to TickerTracker API! The DB connection is live."}


# Update the overview endpoint to support markets
@app.get("/api/ticker/{market}/{ticker_id}/overview", response_model=TickerOverviewResponse)
def get_ticker_overview(market: str, ticker_id: str, db: Session = Depends(get_db)):
    # Query the database for the ticker in the specific market
    db_ticker = db.query(TickerOverview).filter(
        TickerOverview.symbol == ticker_id.upper(),
        TickerOverview.market == market.upper()
    ).first()

    if db_ticker is None:
        raise HTTPException(status_code=404, detail="Ticker not found in this market")
    
    return db_ticker

# Update the news endpoint
@app.get("/api/ticker/{market}/{ticker_id}/news")
def get_ticker_news(market: str, ticker_id: str):
    news_list = list(news_collection.find({
        "symbol": ticker_id.upper(),
        "market": market.upper()
    }).sort("publishedAt", -1).limit(10))
    
    for news in news_list:
        news["_id"] = str(news["_id"])
    return news_list

# Update the insights endpoint
@app.get("/api/ticker/{market}/{ticker_id}/insights")
def get_ticker_insights(market: str, ticker_id: str):
    """Get AI-generated insights for a ticker"""
    insights = generate_insights(ticker_id.upper(), market.upper())
    return {"ticker": ticker_id.upper(), "market": market.upper(), "insights": insights}

# Add new endpoint to get popular tickers by market
@app.get("/api/markets/{market}/popular-tickers")
def get_popular_tickers(market: str):
    """Get popular tickers for a specific market"""
    market_upper = market.upper()
    if market_upper in POPULAR_TICKERS:
        return {
            "market": market_upper,
            "tickers": POPULAR_TICKERS[market_upper]
        }
    raise HTTPException(status_code=404, detail="Market not found")

# Add endpoint to get all supported markets
@app.get("/api/markets")
def get_supported_markets():
    """Get all supported markets"""
    return list(MARKET_CONFIG.keys())