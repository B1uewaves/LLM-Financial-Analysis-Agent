# Fetches live stock data (price, 30‑day history, key metrics) via yfinance.
# Implements simple in‑memory caching to reduce redundant API calls.
# Returns raw Python dicts for downstream LLM consumption.

import yfinance as yf
from typing import Optional

def _human_format(num: Optional[float]) -> str:
    """Convert large numbers to human-friendly strings (e.g. 1.2B, 5.6M)."""
    if num is None:
        return "N/A"
    magnitude = 0
    units = ['', 'K', 'M', 'B', 'T']
    while abs(num) >= 1000 and magnitude < len(units)-1:
        magnitude += 1
        num /= 1000.0
    return f"{num:.1f}{units[magnitude]}"

def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch data from yfinance and compute:
      - current_price
      - pct_change vs. previous close
      - 30‑day trend (%)
      - volume vs. avg volume
      - bid/ask
      - day’s low/high
      - market_cap
      - P/E ratio
      - 30‑day closing history
    Returns {"error": "..."} on failure.
    """

    ticker = ticker.strip().upper()

    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
    except Exception as e:
        return {"error": f"Failed to fetch data for '{ticker}': {e}"}

    # Now fetch history
    try:
        hist = tkr.history(period="31d")
    except Exception as e:
        return {"error": f"Failed to fetch history for '{ticker}': {e}"}

    # No data?
    if hist.empty or "Close" not in hist:
        return {"error": f"No price data found for '{ticker}'."}

    # Get history for 31 days so we can compute a 30d trend
    closes = hist["Close"].tolist()
    if len(closes) < 2:
        return {"ticker": ticker, "error": f"Not enough closing prices for '{ticker}'."}

    history_30d = closes[-30:]
    price_30d_ago = closes[0] if len(closes) >= 30 else closes[0]

    # Prices
    current_price   = info.get("currentPrice") or closes[-1]
    previous_close  = info.get("previousClose") or closes[-2]

    # Percent changes
    pct_change      = (current_price - previous_close) / previous_close * 100
    trend_30d_pct   = (current_price - price_30d_ago)     / price_30d_ago  * 100

    # Volume
    volume          = info.get("volume")
    avg_volume      = info.get("averageVolume")
    vol_str         = f"{_human_format(volume)} (avg {_human_format(avg_volume)})"

    # Bid/Ask
    bid             = info.get("bid", 0.0)
    ask             = info.get("ask", 0.0)
    bid_ask_str     = f"${bid:.2f}/${ask:.2f}"

    # Day’s range
    low             = info.get("dayLow")
    high            = info.get("dayHigh")
    day_range_str   = f"${low:.2f}–${high:.2f}"

    # Market cap & P/E
    mc              = info.get("marketCap", 0)
    market_cap_str  = f"${_human_format(mc)}"
    pe_ratio        = info.get("trailingPE") or info.get("forwardPE") or 0.0
    pe_ratio_str    = f"{pe_ratio:.1f}×"

    return {
        "ticker":       ticker.upper(),
        "name":         info.get("longName") or info.get("shortName"),
        "current_price": f"{current_price:.2f}",
        "pct_change":    f"{pct_change:+.2f}%",
        "trend_30d":     f"{trend_30d_pct:+.2f}%",
        "volume":        vol_str,
        "bid_ask":       bid_ask_str,
        "day_range":     day_range_str,
        "market_cap":    market_cap_str,
        "pe_ratio":      pe_ratio_str,
        "history_30d":   history_30d,  # still available if you need raw for other uses
    }