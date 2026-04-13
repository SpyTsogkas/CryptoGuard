import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class CryptoPredictor:
    def __init__(self):
        self.model = LinearRegression()

    def _calculate_volatility(self, prices):
        """Υπολογίζει το ρίσκο βάσει τυπικής απόκλισης"""
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        if volatility < 0.02: return "Low"
        if volatility < 0.05: return "Moderate"
        return "High"

    def predict(self, history_data):
        """
        history_data: Λίστα με τιμές κλεισίματος (π.χ. τελευταίες 30 μέρες)
        """
        df = pd.DataFrame(history_data, columns=['price'])
        df['day'] = np.arange(len(df))
        
        # Εκπαίδευση 'on the fly' για την τάση των τελευταίων ημερών
        X = df[['day']]
        y = df['price']
        self.model.fit(X, y)
        
        # Πρόβλεψη επόμενης ημέρας
        next_day = np.array([[len(df)]])
        prediction = self.model.predict(next_day)[0]
        
        # Λογική Τάσης
        last_price = history_data[-1]
        trend = "BULLISH" if prediction > last_price else "BEARISH"
        
        # Υπολογισμός Confidence (πολύ απλοποιημένο για αρχή)
        confidence = round(self.model.score(X, y) * 100, 2)
        
        return {
            "trend": trend,
            "confidence": f"{confidence}%",
            "risk": self._calculate_volatility(np.array(history_data)),
            "predicted_price": round(prediction, 2)
        }

# Παράδειγμα χρήσης για δοκιμή
if __name__ == "__main__":
    # Dummy data: Τιμές Bitcoin που ανεβαίνουν
    test_data = [60000, 60500, 61000, 60800, 62000, 62500, 63000]
    ai = CryptoPredictor()
    result = ai.predict(test_data)
    print(f"Result for Backend: {result}")