# Jane Street AI Trading Agent

A personal AI-powered trading agent with live market data, option Greeks, portfolio analytics, and AI analysis powered by xAI Grok.

## Features

- 📊 **Portfolio Tracking** - Track your stock positions with live prices
- 📈 **Option Greeks** - Calculate Delta, Gamma, Theta, Vega for positions
- 🤖 **AI Analyst** - Ask Grok for portfolio analysis and trading advice
- 📉 **Scenario Analysis** - Run what-if scenarios on your positions
- 🔄 **Live Data** - Real-time prices from Polygon.io

## Quick Start

### 1. Clone & Install
```bash
git clone <your-repo-url>
cd jane-street-ai-agent
pip install -r requirements.txt
```

### 2. Set API Keys
Create a `.env` file:
```
POLYGON_API_KEY=your_polygon_key
XAI_API_KEY=your_xai_key
```

Get free keys:
- Polygon.io: https://polygon.io/dashboard/keys
- xAI: https://x.ai/api

### 3. Run
```bash
streamlit run app.py
```

Open http://localhost:8501

## Portfolio Configuration

Edit `portfolio.py` to update your holdings:
```python
PORTFOLIO = {
    "TSLA": {"shares": 600, "avg_price": 339},
    "RKLB": {"shares": 650, "avg_price": 26.6},
    # Add more...
}
```

## Tech Stack

- **Frontend**: Streamlit
- **Data**: Polygon.io API
- **AI**: xAI Grok
- **Analytics**: NumPy, SciPy, Pandas

## Deploy to Streamlit Cloud

1. Push this code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repo
4. Deploy!

---
Built for personal use 🚀
