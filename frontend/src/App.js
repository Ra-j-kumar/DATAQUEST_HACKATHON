// import React, { useState, useEffect } from 'react';
// import './App.css';

// function App() {
//   const [ticker, setTicker] = useState('AAPL');
//   const [market, setMarket] = useState('us_stock');
//   const [overviewData, setOverviewData] = useState(null);
//   const [newsData, setNewsData] = useState(null);
//   const [insightsData, setInsightsData] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [activeTab, setActiveTab] = useState('overview');
//   const [availableMarkets, setAvailableMarkets] = useState([]);
//   const [marketTickers, setMarketTickers] = useState([]);

//   // Fetch available markets on component mount
//   useEffect(() => {
//     fetch('http://localhost:8000/api/markets')
//       .then(response => response.json())
//       .then(data => setAvailableMarkets(data))
//       .catch(error => console.error('Error fetching markets:', error));
//   }, []);

//   // Fetch tickers for selected market
//   useEffect(() => {
//     if (market) {
//       fetch(`http://localhost:8000/api/market/${market}/tickers`)
//         .then(response => response.json())
//         .then(data => setMarketTickers(data))
//         .catch(error => console.error('Error fetching market tickers:', error));
//     }
//   }, [market]);

//   const fetchTickerData = async () => {
//     setLoading(true);
//     setError(null);
//     try {
//       // 1. Fetch Overview Data
//       const overviewResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/overview`);
//       if (!overviewResponse.ok) {
//         throw new Error(`HTTP error! status: ${overviewResponse.status}`);
//       }
//       const overviewJson = await overviewResponse.json();
//       setOverviewData(overviewJson);

//       // 2. Fetch News Data
//       const newsResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/news`);
//       const newsJson = await newsResponse.json();
//       setNewsData(newsJson);

//       // 3. Fetch AI Insights
//       const insightsResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/insights`);
//       const insightsJson = await insightsResponse.json();
//       setInsightsData(insightsJson);

//     } catch (e) {
//       setError(e.message);
//       console.error("Failed to fetch data:", e);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchTickerData();
//   }, [ticker]);

//   const handleSubmit = (event) => {
//     event.preventDefault();
//     const formTicker = event.target.elements.tickerInput.value;
//     setTicker(formTicker);
//   };

//   const handleMarketChange = (newMarket) => {
//     setMarket(newMarket);
//     // Reset ticker to first available ticker in the new market
//     if (marketTickers.length > 0) {
//       setTicker(marketTickers[0].symbol);
//     }
//   };


//   return (
//     <div className="App">
//       <header className="App-header">
//          <h1>📈 TickerTracker</h1>
//          {/* Market Selection */}
//         <div className="market-selector">
//           <label>Select Market: </label>
//           <select 
//             value={market} 
//             onChange={(e) => handleMarketChange(e.target.value)}
//             className="market-dropdown"
//           >
//             {availableMarkets.map(mkt => (
//               <option key={mkt.id} value={mkt.id}>{mkt.name}</option>
//             ))}
//           </select>
//         </div>

//         {/* Search Form */}
//         <form onSubmit={handleSubmit}>
//           <input
//             type="text"
//             name="tickerInput"
//             defaultValue={ticker}
//             placeholder="Enter a ticker (e.g., AAPL, MSFT)"
//           />

//           <button type="submit">Search</button>
//         </form>
//         {/* Ticker Selection */}
//         <form onSubmit={handleSubmit} className="search-form">
//           <select 
//             value={ticker} 
//             onChange={(e) => setTicker(e.target.value)}
//             className="ticker-dropdown"
//           >
//             {marketTickers.map(tkr => (
//               <option key={tkr.symbol} value={tkr.symbol}>
//                 {tkr.symbol} - {tkr.name}
//               </option>
//             ))}
//           </select>
//           <button type="submit" className="search-button">Refresh</button>
//         </form>
//       </header>

//       <main>
//         {loading && <p>Loading data...</p>}
//         {error && <p style={{ color: 'red' }}>Error: {error}</p>}

//         {/* Display Overview Data */}
//         {overviewData && !overviewData.error && (
//           <section className="overview">
//             <h2>{overviewData.name} ({overviewData.symbol})</h2>
//             <p><strong>Price:</strong> ${overviewData.price}</p>
//             <p style={{ color: overviewData.change >= 0 ? 'green' : 'red' }}>
//               <strong>Change:</strong> {overviewData.change} ({overviewData.changePercent}%)
//             </p>
//             <p><strong>Market Cap:</strong> ${(overviewData.marketCap / 1e12).toFixed(2)} T</p>
//           </section>
//         )}
//         {overviewData?.error && <p>Ticker not found.</p>}

//         {/* Display News Data */}
//         {newsData && (
//           <section className="news">
//             <h2>Latest News</h2>
//             <ul>
//               {newsData.map((article) => (
//                 <li key={article.id}>
//                   <h3>{article.headline}</h3>
//                   <p>{article.summary}</p>
//                   <p><em>Source: {article.source}</em> | Sentiment: <strong>{article.sentimentScore > 0 ? '😊 Positive' : article.sentimentScore < 0 ? '😠 Negative' : '😐 Neutral'}</strong></p>
//                 </li>
//               ))}
//             </ul>
//           </section>
//         )}
//       </main>
//     </div>
//   );
// }

// export default App;



import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('AAPL');
  const [overviewData, setOverviewData] = useState(null);
  const [newsData, setNewsData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const fetchTickerData = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch Overview Data
      const overviewResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/overview`);
      if (!overviewResponse.ok) {
        throw new Error(`HTTP error! status: ${overviewResponse.status}`);
      }
      const overviewJson = await overviewResponse.json();
      setOverviewData(overviewJson);

      // 2. Fetch News Data
      const newsResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/news`);
      const newsJson = await newsResponse.json();
      setNewsData(newsJson);

      // 3. Fetch AI Insights
      const insightsResponse = await fetch(`http://localhost:8000/api/ticker/${ticker}/insights`);
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
  }, [ticker]);

  const handleSubmit = (event) => {
    event.preventDefault();
    const formTicker = event.target.elements.tickerInput.value;
    setTicker(formTicker);
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
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            name="tickerInput"
            defaultValue={ticker}
            placeholder="Enter a ticker (e.g., AAPL, MSFT, GOOGL)"
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
        </form>
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
            <div className="price-display">
              <div className="price">${overviewData.price}</div>
              <div className="change" style={{ color: overviewData.change >= 0 ? '#4caf50' : '#f44336' }}>
                {overviewData.change >= 0 ? '+' : ''}{overviewData.change} ({overviewData.changePercent}%)
              </div>
            </div>
            <div className="stats">
              <div className="stat">
                <span className="stat-label">Market Cap:</span>
                <span className="stat-value">${(overviewData.marketCap / 1e9).toFixed(2)}B</span>
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
            <h3>AI Insights for {insightsData.ticker}</h3>
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