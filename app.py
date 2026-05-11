import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtGui import QPalette, QColor, QFont
from database.db_manager import DataBaseManager 
from ui.dashboard import AuthScreen, DashBoardUI

class CryptoGuardRunner:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion") 
        
        # --- GLOBAL FONT ΣΕ CENTURY GOTHIC BOLD ---
        global_font = QFont("Century Gothic", 10, QFont.Weight.Bold)
        global_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.app.setFont(global_font)

        # Global Dark mode ON
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor("#0B132B"))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor("#FFFFFF"))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor("#1E2D4A"))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#14213D"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#FFFFFF"))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor("#FFFFFF"))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor("#14213D"))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
        dark_palette.setColor(QPalette.ColorRole.Link, QColor("#00E5FF"))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor("#00E5FF"))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
        self.app.setPalette(dark_palette)
        
        self.app.setStyleSheet("* { font-family: 'Century Gothic'; font-weight: bold; } QStackedWidget { background-color: #0B132B; }")
        # --------------------------------

        self.db = DataBaseManager()
        self.window_stack = QStackedWidget()
        self.window_stack.setWindowTitle("CryptoGuard AI Engine")
        
        # Login Screen
        self.auth = AuthScreen(self.db, self.launch_main_ui)
        self.window_stack.addWidget(self.auth)
        
        self.window_stack.setFixedSize(450, 600)
        self.window_stack.show()

    def launch_main_ui(self, username, risk_level):
        """Login --> Dashboard με δυναμική προσαρμογή μεγέθους"""
        self.main_ui = DashBoardUI(username, risk_level)
        self.window_stack.addWidget(self.main_ui)
        self.window_stack.setCurrentWidget(self.main_ui)
        
        # 1. ΑΦΑΙΡΟΥΜΕ ΤΟ setFixedSize(1000, 750)
        # Αντ' αυτού, ορίζουμε ένα ελάχιστο μέγεθος για να μην "καταρρέουν" τα labels
        self.window_stack.setMinimumSize(900, 700) 
        
        # Καταργούμε τον περιορισμό του σταθερού μεγέθους για να μπορεί το παράθυρο να μεγαλώνει
        self.window_stack.setMaximumSize(16777215, 16777215) 

        # 2. ΡΥΘΜΙΖΟΥΜΕ ΤΟ ΠΑΡΑΘΥΡΟ ΝΑ ΠΑΙΡΝΕΙ ΤΟ 90% ΤΗΣ ΔΙΑΘΕΣΙΜΗΣ ΟΘΟΝΗΣ
        screen_geo = self.app.primaryScreen().availableGeometry()
        width = int(screen_geo.width() * 0.9)
        height = int(screen_geo.height() * 0.9)
        self.window_stack.resize(width, height)
        
        # 3. ΚΕΝΤΡΑΡΙΣΜΑ (Προαιρετικά, μπορείς να χρησιμοποιήσεις και το self.window_stack.showMaximized())
        qr = self.window_stack.frameGeometry()
        cp = screen_geo.center()
        qr.moveCenter(cp)
        self.window_stack.move(qr.topLeft())

if __name__ == "__main__":
    core_app = CryptoGuardRunner()
    sys.exit(core_app.app.exec())