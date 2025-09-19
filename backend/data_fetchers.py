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
        
    API_KEY = "7d9923d9b71c4a2f9c0f41aa05a88cf3"  
    
    if API_KEY == "YOUR_NEWSAPI_KEY_HERE":
        print("ERROR: Please get a NewsAPI key from https://newsapi.org/ and update the script.")
        return create_fallback_news(ticker_symbol, market)
    
    try:
        # Search for news about this ticker
        search_query = f"{ticker_symbol} stock"
        if market == "CRYPTO":
            search_query = f"{ticker_symbol} cryptocurrency"
        
        url = f"https://newsapi.org/v2/everything?q={search_query}&language=en&sortBy=publishedAt&pageSize=5&apiKey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if data['status'] != 'ok' or 'articles' not in data:
            print("Error fetching from NewsAPI, using fallback data")
            return create_fallback_news(ticker_symbol, market)
        
        articles = data['articles']
        inserted_count = 0
        
        for article in articles:
            # Structure the data for MongoDB
            news_document = {
                "symbol": ticker_symbol.upper(),
                "market": market,
                "headline": article['title'],
                "summary": article['description'] or article['title'],
                "source": article['source']['name'],
                "url": article['url'],
                "publishedAt": article['publishedAt'],
                "content": article['content'],
                # sentimentScore will be added later by AI analysis
            }
            
            # Insert into MongoDB
            news_collection.update_one(
                {"url": article['url']},
                {"$set": news_document},
                upsert=True
            )
            inserted_count += 1
        
        print(f"Inserted/Updated {inserted_count} real news articles for {ticker_symbol} in {market} market")
        
    except Exception as e:
        print(f"Error fetching news for {ticker_symbol}: {e}")
        create_fallback_news(ticker_symbol, market)

def create_fallback_news(ticker_symbol, market):
    """Create fallback mock news if API fails"""
    print("Creating fallback mock news...")
    
    market_specific_news = {
        "US": [
            {
                "headline": f"{ticker_symbol} Quarterly Earnings Beat Expectations",
                "summary": f"{ticker_symbol} reported better-than-expected quarterly results, driven by strong consumer demand.",
                "source": "MarketWatch",
                "url": f"https://example.com/{ticker_symbol}-earnings",
                "publishedAt": datetime.now(timezone.utc).isoformat(),
            },
            {
                "headline": f"Analysts Raise Price Target for {ticker_symbol}",
                "summary": f"Several Wall Street analysts have increased their price targets for {ticker_symbol} following positive guidance.",
                "source": "Bloomberg",
                "url": f"https://example.com/{ticker_symbol}-price-target",
                "publishedAt": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
            }
        ],
        "INDIA": [
            {
                "headline": f"{ticker_symbol} Expands Operations in Indian Market",
                "summary": f"{ticker_symbol} announces new investments in Indian manufacturing facilities.",
                "source": "Economic Times",
                "url": f"https://example.com/{ticker_symbol}-india-expansion",
                "publishedAt": datetime.now(timezone.utc).isoformat(),
            },
            {
                "headline": f"{ticker_symbol} Partners with Indian Tech Firms",
                "summary": f"{ticker_symbol} forms strategic partnerships with leading Indian technology companies.",
                "source": "Business Standard",
                "url": f"https://example.com/{ticker_symbol}-india-partnership",
                "publishedAt": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            }
        ],
        "CRYPTO": [
            {
                "headline": f"{ticker_symbol} Adoption Continues to Grow",
                "summary": f"Major retailers and services continue to adopt {ticker_symbol} payments.",
                "source": "CoinDesk",
                "url": f"https://example.com/{ticker_symbol}-adoption",
                "publishedAt": datetime.now(timezone.utc).isoformat(),
            },
            {
                "headline": f"{ticker_symbol} Network Upgrade Completed Successfully",
                "summary": f"The latest network upgrade for {ticker_symbol} has been successfully implemented.",
                "source": "CryptoNews",
                "url": f"https://example.com/{ticker_symbol}-upgrade",
                "publishedAt": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
            }
        ]
    }
    
    # Use market-specific news templates
    news_items = market_specific_news.get(market, market_specific_news["US"])
    
    for article in news_items:
        article["symbol"] = ticker_symbol.upper()
        article["market"] = market
        news_collection.update_one(
            {"url": article['url']},
            {"$set": article},
            upsert=True
        )
    
    print(f"Created {len(news_items)} fallback news articles for {ticker_symbol} in {market} market")
    
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