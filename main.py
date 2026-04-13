import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import DashboardUI

def main():
    app = QApplication(sys.argv)
    
    # Δημιουργία του UI
    window = DashboardUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()