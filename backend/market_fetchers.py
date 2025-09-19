import yfinance as yf
import requests
from sqlalchemy.orm import Session
from database import SessionLocal
from models import TickerOverview, MarketType
from datetime import datetime, timezone
import json

def fetch_us_stock_data(ticker_symbol):
    """Fetch data for US stocks using Yahoo Finance"""
    db = SessionLocal()
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        history = ticker.history(period="2d")
        
        if history.empty or len(history) < 2:
            return None
            
        last_price = history['Close'].iloc[-1]
        prev_close = history['Close'].iloc[-2]
        change = last_price - prev_close
        change_percent = (change / prev_close) * 100
        
        overview_data = {
            "symbol": ticker_symbol.upper(),
            "name": info.get('longName', ticker_symbol),
            "price": float(round(last_price, 2)),
            "change": float(round(change, 2)),
            "changePercent": float(round(change_percent, 2)),
            "marketCap": info.get('marketCap', 0),
            "market": MarketType.US_STOCK,
            "currency": "USD"
        }
        
        # Update or create record
        existing_ticker = db.query(TickerOverview).filter(
            TickerOverview.symbol == ticker_symbol.upper(),
            TickerOverview.market == MarketType.US_STOCK
        ).first()
        
        if existing_ticker:
            for key, value in overview_data.items():
                setattr(existing_ticker, key, value)
            existing_ticker.last_updated = datetime.now(timezone.utc)
        else:
            new_ticker = TickerOverview(**overview_data)
            db.add(new_ticker)
            
        db.commit()
        return overview_data
        
    except Exception as e:
        print(f"Error fetching US stock {ticker_symbol}: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def fetch_indian_stock_data(ticker_symbol):
    """Fetch data for Indian stocks using Yahoo Finance (format: TICKER.NS)"""
    # Indian stocks on Yahoo Finance use .NS suffix
    yahoo_symbol = f"{ticker_symbol}.NS"
    return fetch_us_stock_data(yahoo_symbol)

def fetch_crypto_data(crypto_symbol):
    """Fetch data for cryptocurrencies using Yahoo Finance"""
    # Cryptos on Yahoo Finance use -USD suffix
    yahoo_symbol = f"{crypto_symbol}-USD"
    db = SessionLocal()
    try:
        ticker = yf.Ticker(yahoo_symbol)
        info = ticker.info
        history = ticker.history(period="2d")
        
        if history.empty or len(history) < 2:
            return None
            
        last_price = history['Close'].iloc[-1]
        prev_close = history['Close'].iloc[-2]
        change = last_price - prev_close
        change_percent = (change / prev_close) * 100
        
        overview_data = {
            "symbol": crypto_symbol.upper(),
            "name": info.get('name', crypto_symbol),
            "price": float(round(last_price, 2)),
            "change": float(round(change, 2)),
            "changePercent": float(round(change_percent, 2)),
            "marketCap": info.get('marketCap', 0),
            "market": MarketType.CRYPTO,
            "currency": "USD"
        }
        
        # Update or create record
        existing_ticker = db.query(TickerOverview).filter(
            TickerOverview.symbol == crypto_symbol.upper(),
            TickerOverview.market == MarketType.CRYPTO
        ).first()
        
        if existing_ticker:
            for key, value in overview_data.items():
                setattr(existing_ticker, key, value)
            existing_ticker.last_updated = datetime.now(timezone.utc)
        else:
            new_ticker = TickerOverview(**overview_data)
            db.add(new_ticker)
            
        db.commit()
        return overview_data
        
    except Exception as e:
        print(f"Error fetching crypto {crypto_symbol}: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def fetch_all_market_data():
    """Fetch data for all supported markets"""
    print("Fetching data for all markets...")
    
    # US Stocks
    us_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    for symbol in us_stocks:
        fetch_us_stock_data(symbol)
    
    # Indian Stocks (major companies)
    indian_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
    for symbol in indian_stocks:
        fetch_indian_stock_data(symbol)
    
    # Cryptocurrencies
    cryptos = ["BTC", "ETH", "BNB", "ADA", "DOGE"]
    for symbol in cryptos:
        fetch_crypto_data(symbol)
    
    print("Completed fetching multi-market data")