import yfinance as yf

def get_last_price(symbol):
    ticker_yahoo = yf.Ticker(symbol)
    data = ticker_yahoo.history()
    print("Data length:", len(data))
    if len(data) == 0:
        print("No data available for symbol:", symbol)
        return None
    last_quote = data['Close'].iloc[-1]
    last_quote = round(last_quote, 2)
    return last_quote

# aapl = yf.Ticker("AAPL")
# data = aapl.history()
# print(data['Close'].iloc[-1])
