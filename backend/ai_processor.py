import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timezone, timedelta
from database import SessionLocal, news_collection
from sqlalchemy.orm import Session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentiment analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze_news_sentiment():
    """
    Analyze sentiment for all news articles that don't have sentiment scores yet
    """
    logger.info("Analyzing news sentiment...")
    
    try:
        # Find news articles without sentiment scores
        articles_to_analyze = list(news_collection.find({
            "sentimentScore": {"$exists": False}
        }))
        
        if not articles_to_analyze:
            logger.info("No new articles to analyze")
            return
        
        analyzed_count = 0
        for article in articles_to_analyze:
            headline = article.get('headline', '')
            summary = article.get('summary', '')
            
            # Combine headline and summary for better analysis
            text_to_analyze = f"{headline}. {summary}"
            
            # Get sentiment scores
            sentiment_scores = sentiment_analyzer.polarity_scores(text_to_analyze)
            compound_score = sentiment_scores['compound']  # -1 (negative) to +1 (positive)
            
            # Update the article with sentiment score
            news_collection.update_one(
                {"_id": article["_id"]},
                {"$set": {
                    "sentimentScore": compound_score,
                    "sentimentAnalysis": {
                        "positive": sentiment_scores['pos'],
                        "neutral": sentiment_scores['neu'],
                        "negative": sentiment_scores['neg'],
                        "compound": compound_score
                    },
                    "analyzedAt": datetime.now(timezone.utc)
                }}
            )
            analyzed_count += 1
        
        logger.info(f"Analyzed sentiment for {analyzed_count} articles")
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    deltas = np.diff(prices)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gains and losses
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # Calculate subsequent averages using smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    # Avoid division by zero
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_moving_averages(prices, short_window=20, long_window=50):
    """
    Calculate Simple Moving Averages
    """
    if len(prices) < long_window:
        return None, None
    
    short_ma = np.mean(prices[-short_window:])
    long_ma = np.mean(prices[-long_window:])
    
    return round(short_ma, 2), round(long_ma, 2)

def calculate_technical_indicators(ticker_symbol="AAPL", market="US"):
    """
    Calculate technical indicators for a given ticker
    """
    logger.info(f"Calculating technical indicators for {ticker_symbol} ({market})...")
    
    try:
        # Get the full symbol for the market
        from market_config import get_full_symbol
        full_symbol = get_full_symbol(ticker_symbol, market)
        
        import yfinance as yf
        ticker = yf.Ticker(full_symbol)
        history = ticker.history(period="1mo")  # 1 month of data
        
        if history.empty:
            logger.warning(f"No historical data for {full_symbol}")
            return None
        
        prices = history['Close'].tolist()
        
        # Calculate indicators
        rsi = calculate_rsi(prices)
        short_ma, long_ma = calculate_moving_averages(prices)
        
        # Get current price
        current_price = prices[-1] if prices else None
        
        # Generate trading signal based on indicators
        signal = "NEUTRAL"
        if rsi and current_price and short_ma and long_ma:
            if rsi > 70:
                signal = "OVERBOUGHT"
            elif rsi < 30:
                signal = "OVERSOLD"
            elif current_price > short_ma > long_ma:
                signal = "BULLISH"
            elif current_price < short_ma < long_ma:
                signal = "BEARISH"
        
        indicators = {
            "rsi": rsi,
            "shortMA": short_ma,
            "longMA": long_ma,
            "currentPrice": round(current_price, 2) if current_price else None,
            "signal": signal,
            "lastUpdated": datetime.now(timezone.utc)
        }
        
        logger.info(f"Technical indicators for {ticker_symbol}: {indicators}")
        return indicators
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators for {ticker_symbol}: {e}")
        return None

def generate_insights(ticker_symbol="AAPL", market="US"):
    """
    Generate AI insights based on sentiment and technical analysis
    """
    logger.info(f"Generating insights for {ticker_symbol} ({market})...")
    
    try:
        # Get latest news sentiment for this ticker and market
        latest_news = list(news_collection.find({
            "symbol": ticker_symbol.upper(),
            "market": market.upper()
        }).sort("publishedAt", -1).limit(5))
        
        # Calculate average sentiment
        sentiment_scores = []
        for news in latest_news:
            if 'sentimentScore' in news and news['sentimentScore'] is not None:
                sentiment_scores.append(news['sentimentScore'])
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Get technical indicators
        tech_indicators = calculate_technical_indicators(ticker_symbol, market)
        
        # Generate simple insights based on rules
        insights = []
        
        if tech_indicators:
            if tech_indicators['signal'] == 'BULLISH':
                insights.append("Technical indicators show bullish trend with price above moving averages.")
            elif tech_indicators['signal'] == 'BEARISH':
                insights.append("Technical indicators suggest bearish trend with price below moving averages.")
            
            if tech_indicators['rsi'] and tech_indicators['rsi'] > 70:
                insights.append("RSI indicates overbought conditions, suggesting potential pullback.")
            elif tech_indicators['rsi'] and tech_indicators['rsi'] < 30:
                insights.append("RSI indicates oversold conditions, suggesting potential bounce.")
        
        # Add sentiment insights
        if avg_sentiment > 0.3:
            insights.append("Recent news sentiment is strongly positive.")
        elif avg_sentiment < -0.3:
            insights.append("Recent news sentiment is strongly negative.")
        elif sentiment_scores and abs(avg_sentiment) < 0.1:
            insights.append("News sentiment is relatively neutral recently.")
        else:
            insights.append("No recent news sentiment data available.")
        
        # Add market-specific context
        if market == "CRYPTO":
            insights.append("Cryptocurrency markets are highly volatile. Exercise caution with investments.")
        elif market == "INDIA":
            insights.append("Indian market performance may be influenced by local economic factors and regulations.")
        
        # Combine insights
        if not insights:
            insights.append("No strong signals detected. Market appears to be in consolidation.")
        
        insight_text = " ".join(insights)
        
        logger.info(f"Generated insights for {ticker_symbol} ({market}): {insight_text}")
        return insight_text
        
    except Exception as e:
        logger.error(f"Error generating insights for {ticker_symbol} ({market}): {e}")
        return f"Unable to generate insights for {ticker_symbol} at this time. Error: {str(e)}"

# Test function
def test_ai_processor():
    """Test all AI processor functions"""
    print("Testing AI Processor...")
    
    # Test sentiment analysis
    analyze_news_sentiment()
    
    # Test insights generation for each market
    test_cases = [
        ("AAPL", "US"),
        ("RELIANCE", "INDIA"), 
        ("BTC", "CRYPTO")
    ]
    
    for symbol, market in test_cases:
        insights = generate_insights(symbol, market)
        print(f"\nInsights for {symbol} ({market}):")
        print(insights)

if __name__ == "__main__":
    test_ai_processor()