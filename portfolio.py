import os
import numpy as np
from scipy.stats import norm
from polygon import StocksClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

client = StocksClient(os.getenv("POLYGON_API_KEY"))

# Your exact portfolio (update shares if you change)
PORTFOLIO = {
    "TSLA": {"shares": 600, "avg_price": 339},
    "RKLB": {"shares": 650, "avg_price": 26.6},
    "PLTR": {"shares": 200, "avg_price": 125.6},
    "NVDA": {"shares": 150, "avg_price": None}, # put your cost basis if known
    "ONDS": {"shares": 1111, "avg_price": 12.46},
}

# TSLA LEAP collar details (Dec 15 2028)
COLLARS = {
    "TSLA": {
        "expiry": "2028-12-15",
        "put_strike": 300,
        "call_strike": 600,
        "contracts": 5, # 500 shares protected
        "put_symbol": "O:TSLA281215P00300000", # Polygon format
        "call_symbol": "O:TSLA281215C00600000",
    }
}

def black_scholes_greeks(S, K, T, r, sigma, option_type="call"):
    """Full Black-Scholes Greeks calculator"""
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else: # put
        delta = norm.cdf(d1) - 1
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    return {"delta": delta, "gamma": gamma, "theta": theta, "vega": vega, "rho": rho}

def get_portfolio_snapshot():
    data = {}
    total_mv = 0
    net_delta = 0
    
    for ticker, info in PORTFOLIO.items():
        try:
            snapshot = client.get_ticker_snapshot(ticker)
            price = snapshot.last["price"]
            mv = info["shares"] * price
            total_mv += mv
            net_delta += info["shares"] # stocks = delta 1.0
            
            data[ticker] = {
                "price": round(price, 2),
                "mv": round(mv, 0),
                "shares": info["shares"],
                "delta_contrib": info["shares"]
            }
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            data[ticker] = {
                "price": 0,
                "mv": 0,
                "shares": info["shares"],
                "delta_contrib": 0
            }
    
    # TSLA collar adjustment (approximate live IV ~53-55%; you can override)
    if "TSLA" in data and data["TSLA"]["price"] > 0:
        tsla_price = data["TSLA"]["price"]
        T = 2.71 # years to Dec 2028
        r = 0.04
        iv = 0.535 # current live IV for your LEAPs — code can pull exact later
        
        # Long put Greeks
        put_g = black_scholes_greeks(tsla_price, 300, T, r, iv, "put")
        # Short call Greeks
        call_g = black_scholes_greeks(tsla_price, 600, T, r, iv, "call")
        
        collar_net_delta = (put_g["delta"] - call_g["delta"]) * 500
        net_delta += collar_net_delta # replaces 500 shares with net option delta
        
        data["TSLA"]["delta_contrib"] = 100 + collar_net_delta + 500 # 100 naked + collar net
    
    return {
        "positions": data,
        "total_mv": round(total_mv, 0),
        "net_delta_equiv": round(net_delta, 0),
        "spx_equiv": round(total_mv / 638, 0) # rough SPY equivalent
    }

# For future: add full scenario engine here (copy from our earlier tables)
