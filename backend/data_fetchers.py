# Update the fetch_stock_data function to accept market parameter
import yfinance as yf
from sqlalchemy.orm import Session
from database import SessionLocal, engine, news_collection
from models import TickerOverview, Base
from datetime import datetime, timezone, timedelta
import requests
import numpy as np
from market_config import MARKET_CONFIG, POPULAR_TICKERS, get_full_symbol
from ai_processor import analyze_news_sentiment, generate_insights

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
def fetch_stock_data(ticker_symbol="AAPL", market="US"):
    print(f"Fetching data for {ticker_symbol} ({market})...")
    
    # Convert to full symbol for the market
    full_symbol = get_full_symbol(ticker_symbol, market)
    
    db = SessionLocal()
    try:
        ticker = yf.Ticker(full_symbol)
        info = ticker.info
        history = ticker.history(period="2d")  # Get 2 days to calculate change

        if history.empty or len(history) < 1:
            print(f"No data found for {full_symbol}")
            return

        # Get the last available price
        last_price = history['Close'].iloc[-1]
        
        # Calculate change from previous close if available
        if len(history) > 1:
            prev_close = history['Close'].iloc[-2]
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            # If only one day of data, use open price or set to 0
            prev_close = history['Open'].iloc[-1] if 'Open' in history else last_price
            change = last_price - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0

        # Prepare data for our TickerOverview model
        overview_data = {
            "symbol": ticker_symbol.upper(),
            "market": market,
            "full_symbol": full_symbol,
            "name": info.get('longName', ticker_symbol),
            "price": float(round(last_price, 2)),
            "change": float(round(change, 2)),
            "changePercent": float(round(change_percent, 2)),
            "marketCap": info.get('marketCap', 0),
            "currency": MARKET_CONFIG[market]["currency"]
        }

        # Convert numpy types to Python native types
        overview_data = convert_numpy_types(overview_data)

        # Check if the ticker already exists in the database
        existing_ticker = db.query(TickerOverview).filter(
            TickerOverview.symbol == ticker_symbol.upper(),
            TickerOverview.market == market
        ).first()
        
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
        print(f"Successfully updated {market} database for {ticker_symbol}: ${overview_data['price']} ({overview_data['changePercent']}%)")

    except Exception as e:
        print(f"An error occurred fetching {full_symbol}: {e}")
        db.rollback()
    finally:
        db.close()

# 2. FETCH NEWS DATA
def fetch_news_data(ticker_symbol="AAPL", market="US"):
    print(f"Fetching news for {ticker_symbol} ({market})...")
    
    # Use mock news data since NewsAPI requires a key
    mock_news = [
        {
            "headline": f"{ticker_symbol} Announces New Product Launch",
            "summary": f"{ticker_symbol} has announced a revolutionary new product that is expected to drive growth in the coming quarters.",
            "source": "Financial Times",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-product-launch",
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "symbol": ticker_symbol.upper(),
            "market": market,
            "sentimentScore": 0.8
        },
        {
            "headline": f"Analysts Upgrade {ticker_symbol} to Buy Rating",
            "summary": f"Leading analysts have upgraded {ticker_symbol} from Hold to Buy based on strong quarterly results and positive outlook.",
            "source": "Wall Street Journal",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-upgrade",
            "publishedAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
            "symbol": ticker_symbol.upper(),
            "market": market,
            "sentimentScore": 0.9
        },
        {
            "headline": f"{ticker_symbol} Faces Supply Chain Challenges",
            "summary": f"{ticker_symbol} reported minor supply chain disruptions that may affect Q4 delivery targets.",
            "source": "Bloomberg",
            "url": f"https://example.com/news/{ticker_symbol.lower()}-supply-chain",
            "publishedAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "symbol": ticker_symbol.upper(),
            "market": market,
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
    print(f"Inserted/Updated {len(mock_news)} news articles for {ticker_symbol} in {market} market")

def run_ai_analysis():
    """Run all AI analysis processes"""
    print("Running AI analysis...")
    analyze_news_sentiment()
    
    # Generate insights for all tracked tickers across markets
    for market in ["US", "INDIA", "CRYPTO"]:
        for ticker in POPULAR_TICKERS[market][:3]:  # First 3 tickers per market
            base_ticker = ticker.replace(".NS", "").replace("-USD", "")
            insights = generate_insights(base_ticker, market)
            print(f"Insights for {base_ticker} ({market}): {insights}")

if __name__ == "__main__":
    # Fetch data for all markets
    print("=== FETCHING US STOCK DATA ===")
    for ticker in POPULAR_TICKERS["US"][:5]:  
        fetch_stock_data(ticker, "US")
        fetch_news_data(ticker, "US")
    
    print("\n=== FETCHING INDIAN STOCK DATA ===")
    for ticker in POPULAR_TICKERS["INDIA"][:5]:
        base_ticker = ticker.replace(".NS", "")
        fetch_stock_data(base_ticker, "INDIA")
        fetch_news_data(base_ticker, "INDIA")
    
    print("\n=== FETCHING CRYPTO DATA ===")
    for ticker in POPULAR_TICKERS["CRYPTO"][:5]:
        base_ticker = ticker.replace("-USD", "")
        fetch_stock_data(base_ticker, "CRYPTO")
        fetch_news_data(base_ticker, "CRYPTO")
    
    # Run AI analysis after fetching data
    run_ai_analysis()