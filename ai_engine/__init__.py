import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

class TrendPredictor:
    def __init__(self):
        """
        Initialize the AI Engine with a Random Forest Regressor.
        Hyperparameters are tuned to prevent overfitting.
        """
        self.model = RandomForestRegressor(
            n_estimators=200,    # Number of trees in the forest
            max_depth=10,        # Maximum depth of each tree
            min_samples_split=5, # Minimum samples required to split a node
            random_state=42      # Ensures consistent results across runs
        )
        self.mae_score = 0.0

    def _prepare_features(self, data: pd.DataFrame):
        """
        Feature Engineering: Convert raw prices into technical indicators.
        """
        df = data.copy()
        
        # 1. Momentum Indicator: RSI (Relative Strength Index)
        # Measures the speed and change of price movements
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9) # Avoid division by zero
        df['RSI'] = 100 - (100 / (1 + rs))

        # 2. Volatility Indicators: Bollinger Bands
        # Standard deviation bands around a moving average
        sma_20 = df['price'].rolling(window=20).mean()
        std_20 = df['price'].rolling(window=20).std()
        df['Upper_Band'] = sma_20 + (std_20 * 2)
        df['Lower_Band'] = sma_20 - (std_20 * 2)

        # 3. Memory Features: Lags
        # Provides the model with knowledge of previous days' prices
        df['price_yesterday'] = df['price'].shift(1)
        df['price_2_days_ago'] = df['price'].shift(2)

        # Drop rows with NaN values created by moving windows and lags
        df = df.dropna()
        return df

    def train(self, data: pd.DataFrame):
        """
        Train the model using technical indicators and calculate MAE.
        """
        df = self._prepare_features(data)
        
        # Define features used for prediction
        feature_cols = ['RSI', 'Upper_Band', 'Lower_Band', 'price_yesterday', 'price_2_days_ago']
        X = df[feature_cols]
        y = df['price']
        
        # Training phase
        self.model.fit(X, y)
        
        # Calculate training error (Mean Absolute Error)
        predictions = self.model.predict(X)
        self.mae_score = mean_absolute_error(y, predictions)

    def predict_next(self, last_data: pd.DataFrame) -> float:
        """
        Predict the price for the next day using the latest market data.
        """
        processed = self._prepare_features(last_data).tail(1)
        feature_cols = ['RSI', 'Upper_Band', 'Lower_Band', 'price_yesterday', 'price_2_days_ago']
        X_new = processed[feature_cols]
        
        prediction = self.model.predict(X_new)[0]
        return float(prediction)

    def get_accuracy_report(self, current_price: float):
        """
        Calculate relative error (MAPE) and return a human-friendly rating.
        """
        # Calculate Mean Absolute Percentage Error
        mape = (self.mae_score / current_price) * 100
        
        if mape < 2.0:
            return "High Reliability", "#22c55e"    # Green
        elif mape < 5.0:
            return "Medium Reliability", "#f59e0b"  # Orange
        else:
            return "Low Reliability", "#ef4444"     # Red