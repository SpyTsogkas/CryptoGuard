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
        Multi-Horizon Quant-Pro Engine.
        Trains multiple models for different time horizons.
        """
        self.horizons = {
            "1 Ημέρα (24h)": 1,
            "1 Εβδομάδα": 7,
            "2 Εβδομάδες": 14,
            "1 Μήνας": 30,
        }
        
        # Create an AI model and a Scaler for each time horizon
        self.models = {
            name: RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1) 
            for name in self.horizons
        }
        self.scalers = {name: StandardScaler() for name in self.horizons}
        
        self.is_trained = False
        self.mae_scores = {}

    def _safe_data_check(self, df):
        """Ensures the dataframe has the correct column names (OHLC)."""
        if 'price' in df.columns and 'close' not in df.columns:
            df = df.rename(columns={'price': 'close'})
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
        """Calculates Technical Indicators (EMA, SMA, RSI, ATR) + Candlestick Patterns."""
        df = self._safe_data_check(data.copy())
        
        df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        # Add long-term trend indicator
        df['SMA_50'] = df['close'].rolling(window=50).mean() 
        df['ATR'] = (df['high'] - df['low']).rolling(window=14).mean()
        
        # RSI Logic
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))

        df = self._identify_candle_patterns(df)
        return df

    def train(self, historical_data: pd.DataFrame):
        """Trains separate models by predicting shifted future targets."""
        df = self._calculate_indicators(historical_data)
        features = ['EMA_10', 'SMA_20', 'SMA_50', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        
        for horizon_name, days_ahead in self.horizons.items():
            df_horizon = df.copy()
            # The "secret" of forecasting: Ask the AI to guess the price X days LATER
            df_horizon['future_target'] = df_horizon['close'].shift(-days_ahead)
            
            # Remove rows that don't have future data (NaN)
            train_data = df_horizon.dropna(subset=features + ['future_target'])
            
            if len(train_data) < 10:
                logging.warning(f"Not enough data to train for horizon: {horizon_name}")
                self.mae_scores[horizon_name] = None
                continue
                
            X = train_data[features]
            y = train_data['future_target']
            
            X_scaled = self.scalers[horizon_name].fit_transform(X)
            self.models[horizon_name].fit(X_scaled, y)
            
            self.mae_scores[horizon_name] = mean_absolute_error(y, self.models[horizon_name].predict(X_scaled))
            
        self.is_trained = True

    def predict_future(self, current_data: pd.DataFrame):
        """Generates multi-horizon predictions for the UI."""
        df = self._calculate_indicators(current_data).tail(1)
        features = ['EMA_10', 'SMA_20', 'SMA_50', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        
        predictions = {}
        current_price = df['close'].values[0]
        base_signal = "BULLISH" if df['is_hammer'].values[0] or df['is_bullish_engulfing'].values[0] else "NEUTRAL"
        
        # Generate macroeconomic text for the UI
        macro_text = "\n\n📅 ΠΡΟΒΛΕΨΕΙΣ ΠΟΛΛΑΠΛΩΝ ΟΡΙΖΟΝΤΩΝ (MACRO ANALYSIS):\n"
        
        for horizon_name in self.horizons:
            if self.mae_scores.get(horizon_name) is None:
                continue
                
            X_latest = self.scalers[horizon_name].transform(df[features])
            pred_val = self.models[horizon_name].predict(X_latest)[0]
            
            mae = self.mae_scores[horizon_name]
            change_pct = ((pred_val - current_price) / current_price) * 100
            sign = "+" if change_pct > 0 else ""
            
            predictions[horizon_name] = {
                "target": round(float(pred_val), 2),
                "mae": round(mae, 2),
                "change": round(change_pct, 2)
            }
            
            macro_text += f"• {horizon_name}: ${pred_val:,.2f} ({sign}{change_pct:.2f}%) | Ακρίβεια (MAE): ±${mae:,.2f}\n"

        # Set "1 Month" as the main prediction for the central UI numbers 
        # (if not available, fallback to 1 Week)
        main_horizon = "1 Μήνας" if "1 Μήνας" in predictions else "1 Εβδομάδα"
        main_pred = predictions.get(main_horizon, {"target": current_price, "mae": 0})

        return {
            "target_price": main_pred["target"],
            "signal": base_signal,
            "time_horizon": main_horizon,
            "mae": main_pred["mae"],
            "macro_text": macro_text # The text to be appended to the advice
        }