from core import InvestmentAdvisor

advisor = InvestmentAdvisor(risk_profile="Aggressive")
print(advisor.generate_advice("bitcoin"))