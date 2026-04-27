import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLabel, QTextEdit, QFrame, 
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont, QIcon, QStandardItemModel, QStandardItem
from core.investment_advisor import InvestmentAdvisor

class DashBoardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CryptoGuard AI - Pro Terminal")
        self.setMinimumSize(1200, 850)
        
        self.advisor = InvestmentAdvisor(risk_profile="Moderate")
        self.current_theme = "dark"

        # ΔΙΟΡΘΩΣΗ: Ο φάκελος όπως φαίνεται στο screenshot σου
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets images')

        # ΔΙΟΡΘΩΣΗ: Ονόματα αρχείων ακριβώς όπως στο screenshot (με κεφαλαία)
        self.coin_data = {
            "bitcoin": ("BITCOIN", "Bitcoin.png"),
            "ethereum": ("ETHEREUM", "Ethereum.png"),
            "solana": ("SOLANA", "Solana.png"),
            "binancecoin": ("BNB", "Binance-Coin.png"),
            "cardano": ("CARDANO", "Cardano.png")
        }

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.init_sidebar()
        self.init_main_content()
        self.apply_theme()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 120))
        return shadow

    def init_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(25, 40, 25, 40)

        logo = QLabel("🛡️ CryptoGuard")
        logo.setStyleSheet("font-size: 22px; font-weight: 900; color: #f0b90b; margin-bottom: 30px;")
        layout.addWidget(logo)

        for item in ["📊 Dashboard", "💹 Markets", "💼 Portfolio"]:
            btn = QPushButton(item)
            btn.setObjectName("navBtn")
            layout.addWidget(btn)
        
        layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

    def init_main_content(self):
        self.container = QWidget()
        self.container.setObjectName("mainView")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 20, 40, 40)

        header_layout = QHBoxLayout()
        title = QLabel("Crypto Advice Dashboard")
        title.setStyleSheet("font-size: 26px; font-weight: 800;")
        
        self.theme_btn = QPushButton("🌓 LIGHT MODE")
        self.theme_btn.setObjectName("themeBtnTop")
        self.theme_btn.setFixedSize(150, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        layout.addLayout(header_layout)
        layout.addSpacing(20)

        self.ctrl_card = QFrame()
        self.ctrl_card.setObjectName("card")
        self.ctrl_card.setGraphicsEffect(self.create_shadow())
        ctrl_layout = QHBoxLayout(self.ctrl_card)
        ctrl_layout.setContentsMargins(25, 25, 25, 25)

        v_asset = QVBoxLayout()
        v_asset.addWidget(QLabel("SELECT ASSET"))
        
        self.coin_box = QComboBox()
        self.coin_box.setIconSize(QSize(20, 20)) # Πιο μικρό εικονίδιο όπως ζήτησες
        
        model = QStandardItemModel()
        bold_font = QFont()
        bold_font.setWeight(QFont.Weight.ExtraBold)

        for api_id, (name, icon_file) in self.coin_data.items():
            item = QStandardItem(name)
            item.setData(api_id, Qt.ItemDataRole.UserRole)
            item.setFont(bold_font)
            
            icon_path = os.path.join(self.assets_path, icon_file)
            if os.path.exists(icon_path):
                item.setIcon(QIcon(icon_path))
            else:
                print(f"Warning: File not found at {icon_path}") # Debugging
                
            model.appendRow(item)
            
        self.coin_box.setModel(model)
        v_asset.addWidget(self.coin_box)
        
        v_risk = QVBoxLayout()
        v_risk.addWidget(QLabel("RISK PROFILE"))
        self.risk_box = QComboBox()
        self.risk_box.addItems(["Conservative", "Moderate", "Aggressive"])
        self.risk_box.setStyleSheet("font-weight: 900;")
        v_risk.addWidget(self.risk_box)

        self.btn_run = QPushButton("⚡ RUN ANALYSIS")
        self.btn_run.setObjectName("runBtn")
        self.btn_run.clicked.connect(self.start_analysis)
        
        ctrl_layout.addLayout(v_asset)
        ctrl_layout.addLayout(v_risk)
        ctrl_layout.addWidget(self.btn_run)
        layout.addWidget(self.ctrl_card)

        results_row = QHBoxLayout()
        
        self.advice_card = QFrame()
        self.advice_card.setObjectName("card")
        self.advice_card.setGraphicsEffect(self.create_shadow())
        adv_layout = QVBoxLayout(self.advice_card)
        adv_layout.addWidget(QLabel("💡 INVESTMENT ADVICE"))
        self.advice_display = QTextEdit()
        self.advice_display.setReadOnly(True)
        adv_layout.addWidget(self.advice_display)
        
        self.stats_card = QFrame()
        self.stats_card.setObjectName("card")
        self.stats_card.setGraphicsEffect(self.create_shadow())
        stats_layout = QVBoxLayout(self.stats_card)
        stats_layout.addWidget(QLabel("📊 STATUS"))
        self.price_label = QLabel("$ --")
        self.price_label.setObjectName("bigPrice")
        stats_layout.addWidget(self.price_label)
        self.change_label = QLabel("Waiting...")
        self.change_label.setObjectName("changeText")
        stats_layout.addWidget(self.change_label)
        stats_layout.addStretch()

        results_row.addWidget(self.advice_card, 2)
        results_row.addWidget(self.stats_card, 1)
        layout.addLayout(results_row)

        self.main_layout.addWidget(self.container)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_btn.setText("🌓 DARK MODE" if self.current_theme == "light" else "🌓 LIGHT MODE")
        self.apply_theme()

    def start_analysis(self):
        symbol = self.coin_box.currentData(Qt.ItemDataRole.UserRole)
        data = self.advisor.generate_advice(symbol)
        
        if "error" in data:
            self.advice_display.setText(data["error"])
        else:
            self.price_label.setText(f"${data['current_price']:,}")
            self.advice_display.setText(data['advice'])
            pct = data['price_change_pct']
            self.change_label.setText(f"{'+' if pct > 0 else ''}{pct}% (24h)")
            color = "#27ae60" if pct >= 0 else "#e74c3c"
            self.change_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 900;")

    def apply_theme(self):
        if self.current_theme == "dark":
            style = """
                QMainWindow { background-color: #0b0e14; }
                #sidebar { background-color: #12151c; border-right: 1px solid #1e222d; }
                #mainView { background-color: #0b0e14; }
                QLabel { color: #848e9c; font-weight: bold; }
                #card { background-color: #1e2329; border-radius: 20px; border: 1px solid #2b3139; }
                #navBtn { background: transparent; color: #848e9c; text-align: left; padding: 15px; border: none; font-weight: bold; }
                #navBtn:hover { background-color: #2b3139; color: white; }
                #runBtn { background-color: #f0b90b; color: black; border-radius: 12px; padding: 15px; font-weight: 900; }
                #themeBtnTop { background-color: #2b3139; color: white; border: 1px solid #474d57; border-radius: 10px; font-weight: 900; }
                #bigPrice { color: #ffffff; font-size: 44px; font-weight: 900; }
                QComboBox { background-color: #2b3139; color: white; border-radius: 8px; padding: 10px; border: 1px solid #474d57; font-weight: bold; }
                QComboBox QAbstractItemView { background-color: #1e2329; color: white; selection-background-color: #2b3139; }
                QTextEdit { background: transparent; color: white; border: none; font-size: 15px; }
            """
        else:
            style = """
                QMainWindow { background-color: #f0f2f5; }
                #sidebar { background-color: #ffffff; border-right: 1px solid #dcdfe4; }
                #mainView { background-color: #f0f2f5; }
                QLabel { color: #474d57; font-weight: bold; }
                #card { background-color: #ffffff; border-radius: 20px; border: 1px solid #e0e3e7; }
                #runBtn { background-color: #f0b90b; color: black; border-radius: 12px; padding: 15px; font-weight: 900; }
                #themeBtnTop { background-color: #ffffff; color: #1e2329; border: 1px solid #cfd3d8; border-radius: 10px; font-weight: 900; }
                #bigPrice { color: #1e2329; font-size: 44px; font-weight: 900; }
                QComboBox { background-color: #ffffff; color: #1e2329; border: 1px solid #cfd3d8; border-radius: 8px; padding: 10px; font-weight: bold; }
                QTextEdit { background: transparent; color: #1e2329; border: none; font-size: 15px; }
            """
        self.setStyleSheet(style)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = DashBoardUI()
    window.show()
    sys.exit(app.exec())