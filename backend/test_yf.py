import yfinance as yf

def test_yfinance():
    print("Fetching AAPL history...")
    ticker = yf.Ticker("AAPL")
    hist = ticker.history(period="1mo")
    print(hist.head())
    print(f"Data points: {len(hist)}")

if __name__ == "__main__":
    test_yfinance()
