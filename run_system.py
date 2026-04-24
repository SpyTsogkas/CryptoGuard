from core import InvestmentAdvisor

def main():
    print("--- CRYPTO GUARD: SYSTEM START ---")
    
    # 1. Αρχικοποίηση με προφίλ ρίσκου
    advisor = InvestmentAdvisor(risk_profile="Aggressive")
    
    # 2. Εκτέλεση ανάλυσης για το Bitcoin
    symbol = "bitcoin"
    print(f"Εκκίνηση ανάλυσης για: {symbol}...")
    
    result = advisor.generate_advice(symbol)
    
    # --- Εμφάνιση Εμπλουτισμένων Αποτελεσμάτων ---
   # 1. Προσθήκη προσήμου (+/-)
    pct = result['price_change_pct']
    sign = "+" if pct > 0 else ""

    # 2. Εμφάνιση των αποτελεσμάτων
    print("\n" + "═"*55)
    print(f" 💰 ΝΟΜΙΣΜΑ       : {result['symbol'].upper()}")
    print(f" 💵 ΤΡΕΧΟΥΣΑ ΤΙΜΗ : ${result['current_price']:,.2f}")

    # Εδώ εμφανίζεται το ποσοστό που υπολογίζεται πλέον εσωτερικά στον Advisor
    print(f" 🎯 ΣΤΟΧΟΣ AI     : ${result['prediction']['target_price']:,.2f} ({sign}{pct:.2f}%)")
    print(f" ⏱️  ΕΚΤΙΜ. ΧΡΟΝΟΣ : {result['time_limit']}")
    print(f" 📉 ΣΦΑΛΜΑ (MAE)  : ${result['error_margin']:,.2f}")
    print(f" 🚦 ΣΗΜΑ          : {result['prediction']['signal']}")
    print("─" * 55)
    print(f" 💡 ΣΥΜΒΟΥΛΗ: {result['advice']}")
    print("═"*55)
    print("\n[✓] Η πρόβλεψη αποθηκεύτηκε στη βάση δεδομένων.")

if __name__ == "__main__":
    main()