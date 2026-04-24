import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

# Professional logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TrendPredictor:
    def __init__(self):
        """
        Finalized Quant-Pro Engine. 
        Supports OHLC data and Candlestick Pattern Recognition.
        """
        self.model = RandomForestRegressor(
            n_estimators=500, 
            max_depth=12,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.mae_score = 0.0

    def _safe_data_check(self, df):
        """Ensures the dataframe has the correct column names (OHLC)."""
        # If the backend sends 'price' instead of 'close', we rename it
        if 'price' in df.columns and 'close' not in df.columns:
            df = df.rename(columns={'price': 'close'})
        
        # For Quant analysis, we need high/low/open. If missing, we simulate them from close.
        for col in ['open', 'high', 'low']:
            if col not in df.columns:
                df[col] = df['close']
        return df

    def _identify_candle_patterns(self, df):
        """Identifies Hammer and Engulfing patterns from price action."""
        body = df['close'] - df['open']
        abs_body = body.abs()
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']

        # Bullish Hammer detection
        df['is_hammer'] = ((lower_shadow > (2 * abs_body)) & (upper_shadow < (0.1 * abs_body))).astype(int)
        
        # Bullish Engulfing detection
        df['is_bullish_engulfing'] = ((body > 0) & (body.shift(1) < 0) & (abs_body > abs_body.shift(1))).astype(int)
        
        return df

    def _calculate_indicators(self, data: pd.DataFrame):
        """Calculates Math Indicators (EMA, RSI, ATR) + Candlestick Patterns."""
        df = self._safe_data_check(data.copy())
        
        # Technical Math
        df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['ATR'] = (df['high'] - df['low']).rolling(window=14).mean()
        
        # RSI Logic
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

        # Candlestick Logic
        df = self._identify_candle_patterns(df)

        return df.dropna()

    def train(self, historical_data: pd.DataFrame):
        """Trains the AI on 10 combined features (Math + Patterns)."""
        df = self._calculate_indicators(historical_data)
        
        features = ['EMA_10', 'SMA_20', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        X = df[features]
        y = df['close']
        
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        
        self.mae_score = mean_absolute_error(y, self.model.predict(X_scaled))
        self.is_trained = True

    def predict_future(self, current_data: pd.DataFrame):
        df = self._calculate_indicators(current_data).tail(1)
        features = ['EMA_10', 'SMA_20', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        
        X_latest = self.scaler.transform(df[features])
        prediction = self.model.predict(X_latest)[0]
        current_price = df['close'].values[0]
        latest_atr = df['ATR'].values[0]

        # Estimated Time Calculation (Volatility-Adjusted)
        price_diff = abs(prediction - current_price)
        # If the difference is 100$ and the volitality (ATR) is 50$ per day, then we want 2 days
        # Add "the safe" (1e-9) to avoid devision by 0
        est_days = price_diff / (latest_atr + 1e-9)
        est_hours = round(est_days * 24)
        
        # Logical Limitation (e.x from 1 to 120 hours)
        est_hours = max(1, min(est_hours, 120))

        return {
            "target_price": round(float(prediction), 2),
            "signal": "BULLISH" if df['is_hammer'].values[0] or df['is_bullish_engulfing'].values[0] else "NEUTRAL",
            "time_horizon": f"{est_hours} Hours",
            "estimated_hours": est_hours,
            "mae": round(self.mae_score, 2)
        }