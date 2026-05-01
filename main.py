import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from database.db_manager import DataBaseManager
from ui.dashboard import LoginScreen, DashBoardUI

class CryptoGuardApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion") # Για ομοιόμορφο look σε όλα τα OS
        
        self.db = DataBaseManager()
        self.stack = QStackedWidget()
        
        # Αρχικοποίηση Login
        self.login = LoginScreen(self.db, self.show_dashboard)
        self.stack.addWidget(self.login)
        self.stack.setFixedSize(450, 550)
        self.stack.show()

    def show_dashboard(self, username, risk):
        # Μετάβαση στο Dashboard
        self.dashboard = DashBoardUI(username, risk)
        self.stack.addWidget(self.dashboard)
        self.stack.setCurrentWidget(self.dashboard)
        
        # Resize για το Dashboard
        self.stack.setFixedSize(1200, 850)
        
        # Κεντράρισμα παραθύρου
        center = self.app.primaryScreen().availableGeometry().center()
        geo = self.stack.frameGeometry()
        geo.moveCenter(center)
        self.stack.move(geo.topLeft())

if __name__ == "__main__":
    runner = CryptoGuardApp()
    sys.exit(runner.app.exec())