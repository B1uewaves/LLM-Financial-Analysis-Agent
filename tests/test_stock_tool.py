import pytest
from tools.stock_tool import fetch_stock_data

@pytest.mark.parametrize("ticker", ["AAPL", "MSFT", "GOOGL"])
def test_fetch_stock_data_structure(ticker):
    data = fetch_stock_data(ticker)
    # Basic keys exist
    expected_keys = {"ticker", "name", "current_price", "history_30d"}
    assert expected_keys.issubset(data.keys()), f"Missing keys in {data.keys()}"

    # Types are correct
    assert isinstance(data["ticker"], str)
    assert data["ticker"] == ticker.upper()
    assert isinstance(data["name"], str) or data["name"] is None
    assert isinstance(data["current_price"], (int, float)) or data["current_price"] is None
    assert isinstance(data["history_30d"], list)

    # If history is non-empty, all entries should be numeric
    if data["history_30d"]:
        assert all(isinstance(p, (int, float)) for p in data["history_30d"])

def test_fetch_stock_data_invalid_ticker():
    # An invalid ticker should not crash; it may return None or empty history
    data = fetch_stock_data("INVALID_TICKER_123")
    assert isinstance(data, dict)
    # At minimum, ticker field should echo back the input
    assert data.get("ticker") == "INVALID_TICKER_123"
    # history_30d should be a list (even if empty)
    assert isinstance(data.get("history_30d"), list)
