import logging
from app.core.database import SessionLocal, engine, Base
from app.models.ticker import Ticker

# Import all models so Base.metadata has them
from app.models import user, holding, order

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if tickers exist
        if db.query(Ticker).first():
            print("Tickers already seeded.")
            return

        tickers = [
            "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA",
            "JPM", "BAC", "V", "MA", "BRK.B", "UNH",
            "JNJ", "PG", "KO", "PEP", "COST",
            "XOM", "DIS"
        ]
        print(f"Seeding {len(tickers)} tickers...")
        for symbol in tickers:
            db.add(Ticker(symbol=symbol))
        db.commit()
        print("Done.")
    except Exception as e:
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
