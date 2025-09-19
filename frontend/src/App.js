import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [market, setMarket] = useState('US');
  const [overviewData, setOverviewData] = useState(null);
  const [newsData, setNewsData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [availableMarkets, setAvailableMarkets] = useState(['US']);
  const [popularTickers, setPopularTickers] = useState([]);

  // Fetch available markets on component mount
  useEffect(() => {
    fetch('http://localhost:8000/api/markets')
      .then(response => response.json())
      .then(data => setAvailableMarkets(data))
      .catch(console.error);
  }, []);

  // Fetch popular tickers when market changes
  useEffect(() => {
    fetch(`http://localhost:8000/api/markets/${market}/popular-tickers`)
      .then(response => response.json())
      .then(data => setPopularTickers(data.tickers || []))
      .catch(console.error);
  }, [market]);

  const fetchTickerData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Overview Data
      const overviewResponse = await fetch(`http://localhost:8000/api/ticker/${market}/${ticker}/overview`);
      if (!overviewResponse.ok) {
        throw new Error(`HTTP error! status: ${overviewResponse.status}`);
      }
      const overviewJson = await overviewResponse.json();
      setOverviewData(overviewJson);

      // 2. Fetch News Data
      const newsResponse = await fetch(`http://localhost:8000/api/ticker/${market}/${ticker}/news`);
      const newsJson = await newsResponse.json();
      setNewsData(newsJson);

      // 3. Fetch AI Insights
      const insightsResponse = await fetch(`http://localhost:8000/api/ticker/${market}/${ticker}/insights`);
      const insightsJson = await insightsResponse.json();
      setInsightsData(insightsJson);

    } catch (e) {
      setError(e.message);
      console.error("Failed to fetch data:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickerData();
  }, [ticker, market]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const formTicker = event.target.elements.tickerInput.value;
    setTicker(formTicker);
  };

  const handleMarketChange = (newMarket) => {
    setMarket(newMarket);
    // Reset to first popular ticker when market changes
    if (popularTickers.length > 0) {
      // Extract base symbol for display
      const baseTicker = popularTickers[0].replace('.NS', '').replace('-USD', '');
      setTicker(baseTicker);
    }
  };

  const getSentimentEmoji = (score) => {
    if (score > 0.3) return '😊';
    if (score < -0.3) return '😠';
    return '😐';
  };

  const getSentimentColor = (score) => {
    if (score > 0.3) return '#4caf50'; // Green
    if (score < -0.3) return '#f44336'; // Red
    return '#ff9800'; // Orange
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>📈 TickerTracker</h1>
        
        {/* Market Selection */}
        <div className="market-selector">
          <label>Select Market: </label>
          <select 
            value={market} 
            onChange={(e) => handleMarketChange(e.target.value)}
            className="market-dropdown"
          >
            {availableMarkets.map(mkt => (
              <option key={mkt} value={mkt}>{mkt}</option>
            ))}
          </select>
        </div>

        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            name="tickerInput"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder={`Enter ${market} ticker (e.g., ${popularTickers[0]?.replace('.NS', '').replace('-USD', '') || 'AAPL'})`}
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
        </form>

        {/* Popular Tickers Quick Access */}
        <div className="popular-tickers">
          <span>Quick access: </span>
          {popularTickers.slice(0, 5).map(popularTicker => (
            <button
              key={popularTicker}
              className="ticker-button"
              onClick={() => {
                // Extract base symbol for display
                const baseTicker = popularTicker.replace('.NS', '').replace('-USD', '');
                setTicker(baseTicker);
              }}
            >
              {popularTicker.replace('.NS', '').replace('-USD', '')}
            </button>
          ))}
        </div>
      </header>

      <main className="main-content">
        {loading && <div className="loading">Loading data...</div>}
        {error && <div className="error">Error: {error}</div>}

        {/* Navigation Tabs */}
        <div className="tabs">
          <button 
            className={activeTab === 'overview' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={activeTab === 'news' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('news')}
          >
            News & Sentiment
          </button>
          <button 
            className={activeTab === 'insights' ? 'tab active' : 'tab'}
            onClick={() => setActiveTab('insights')}
          >
            AI Insights
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && overviewData && !overviewData.error && (
          <section className="overview">
            <h2>{overviewData.name} ({overviewData.symbol})</h2>
            <div className="market-badge">{overviewData.market} Market</div>
            <div className="price-display">
              <div className="price">
                {overviewData.currency === 'INR' ? '₹' : '$'}{overviewData.price}
                <span className="currency">{overviewData.currency}</span>
              </div>
              <div className="change" style={{ color: overviewData.change >= 0 ? '#4caf50' : '#f44336' }}>
                {overviewData.change >= 0 ? '+' : ''}{overviewData.change} ({overviewData.changePercent}%)
              </div>
            </div>
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Market Cap:</span>
                <span className="stat-value">
                  {overviewData.currency === 'INR' ? '₹' : '$'}
                  {(overviewData.marketCap / 1e9).toFixed(2)}B
                  <span className="currency">{overviewData.currency}</span>
                </span>
              </div>
            </div>
          </section>
        )}

        {/* News Tab */}
        {activeTab === 'news' && newsData && (
          <section className="news">
            <h3>Latest News & Sentiment</h3>
            <div className="news-grid">
              {newsData.map((article) => (
                <div key={article._id} className="news-card">
                  <h4>{article.headline}</h4>
                  <p>{article.summary}</p>
                  <div className="news-meta">
                    <span className="source">{article.source}</span>
                    {article.sentimentScore && (
                      <span 
                        className="sentiment"
                        style={{ color: getSentimentColor(article.sentimentScore) }}
                      >
                        {getSentimentEmoji(article.sentimentScore)} Sentiment: {article.sentimentScore.toFixed(2)}
                      </span>
                    )}
                    <span className="date">
                      {new Date(article.publishedAt).toLocaleDateString()}
                    </span>
                  </div>
                  <a href={article.url} target="_blank" rel="noopener noreferrer" className="read-more">
                    Read more
                  </a>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && insightsData && (
          <section className="insights">
            <h3>AI Insights for {insightsData.ticker} ({insightsData.market})</h3>
            <div className="insights-card">
              <div className="insight-content">
                <p>{insightsData.insights}</p>
              </div>
              <div className="insight-footer">
                <span className="ai-badge">🤖 AI Analysis</span>
              </div>
            </div>
          </section>
        )}

        {overviewData?.error && <div className="error">Ticker not found.</div>}
      </main>
    </div>
  );
}

export default App;