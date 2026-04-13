from ai_engine.predictor import TrendPredictor
from backend.fetcher import DataFetcher

class InvestmentAdvisor:
    def __init__(self):
        self.ai = TrendPredictor()
        self.backend = DataFetcher()

    def get_full_analysis(self, symbol):
        # Αυτή η μέθοδος θα ενώνει τα πάντα
        pass