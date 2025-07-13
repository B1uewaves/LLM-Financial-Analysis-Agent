# yfinance integration tool

def get_stock_data(ticker):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    return stock.history(period="1mo")
