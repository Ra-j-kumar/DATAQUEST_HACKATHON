'''
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
import random
from models import MarketType

# Import from our new files
from database import get_db, news_collection, engine, SessionLocal    # Fixed import
from models import TickerOverview, Base, MarketType
from ai_processor import generate_insights


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

# NEW ENDPOINT: Get overview from DATABASE
@app.get("/api/ticker/{ticker_id}/overview", response_model=TickerOverviewResponse)
def get_ticker_overview(ticker_id: str, db: Session = Depends(get_db)):
    # Query the TimescaleDB database for the ticker
    db_ticker = db.query(TickerOverview).filter(TickerOverview.symbol == ticker_id.upper()).first()

    if db_ticker is None:
        # If not found in DB, return an error
        raise HTTPException(status_code=404, detail="Ticker not found")
    # Return the data from the database
    return db_ticker

# NEW ENDPOINT: Get news from DATABASE
@app.get("/api/ticker/{ticker_id}/news")
def get_ticker_news(ticker_id: str):
    # Query the MongoDB collection for news related to the ticker
    # Sort by publishedAt descending, and get the top 10
    news_list = list(news_collection.find({"symbol": ticker_id.upper()}).sort("publishedAt", -1).limit(10))
    # MongoDB returns Objects which are not JSON serializable. We need to convert them.
    for news in news_list:
        news["_id"] = str(news["_id"]) # Convert the ObjectId to a string
    return news_list

# Keep the root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Welcome to TickerTracker API! The DB connection is live."}


@app.get("/api/markets")
def get_supported_markets():
    """Get list of all supported markets"""
    return [
        {"id": "us_stock", "name": "US Stock Market", "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]},
        {"id": "in_stock", "name": "Indian Stock Market", "symbols": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]},
        {"id": "crypto", "name": "Cryptocurrency", "symbols": ["BTC", "ETH", "BNB", "ADA", "DOGE"]}
    ]

@app.get("/api/tickers")
def get_all_tickers(market: str = None):
    """Get all tickers, optionally filtered by market"""
    db = SessionLocal()
    try:
        query = db.query(TickerOverview)
        if market:
            query = query.filter(TickerOverview.market == MarketType(market))
        
        tickers = query.all()
        return [ticker.to_dict() for ticker in tickers]
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid market type")
    finally:
        db.close()

@app.get("/api/market/{market_type}/tickers")
def get_market_tickers(market_type: str):
    """Get all tickers for a specific market"""
    try:
        market_enum = MarketType(market_type)
        db = SessionLocal()
        tickers = db.query(TickerOverview).filter(TickerOverview.market == market_enum).all()
        return [ticker.to_dict() for ticker in tickers]
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid market type")
    finally:
        db.close()
'''

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# NEW ENDPOINT: Get overview from DATABASE
@app.get("/api/ticker/{ticker_id}/overview", response_model=TickerOverviewResponse)
def get_ticker_overview(ticker_id: str, db: Session = Depends(get_db)):
    # Query the TimescaleDB database for the ticker
    db_ticker = db.query(TickerOverview).filter(TickerOverview.symbol == ticker_id.upper()).first()

    if db_ticker is None:
        # If not found in DB, return an error
        raise HTTPException(status_code=404, detail="Ticker not found")
    # Return the data from the database
    return db_ticker

# NEW ENDPOINT: Get news from DATABASE
@app.get("/api/ticker/{ticker_id}/news")
def get_ticker_news(ticker_id: str):
    # Query the MongoDB collection for news related to the ticker
    # Sort by publishedAt descending, and get the top 10
    news_list = list(news_collection.find({"symbol": ticker_id.upper()}).sort("publishedAt", -1).limit(10))
    # MongoDB returns Objects which are not JSON serializable. We need to convert them.
    for news in news_list:
        news["_id"] = str(news["_id"]) # Convert the ObjectId to a string
    return news_list

# Keep the root endpoint for testing
@app.get("/")
def read_root():
    return {"message": "Welcome to TickerTracker API! The DB connection is live."}

@app.get("/api/ticker/{ticker_id}/insights")
def get_ticker_insights(ticker_id: str):
    """Get AI-generated insights for a ticker"""
    insights = generate_insights(ticker_id.upper())
    return {"ticker": ticker_id.upper(), "insights": insights}