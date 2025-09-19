import yfinance as yf
from sqlalchemy.orm import Session
from database import SessionLocal, engine, news_collection
from models import TickerOverview, Base
from datetime import datetime, timezone, timedelta
from ai_processor import analyze_news_sentiment, generate_insights
import requests
import json

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Convert numpy types to Python native types for SQLAlchemy
def convert_numpy_types(data):
    converted = {}
    for key, value in data.items():
        if hasattr(value, 'item'):
            converted[key] = value.item()
        else:
            converted[key] = value
    return converted

# 1. FETCH STOCK PRICE DATA (using yfinance)
def fetch_stock_data(ticker_symbol="AAPL"):
    print(f"Fetching data for {ticker_symbol}...")
    db = SessionLocal()
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        # Try to get more historical data to ensure we have previous close
        history = ticker.history(period="5d")  # Get 5 days to ensure we have data
        
        if history.empty:
            print("No data found for this ticker.")
            return
            
        # Get the last available price
        last_price = history['Close'].iloc[-1]
        
        # Try to get previous close - use the day before if available
        if len(history) > 1:
            prev_close = history['Close'].iloc[-2]
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            # If only one day of data, use the open price as previous close
            prev_close = history['Open'].iloc[-1] if 'Open' in history else last_price
            change = 0
            change_percent = 0
            print(f"Only one day of data available for {ticker_symbol}, using open price as previous close")

        # Prepare data for our TickerOverview model
        overview_data = {
            "symbol": ticker_symbol.upper(),
            "name": info.get('longName', ticker_symbol),
            "price": float(round(last_price, 2)),
            "change": float(round(change, 2)),
            "changePercent": float(round(change_percent, 2)),
            "marketCap": info.get('marketCap', 0)
        }

        # Convert numpy types to Python native types
        overview_data = convert_numpy_types(overview_data)

        # Check if the ticker already exists in the database
        existing_ticker = db.query(TickerOverview).filter(TickerOverview.symbol == ticker_symbol.upper()).first()
        if existing_ticker:
            # Update existing record
            for key, value in overview_data.items():
                setattr(existing_ticker, key, value)
            existing_ticker.last_updated = datetime.now(timezone.utc)
        else:
            # Create a new record
            new_ticker = TickerOverview(**overview_data)
            db.add(new_ticker)
        db.commit()
        print(f"Successfully updated database for {ticker_symbol}: ${overview_data['price']} ({overview_data['changePercent']}%)")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

# 2. FETCH NEWS DATA
def fetch_news_data(ticker_symbol="AAPL"):
    print(f"Fetching news for {ticker_symbol}...")
    
    # Use mock news data since NewsAPI requires a key
    mock_news = [
        {
            "headline": f"{ticker_symbol} Announces New Product Launch",
            "summary": f"{ticker_symbol} has announced a revolutionary new product that is expected to drive growth in the coming quarters.",
            "source": "Financial Times",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-product-launch",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "symbol": ticker_symbol.upper(),
            "sentimentScore": 0.8
        },
        {
            "headline": f"Analysts Upgrade {ticker_symbol} to Buy Rating",
            "summary": f"Leading analysts have upgraded {ticker_symbol} from Hold to Buy based on strong quarterly results and positive outlook.",
            "source": "Wall Street Journal",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-upgrade",
            "publishedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "symbol": ticker_symbol.upper(),
            "sentimentScore": 0.9
        },
        {
            "headline": f"{ticker_symbol} Faces Supply Chain Challenges",
            "summary": f"{ticker_symbol} reported minor supply chain disruptions that may affect Q4 delivery targets.",
            "source": "Bloomberg",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-supply-chain",
            "publishedAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "symbol": ticker_symbol.upper(),
            "sentimentScore": -0.3
        }
    ]
    
    for article in mock_news:
        # Insert into MongoDB. update_one with upsert=True prevents duplicates based on URL.
        news_collection.update_one(
            {"url": article['url']},
            {"$set": article},
            upsert=True
        )
    print(f"Inserted/Updated {len(mock_news)} news articles for {ticker_symbol}")
    
def run_ai_analysis():
    """Run all AI analysis processes"""
    print("Running AI analysis...")
    analyze_news_sentiment()
    
    # Generate insights for all tracked tickers
    for ticker in ["AAPL", "MSFT", "GOOGL"]:
        insights = generate_insights(ticker)
        print(f"Insights for {ticker}: {insights}")
        
if __name__ == "__main__":
    # Run the fetchers
    fetch_stock_data("AAPL")
    fetch_stock_data("MSFT")
    fetch_stock_data("GOOGL")
    fetch_news_data("AAPL")
    fetch_news_data("MSFT")
    fetch_news_data("GOOGL")
    
    run_ai_analysis()
    
    
'''
from market_fetchers import fetch_all_market_data
from ai_processor import run_ai_analysis

def fetch_all_data():
    """Main function to fetch all data"""
    fetch_all_market_data()
    run_ai_analysis()

if __name__ == "__main__":
    fetch_all_data()
'''