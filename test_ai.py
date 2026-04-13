import pandas as pd
import numpy as np
from sklearn.metrics import r2_score
from ai_engine import TrendPredictor

def run_detailed_test():
    # 1. Generate 50 days of synthetic data
    np.random.seed(42)
    base_price = 60000
    prices = []
    for i in range(50):
        # Create a trend with some randomness
        base_price += 100 + np.random.normal(0, 300) 
        prices.append(base_price)
    
    df = pd.DataFrame({'price': prices})

    # 2. Initialize and Train
    predictor = TrendPredictor()
    predictor.train(df)

    # 3. Get metrics for the numbers part
    # We need to process features to get predictions for the whole set
    processed_df = predictor._prepare_features(df)
    feature_cols = ['RSI', 'Upper_Band', 'Lower_Band', 'price_yesterday', 'price_2_days_ago']
    y_true = processed_df['price']
    y_pred = predictor.model.predict(processed_df[feature_cols])

    # --- CALCULATING NUMBERS ---
    mae = predictor.mae_score
    mape = (mae / y_true.mean()) * 100
    r2 = r2_score(y_true, y_pred)
    next_price = predictor.predict_next(df)
    current_price = df['price'].iloc[-1]
    change_pct = ((next_price - current_price) / current_price) * 100

    # 4. Detailed Output
    print("="*40)
    print("📊 AI MODEL DETAILED PERFORMANCE")
    print("="*40)
    print(f"Total Data Points:    {len(df)} days")
    print(f"Training Samples:     {len(processed_df)} (after indicators)")
    print("-" * 40)
    print(f"MAE (Avg. Error):     ${mae:.2f}")
    print(f"MAPE (Rel. Error):    {mape:.2f}%")
    print(f"R² Score (Fit):       {r2:.4f} (Best is 1.0)")
    print("-" * 40)
    print(f"Current Price:        ${current_price:.2f}")
    print(f"AI Prediction:        ${next_price:.2f}")
    print(f"Predicted Change:     {change_pct:+.2f}%")
    
    rating, color = predictor.get_accuracy_report(current_price)
    print(f"Model Reliability:    {rating}")
    print("="*40)

if __name__ == "__main__":
    run_detailed_test()