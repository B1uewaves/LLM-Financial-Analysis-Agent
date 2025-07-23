import re
import pytest
from tools.stock_tool import fetch_stock_data

@ pytest.mark.parametrize("ticker", ["AAPL", "MSFT", "GOOGL"])
def test_fetch_stock_data_structure(ticker):
    data = fetch_stock_data(ticker)
    # Basic keys exist
    expected_keys = {"ticker", "name", "current_price", "history_30d"}
    assert expected_keys.issubset(data.keys()), f"Missing keys in {data.keys()}"

    # Types are correct
    assert isinstance(data["ticker"], str)
    assert data["ticker"] == ticker.upper()
    # name can be None or str
    assert isinstance(data["name"], str) or data["name"] is None

    # current_price is a formatted string like '123.45'
    assert isinstance(data["current_price"], str), \
        f"Expected current_price as string, got {type(data['current_price'])}"
    assert re.match(r"^\d+\.\d{2}$", data["current_price"]), \
        f"Price string format incorrect: {data['current_price']}"

    # history_30d is a list of floats (or ints)
    assert isinstance(data["history_30d"], list)
    assert all(isinstance(x, (float, int)) for x in data["history_30d"]), \
        "All history_30d elements must be numeric"


def test_fetch_stock_data_invalid_ticker():
    data = fetch_stock_data("INVALID_TICKER_123")
    assert isinstance(data, dict)
    # Should return an error message
    assert "error" in data, "Expected 'error' key for invalid ticker"
    # The error message should mention the ticker symbol
    assert "INVALID_TICKER_123" in data["error"], \
        f"Error message should include ticker: {data['error']}"
