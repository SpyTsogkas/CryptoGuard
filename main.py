from ai_engine import TrendPredictor
from backend import DataFetcher
from database import DataBaseManager
from ui import ProfessionalDashboard

def main():
    print("--- Starting Crypto-Guard Test ---")
    
    # 1. Initialize the objects
    api_fetcher = DataFetcher()
    ai_engine = TrendPredictor()

    # 2. Fetch real data (e.g., for Bitcoin)
    print("Waiting to fetch data from the API...")
    real_crypto_data = api_fetcher.get_data(symbol='bitcoin', days='30')

    # 3. Check if data was received and send it to the AI
    if not real_crypto_data.empty:
        print("Data fetched successfully. Training the AI...")
        
        # Train with real data
        ai_engine.train(real_crypto_data)
        
        # Generate Prediction
        final_prediction = ai_engine.predict_future(real_crypto_data)
        
        print("\n[ FINAL RESULTS ]")
        print(f"Target Price   : ${final_prediction['target_price']}")
        print(f"Signal         : {final_prediction['signal']}")
        print(f"Accuracy (MAE) : {final_prediction['mae']}")
    else:
        print("Error: Could not fetch data from the CoinGecko API.")

# Execute the main function when running this file directly
if __name__ == "__main__":
    main()