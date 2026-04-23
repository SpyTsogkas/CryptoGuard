import pandas as pd
import numpy as np
import logging
from ai_engine import TrendPredictor
from backend import DataFetcher
from database import DataBaseManager


# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_integration_test():
    print("\n" + "="*50)
    print(" 🛡️ CRYPTO-GUARD SYSTEM INTEGRATION TEST")
    print("="*50)

    # 1. Initialization (Αρχικοποίηση όλων των συστημάτων)
    try:
        api = DataFetcher()
        ai = TrendPredictor()
        db = DataBaseManager()
        logging.info("System components initialized successfully.")
    except Exception as e:
        logging.error(f"Initialization Failed: {e}")
        return

    # 2. Data Fetching (Λήψη πραγματικών δεδομένων)
    symbol = 'bitcoin'
    print(f"\n[STEP 1] Fetching live data for {symbol.upper()}...")
    df = api.get_data(symbol, days='30')

    if df.empty:
        logging.error("No data fetched. Test aborted.")
        return

    # 3. AI Training & Prediction (Εκπαίδευση και Πρόβλεψη)
    print(f"\n[STEP 2] Training AI and generating prediction...")
    try:
        ai.train(df)
        results = ai.predict_future(df)
        current_price = df['close'].iloc[-1]
    except Exception as e:
        logging.error(f"AI Processing Error: {e}")
        return

    # 4. Database Logging (Αποθήκευση στη Βάση Δεδομένων)
    print(f"\n[STEP 3] Saving results to SQLite Database...")
    db_status = db.log_prediction(symbol, current_price, results)
    
    if db_status:
        logging.info("Prediction successfully logged to database.")
    else:
        logging.warning("Database logging failed.")

    # 5. Final Report (Εμφάνιση αποτελεσμάτων)
    print("\n" + "="*50)
    print(f"✅ INTEGRATION TEST COMPLETE FOR {symbol.upper()}")
    print("-" * 50)
    print(f"Current Market Price : ${current_price:,.2f}")
    print(f"AI Target Price      : ${results['target_price']:,.2f}")
    print(f"Signal Strength      : {results['signal']}")
    print(f"Forecast Horizon     : {results['time_horizon']}")
    print(f"Confidence (MAE)     : ${results['mae']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_integration_test()