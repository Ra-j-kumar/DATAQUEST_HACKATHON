# Supported markets and their configurations
MARKET_CONFIG = {
    "US": {
        "name": "US Stock Market",
        "symbol_suffix": "",
        "data_source": "yfinance",
        "exchange": "",
        "currency": "USD"
    },
    "INDIA": {
        "name": "Indian Stock Market",
        "symbol_suffix": ".NS",  # NSE suffix for yfinance
        "data_source": "yfinance",
        "exchange": "NSE",
        "currency": "INR"
    },
    "CRYPTO": {
        "name": "Cryptocurrency",
        "symbol_suffix": "-USD",  # yfinance format for crypto
        "data_source": "yfinance",  # We'll use yfinance for crypto too
        "exchange": "",
        "currency": "USD"
    }
}

# Popular tickers for each market for quick access
POPULAR_TICKERS = {
    "US": ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "JPM", "JNJ", "V"],
    "INDIA": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
              "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS"],
    "CRYPTO": ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "XRP-USD", 
               "SOL-USD", "DOT-USD", "DOGE-USD", "AVAX-USD", "MATIC-USD"]
}

def get_full_symbol(ticker, market):
    """Convert a base ticker to the full symbol for the given market"""
    if market in MARKET_CONFIG:
        return ticker + MARKET_CONFIG[market]["symbol_suffix"]
    return ticker

def get_base_symbol(full_symbol, market):
    """Extract the base symbol from a full symbol"""
    if market in MARKET_CONFIG:
        suffix = MARKET_CONFIG[market]["symbol_suffix"]
        if full_symbol.endswith(suffix):
            return full_symbol[:-len(suffix)]
    return full_symbol