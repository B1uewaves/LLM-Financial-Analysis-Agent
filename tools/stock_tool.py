# Grabs live price, company name, and 30‑day history via yfinance.

import yfinance as yf

def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch current price, company name, and 30-day closing history.
    """
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info

    # Grab last 30 days of closing prices
    hist = ticker_obj.history(period="30d")["Close"].tolist()

    return {
        "ticker": ticker.upper(),
        "name": info.get("longName") or info.get("shortName"),
        "current_price": info.get("currentPrice"),
        "history_30d": hist,
    }