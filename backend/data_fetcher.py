import pandas as pd
import numpy as np
import logging
import requests
import time 
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

# Professional logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    def __init__(self):
        # Use the demo-api domain for free/demo API keys
        self.base_url = "https://api.coingecko.com/api/v3"
        # REPLACE THIS WITH YOUR ACTUAL API KEY
        self.api_key = "CG-nhGYGEwsYHzH3zL9cwcw81Ue" 

    def get_headers(self):
        """Returns the necessary headers for CoinGecko API authentication."""
        return {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }

    def get_top_10_by_volume(self):
        """Dynamically fetches the top 10 Cryptos by 24h trading volume."""
        endpoint = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'volume_desc',
            'per_page': 10,
            'page': 1
        }
        try:
            response = requests.get(endpoint, params=params, headers=self.get_headers())
            response.raise_for_status()
            data = response.json()
            return [coin['id'] for coin in data]
        except Exception as e:
            logging.error(f"Error fetching top coins: {e}")
            return ['bitcoin', 'ethereum', 'solana']

    def get_data(self, symbol: str, days: str = '365') -> pd.DataFrame:
        """Fetches historical OHLC data for a specific asset."""
        endpoint = f"{self.base_url}/coins/{symbol.lower()}/ohlc"
        params = {'vs_currency': 'usd', 'days': days}
        try:
            response = requests.get(endpoint, params=params, headers=self.get_headers())
            response.raise_for_status()
            data = response.json()
            
            if not data: return pd.DataFrame()

            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logging.error(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

class TrendPredictor:
    def __init__(self):
        """
        Multi-Horizon AI Engine.
        Trains models for 1 Day, 1 Week, 1 Month, and 1 Year.
        """
        self.horizons = {
            "1 Day (24h)": 1,
            "1 Week": 7,
            "1 Month": 30,
            "1 Year": 365
        }
        # Dictionary to store separate models and scalers for each timeframe
        self.models = {name: RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1) for name in self.horizons}
        self.scalers = {name: StandardScaler() for name in self.horizons}
        self.is_trained = False
        self.mae_scores = {}

    def _safe_data_check(self, df):
        """Standardizes column names and fills missing OHLC data."""
        if 'price' in df.columns and 'close' not in df.columns:
            df = df.rename(columns={'price': 'close'})
        for col in ['open', 'high', 'low']:
            if col not in df.columns: df[col] = df['close']
        return df

    def _identify_candle_patterns(self, df):
        """Detects Hammer and Bullish Engulfing candlestick patterns."""
        body = df['close'] - df['open']
        abs_body = body.abs()
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']

        df['is_hammer'] = ((lower_shadow > (2 * abs_body)) & (upper_shadow < (0.1 * abs_body))).astype(int)
        df['is_bullish_engulfing'] = ((body > 0) & (body.shift(1) < 0) & (abs_body > abs_body.shift(1))).astype(int)
        return df

    def _calculate_indicators(self, data: pd.DataFrame):
        """Calculates EMA, SMA, ATR, RSI and Candlestick patterns."""
        df = self._safe_data_check(data.copy())
        df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['ATR'] = (df['high'] - df['low']).rolling(window=14).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        
        df = self._identify_candle_patterns(df)
        return df

    def train(self, historical_data: pd.DataFrame):
        """Trains individual models for each defined time horizon."""
        df = self._calculate_indicators(historical_data)
        features = ['EMA_10', 'SMA_20', 'SMA_50', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        
        for name, days in self.horizons.items():
            df_horizon = df.copy()
            df_horizon['target'] = df_horizon['close'].shift(-days)
            train_set = df_horizon.dropna(subset=features + ['target'])
            
            if len(train_set) > 20:
                X, y = train_set[features], train_set['target']
                X_scaled = self.scalers[name].fit_transform(X)
                self.models[name].fit(X_scaled, y)
                self.mae_scores[name] = mean_absolute_error(y, self.models[name].predict(X_scaled))
        
        self.is_trained = True

    def predict_future(self, current_data: pd.DataFrame):
        """Predicts future prices across all time horizons."""
        df = self._calculate_indicators(current_data).tail(1)
        features = ['EMA_10', 'SMA_20', 'SMA_50', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        
        results = {}
        for name in self.horizons:
            if name in self.mae_scores:
                X_scaled = self.scalers[name].transform(df[features])
                results[name] = {
                    "price": round(self.models[name].predict(X_scaled)[0], 2),
                    "mae": round(self.mae_scores[name], 2)
                }
        return results

# --- Main Execution Block ---
if __name__ == "__main__":
    print("🚀 Initializing CryptoGuard AI Analysis (Multi-Horizon)...")
    fetcher = DataFetcher()
    predictor = TrendPredictor()
    
    # Get top coins
    top_coins = fetcher.get_top_10_by_volume()
    
    for coin in top_coins:
        print(f"\nProcessing {coin.upper()}...")
        # Fetching maximum history for reliable long-term training
        data = fetcher.get_data(coin, days='365') 
        
        if not data.empty:
            predictor.train(data)
            predictions = predictor.predict_future(data)
            current_price = data['close'].iloc[-1]

            print(f"═" * 50)
            print(f"💰 ASSET: {coin.upper()}")
            print(f"💵 CURRENT PRICE: ${current_price:,.2f}")
            print("-" * 50)
            
            for horizon, pred in predictions.items():
                change = ((pred['price'] - current_price) / current_price) * 100
                sign = "+" if change > 0 else ""
                print(f"🔭 {horizon:12}: ${pred['price']:,.2f} ({sign}{change:.2f}%) | MAE: ±${pred['mae']}")
            
            print(f"═" * 50)
            time.sleep(1) # Delay to respect API rate limits
        else:
            print(f"⚠️ Failed to fetch data for {coin}")