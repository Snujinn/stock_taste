from app.core.database import SessionLocal
from app.models.ticker import Ticker

def update_names():
    db = SessionLocal()
    try:
        # Mapping of Symbol -> Korean Name
        korean_names = {
            "AAPL": "애플",
            "MSFT": "마이크로소프트",
            "AMZN": "아마존",
            "GOOGL": "구글 (알파벳)",
            "META": "메타 (페이스북)",
            "NVDA": "엔비디아",
            "TSLA": "테슬라",
            "JPM": "JP모건 체이스",
            "BAC": "뱅크 오브 아메리카",
            "V": "비자",
            "MA": "마스터카드",
            "BRK.B": "버크셔 해서웨이",
            "UNH": "유나이티드 헬스",
            "JNJ": "존슨앤존슨",
            "PG": "P&G (프록터 앤 갬블)",
            "KO": "코카콜라",
            "PEP": "펩시코",
            "COST": "코스트코",
            "XOM": "엑슨모빌",
            "DIS": "월트 디즈니"
        }

        print("Updating ticker names...")
        tickers = db.query(Ticker).all()
        for ticker in tickers:
            if ticker.symbol in korean_names:
                ticker.name = korean_names[ticker.symbol]
                print(f"Updated {ticker.symbol} -> {ticker.name}")
        
        db.commit()
        print("Done.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_names()
