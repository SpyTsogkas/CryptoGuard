import sys
from PyQt6.QtWidgets import QApplication
from ui.dashboard import DashBoardUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashBoardUI(username="User", risk_level="Moderate")
    window.show()
    sys.exit(app.exec())