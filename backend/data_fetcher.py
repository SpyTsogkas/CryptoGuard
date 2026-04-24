import pandas as pd
import numpy as np
import logging
import requests
import time # Για αποφυγή rate limits
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFetcher:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def get_top_10_by_volume(self):
        """Φέρνει δυναμικά τα 10 νομίσματα με το μεγαλύτερο Trading Volume (24h)."""
        endpoint = f"{self.base_url}/coins/markets"
        params = {
            'vs_currency': 'usd',
            'order': 'volume_desc', # Ταξινόμηση βάσει όγκου συναλλαγών
            'per_page': 10,
            'page': 1
        }
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            # Επιστρέφει μια λίστα με τα IDs (π.χ. ['bitcoin', 'ethereum', ...])
            return [coin['id'] for coin in data]
        except Exception as e:
            logging.error(f"Error fetching top coins: {e}")
            return ['bitcoin', 'ethereum', 'solana'] # Fallback λίστα

    def get_data(self, symbol: str, days: str = '30') -> pd.DataFrame:
        endpoint = f"{self.base_url}/coins/{symbol.lower()}/ohlc"
        params = {'vs_currency': 'usd', 'days': days}
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logging.error(f"Error fetching {symbol}: {e}")
            return pd.DataFrame()

# (Η κλάση TrendPredictor παραμένει ως είχε στον κώδικά σου)
class TrendPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=500, max_depth=12, random_state=42, n_jobs=-1)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.mae_score = 0.0

    def _safe_data_check(self, df):
        if 'price' in df.columns and 'close' not in df.columns:
            df = df.rename(columns={'price': 'close'})
        for col in ['open', 'high', 'low']:
            if col not in df.columns: df[col] = df['close']
        return df

    def _identify_candle_patterns(self, df):
        body = df['close'] - df['open']
        abs_body = body.abs()
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        df['is_hammer'] = ((lower_shadow > (2 * abs_body)) & (upper_shadow < (0.1 * abs_body))).astype(int)
        df['is_bullish_engulfing'] = ((body > 0) & (body.shift(1) < 0) & (abs_body > abs_body.shift(1))).astype(int)
        return df

    def _calculate_indicators(self, data: pd.DataFrame):
        df = self._safe_data_check(data.copy())
        df['EMA_10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['ATR'] = (df['high'] - df['low']).rolling(window=14).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain / (loss + 1e-9))))
        df = self._identify_candle_patterns(df)
        return df.dropna()

    def train(self, historical_data: pd.DataFrame):
        df = self._calculate_indicators(historical_data)
        features = ['EMA_10', 'SMA_20', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        X, y = df[features], df['close']
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.mae_score = mean_absolute_error(y, self.model.predict(X_scaled))
        self.is_trained = True

    def predict_future(self, current_data: pd.DataFrame):
        df = self._calculate_indicators(current_data).tail(1)
        features = ['EMA_10', 'SMA_20', 'RSI', 'ATR', 'is_hammer', 'is_bullish_engulfing']
        X_latest = self.scaler.transform(df[features])
        prediction = self.model.predict(X_latest)[0]
        signal, horizon = "NEUTRAL", "1-2 Days"
        if df['is_hammer'].values[0] == 1 or df['is_bullish_engulfing'].values[0] == 1:
            signal, horizon = "BULLISH (Pattern Detected)", "3-5 Days"
        return {"target_price": round(float(prediction), 2), "signal": signal, "time_horizon": horizon, "mae": round(self.mae_score, 2)}

# --- Updated Testing Block για τα Top 10 Volume Coins ---
if __name__ == "__main__":
    print("🚀 Εκκίνηση Ανάλυσης Top 10 Volume Cryptos...")
    api = DataFetcher()
    ai = TrendPredictor()
    
    # Λήψη των 10 κορυφαίων
    top_10 = api.get_top_10_by_volume()
    
    for coin in top_10:
        print(f"\nΑναλύεται το: {coin.upper()}...")
        df = api.get_data(coin, days='30')
        
        if not df.empty:
            ai.train(df)
            results = ai.predict_future(df)
            
            # Υπολογισμός μεταβολής (%)
            current_price = df['close'].iloc[-1]
            change = ((results['target_price'] - current_price) / current_price) * 100
            sign = "+" if change > 0 else ""

            print(f"═" * 40)
            print(f"💰 COIN          : {coin.upper()}")
            print(f"💵 CURRENT PRICE : ${current_price:,.2f}")
            print(f"🎯 TARGET PRICE  : ${results['target_price']:,.2f} ({sign}{change:.2f}%)")
            print(f"🚦 SIGNAL        : {results['signal']}")
            print(f"⏱️ TIME HORIZON  : {results['time_horizon']}")
            print(f"📉 ERROR (MAE)   : ${results['mae']}")
            print(f"═" * 40)
            
            # Μικρή παύση για να μην μας "κόψει" το API της CoinGecko
            time.sleep(1) 
        else:
            print(f"⚠️ Αδυναμία λήψης δεδομένων για {coin}")