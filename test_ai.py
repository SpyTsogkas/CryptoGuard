import pandas as pd
import numpy as np
from ai_engine import TrendPredictor

def run_test():
    # 1. Create 50 days of OHLC data
    np.random.seed(42)
    data = []
    curr = 60000
    for i in range(50):
        o = curr + np.random.randint(-100, 100)
        c = o + np.random.randint(-200, 300)
        h = max(o, c) + 50
        l = min(o, c) - 50
        data.append([o, h, l, c])
        curr = c
    
    # We use 'close' instead of 'price' now!
    df = pd.DataFrame(data, columns=['open', 'high', 'low', 'close'])

    # 2. Run AI
    predictor = TrendPredictor()
    try:
        predictor.train(df)
        res = predictor.predict_future(df)
        
        print("\n" + "="*40)
        print(f"💰 CURRENT PRICE: ${df['close'].iloc[-1]:,.2f}")
        print(f"🎯 AI TARGET:    ${res['target_price']:,.2f}")
        print(f"🕒 HORIZON:      {res['time_horizon']}")
        print(f"🚦 SIGNAL:       {res['signal']}")
        print(f"📏 ERROR (MAE):  ${res['mae']}")
        print("="*40 + "\n")
        
    except Exception as e:
        print(f"❌ Still getting error: {e}")

if __name__ == "__main__":
    run_test()