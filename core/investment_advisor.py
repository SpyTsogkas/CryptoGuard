from backend import DataFetcher
from ai_engine import TrendPredictor
from database import DataBaseManager

class InvestmentAdvisor:
    def __init__(self, risk_profile="Moderate", investment_amount=1000.0):
        """
        Constructor: Initializes the user settings and the modules.
        """
        self.risk_profile = risk_profile
        self.amount = investment_amount
        
        # Initialization of the other classes
        self.fetcher = DataFetcher()
        self.predictor = TrendPredictor()
        self.db = DataBaseManager()

    def generate_advice(self, symbol):
        """
        The main methon which is called by the run_system.py.
        Organizes the flow: Data -> AI -> DB -> Advice.
        """
        # 1. Data Downloading from the API
        df = self.fetcher.get_data(symbol)
        if df.empty:
            return {"error": "Αδυναμία λήψης δεδομένων από το API."}

        # 2. Training and Prediction from the AI
        self.predictor.train(df)
        prediction = self.predictor.predict_future(df)
        current_price = df['close'].iloc[-1]

        # --- NEW CALCULATION LINE ---
        change_pct = ((prediction['target_price'] - current_price) / current_price) * 100

        # 3. Save the result in the Databasae
        self.db.log_prediction(symbol, current_price, prediction)

        # 4. Producing final advice based on the risk profile
        advice_text = self._logic_engine(prediction, current_price)
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "prediction": prediction, 
            "advice": advice_text,
            "error_margin": prediction['mae'],
            "time_limit": prediction['time_horizon'],
            "price_change_pct": round(change_pct, 2)  # --- ΝΕΑ ΓΡΑΜΜΗ ΣΤΟ RETURN ---
        }

    def _logic_engine(self, prediction, current_price):
        """
        Decision Support Logic: Transforms the "numbers" to "human - friendly" advise.
        """
        target = prediction['target_price']
        signal = prediction['signal']
        horizon = prediction['time_horizon']
        
        # Calculating percentage change
        price_diff_pct = ((target - current_price) / current_price) * 100
        
        # Signal and risk profile based logic
        # --- 1. (BULLISH) ---
        if price_diff_pct > 0.5:
            if self.risk_profile == "Aggressive":
                return (f"ΕΝΤΟΝΗ ΑΓΟΡΑ (Strong Buy). Αναμένεται άνοδος {price_diff_pct:.2f}% "
                        f"εντός των επόμενων {horizon}. Στόχος: ${target:,.2f}. Ιδανικό για άμεση τοποθέτηση.")
            else:
                return (f"ΠΡΟΣΕΚΤΙΚΗ ΑΓΟΡΑ. Εντοπίστηκε ανοδικό pattern. "
                        f"Προτεινόμενος ορίζοντας: {horizon}. Στόχος: ${target:,.2f}.")

        # --- 2. (BEARISH) ---
        elif price_diff_pct < -0.5:
            if self.risk_profile == "Aggressive":
                return (f"ΕΝΤΟΝΗ ΠΩΛΗΣΗ (Strong Sell / Short). Αναμένεται πτώση {abs(price_diff_pct):.2f}% "
                        f"εντός {horizon}. Δυνατότητα κέρδους από πτώση έως τα ${target:,.2f}.")
            else:
                return (f"ΕΞΟΔΟΣ / ΠΩΛΗΣΗ. Εντοπίστηκε καθοδική τάση. Προστατέψτε το κεφάλαιό σας. "
                        f"Αναμονή υποχώρησης στα ${target:,.2f} πριν από νέα είσοδο.")

        # --- 3. (NEUTRAL) ---
        elif abs(price_diff_pct) <= 0.5:
            return (f"ΔΙΑΤΗΡΗΣΗ ΘΕΣΗΣ (Hold). Η αγορά είναι σταθερή (μεταβολή {price_diff_pct:.2f}%). "
                    f"Αναμονή για τις επόμενες {horizon} για καθαρότερη τάση.")
        
        # --- 4. GENERAL NEUTRALITY ---
        else:
            return "Σύσταση: Ουδέτερη στάση (Neutral). Επανεκτίμηση της αγοράς σε 24 ώρες λόγω ασάφειας."