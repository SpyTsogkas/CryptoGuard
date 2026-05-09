import sys
import os
import requests
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QGraphicsDropShadowEffect,
                             QFrame, QGridLayout, QProgressBar, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QThread, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QColor, QCursor, QPixmap
from backend import DataFetcher
from core import InvestmentAdvisor 

# --- ΧΡΩΜΑΤΙΚΗ ΠΑΛΕΤΑ ---
BG_COLOR = "#0B132B"
CARD_COLOR = "#14213D"
ACCENT_COLOR = "#00E5FF"
TEXT_COLOR = "#FFFFFF"
MUTED_TEXT = "#8D99AE"

class ModernButton(QPushButton):
    """Επαγγελματικό κουμπί με ομαλό Hover Effect"""
    def __init__(self, text, primary=True):
        super().__init__(text)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(45)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        bg = ACCENT_COLOR if primary else "transparent"
        text_color = "#000000" if primary else TEXT_COLOR
        border = f"none" if primary else f"2px solid {ACCENT_COLOR}"
        hover_bg = "#00C2D8" if primary else "rgba(0, 229, 255, 0.1)"

        self.setStyleSheet(f"""
            QPushButton {{ background-color: {bg}; color: {text_color}; border-radius: 8px; border: {border}; }}
            QPushButton:hover {{ background-color: {hover_bg}; }}
            QPushButton:pressed {{ background-color: #00A3B5; }}
        """)

class ModernInput(QLineEdit):
    """Επαγγελματικό πεδίο εισαγωγής"""
    def __init__(self, placeholder, is_password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(45)
        self.setFont(QFont("Segoe UI", 11))
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            
        self.setStyleSheet(f"""
            QLineEdit {{ background-color: #1E2D4A; color: {TEXT_COLOR}; border: 1px solid #2C3E5D; border-radius: 8px; padding-left: 15px; }}
            QLineEdit:focus {{ border: 2px solid {ACCENT_COLOR}; }}
        """)

class AuthScreen(QWidget):
    """Η οθόνη Σύνδεσης / Εγγραφής"""
    def __init__(self, db_manager, success_callback):
        super().__init__()
        self.db = db_manager
        self.on_success = success_callback
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        self.logo_label = QLabel("🛡️ CryptoGuard")
        self.logo_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.logo_label.setStyleSheet(f"color: {TEXT_COLOR};")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.logo_label)
        
        self.sub_label = QLabel("Secure AI Trading Predictions")
        self.sub_label.setFont(QFont("Segoe UI", 10))
        self.sub_label.setStyleSheet(f"color: {ACCENT_COLOR}; margin-bottom: 20px;")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.sub_label)

        self.username_input = ModernInput("Username")
        self.password_input = ModernInput("Password", is_password=True)
        
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["Conservative", "Moderate", "Aggressive"])
        self.risk_combo.setMinimumHeight(45)
        self.risk_combo.setStyleSheet(f"""
            QComboBox {{ background-color: #1E2D4A; color: {TEXT_COLOR}; border-radius: 8px; padding-left: 15px; border: 1px solid #2C3E5D; }}
            QComboBox::drop-down {{ border: none; }}
        """)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Select Risk Profile (For Registration):", styleSheet=f"color: {MUTED_TEXT};"))
        layout.addWidget(self.risk_combo)

        self.login_btn = ModernButton("Login")
        self.register_btn = ModernButton("Register", primary=False)
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.handle_register)

        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.msg_label = QLabel("")
        self.msg_label.setStyleSheet("color: #FF5555;")
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.msg_label)

    def handle_login(self):
        user = self.username_input.text()
        pwd = self.password_input.text()
        risk = self.db.authenticate_user(user, pwd)
        if risk:
            self.on_success(user, risk)
        else:
            self.msg_label.setText("Invalid credentials!")
            self.shake_window()

    def handle_register(self):
        user = self.username_input.text()
        pwd = self.password_input.text()
        risk = self.risk_combo.currentText()
        if not user or not pwd:
            self.msg_label.setText("Fields cannot be empty!")
            return
        success = self.db.register_user(user, pwd, risk)
        if success:
            self.msg_label.setStyleSheet(f"color: {ACCENT_COLOR};")
            self.msg_label.setText("Registered! You can now login.")
        else:
            self.msg_label.setStyleSheet("color: #FF5555;")
            self.msg_label.setText("Username already exists!")

    def shake_window(self):
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        start_pos = self.pos()
        self.anim.setKeyValueAt(0, start_pos)
        self.anim.setKeyValueAt(0.25, start_pos + QPoint(-10, 0))
        self.anim.setKeyValueAt(0.75, start_pos + QPoint(10, 0))
        self.anim.setKeyValueAt(1, start_pos)
        self.anim.start()


class CryptoButton(QPushButton):
    """Ειδικό κουμπί για την επιλογή των Cryptos με εικονίδιο"""
    def __init__(self, name, symbol, icon_path):
        super().__init__()
        self.symbol = symbol
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedSize(130, 130)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(45, 45, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
        else:
            icon_label.setText("🪙") # Fallback αν σβηστεί η εικόνα
            icon_label.setFont(QFont("Segoe UI", 24))
            
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        text_label = QLabel(name)
        text_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)

        self.setStyleSheet(f"""
            QPushButton {{ background-color: {CARD_COLOR}; color: {TEXT_COLOR}; border-radius: 12px; border: 2px solid transparent; }}
            QPushButton:hover {{ border: 2px solid {ACCENT_COLOR}; background-color: #1E2D4A; }}
            QPushButton:pressed {{ background-color: #0B132B; }}
        """)


class AnalysisWorker(QThread):
    """Worker Thread για να μην παγώνει το UI κατά την ανάλυση"""
    finished = pyqtSignal(dict)
    def __init__(self, symbol, risk_profile):
        super().__init__()
        self.symbol = symbol
        self.risk_profile = risk_profile
        
    def run(self):
        try:
            advisor = InvestmentAdvisor(risk_profile=self.risk_profile)
            result = advisor.generate_advice(self.symbol)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({"error": str(e)})


class DashBoardUI(QWidget):
    """Το κεντρικό ταμπλό της εφαρμογής"""
    def __init__(self, username, risk_level):
        super().__init__()
        self.username = username
        self.risk_level = risk_level
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        self.assets = self._fetch_top10_assets()  # ← εδώ, ΠΡΙΝ το init_ui
        self.init_ui()

    def _fetch_top10_assets(self):
        """Κατεβάζει δυναμικά τα Top 10 coins με ονόματα και logos από το CoinGecko."""
        try:
            fetcher = DataFetcher()
            endpoint = f"{fetcher.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'volume_desc',
                'per_page': 10,
                'page': 1
            }
            response = requests.get(endpoint, params=params, headers=fetcher.get_headers())
            response.raise_for_status()
            coins = response.json()

            assets = []
            os.makedirs("assets images/cache", exist_ok=True)

            for coin in coins:
                coin_id = coin['id']
                name = coin['name']
                image_url = coin.get('image', '')
                icon_path = f"assets images/cache/{coin_id}.png"

                if not os.path.exists(icon_path) and image_url:
                    try:
                        img_data = requests.get(image_url, timeout=5).content
                        with open(icon_path, 'wb') as f:
                            f.write(img_data)
                    except Exception:
                        icon_path = ""

                assets.append({
                    "name": name,
                    "symbol": coin_id,
                    "icon": icon_path
                })

            return assets

        except Exception as e:
            return [
                {"name": "Bitcoin",  "symbol": "bitcoin",     "icon": "assets images/Bitcoin.png"},
                {"name": "Ethereum", "symbol": "ethereum",    "icon": "assets images/Ethereum.png"},
                {"name": "Solana",   "symbol": "solana",      "icon": "assets images/Solana.png"},
                {"name": "Cardano",  "symbol": "cardano",     "icon": "assets images/Cardano.png"},
                {"name": "BNB",      "symbol": "binancecoin", "icon": "assets images/Binance-Coin.png"}
            ]

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("🛡️ CryptoGuard AI Engine")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_COLOR};")
        
        user_info = QLabel(f"👤 {self.username.upper()} | Risk: {self.risk_level}")
        user_info.setFont(QFont("Segoe UI", 12))
        user_info.setStyleSheet(f"color: {ACCENT_COLOR};")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        main_layout.addLayout(header_layout)
        
        # Visual Crypto Selector (Με τα σωστά paths)
        selection_label = QLabel("⚡ Επιλέξτε Asset για Ανάλυση:")
        selection_label.setStyleSheet(f"color: {MUTED_TEXT}; font-size: 14px; font-weight: bold;")
        main_layout.addWidget(selection_label)

        crypto_grid = QGridLayout()
        crypto_grid.setSpacing(15)

        for i, asset in enumerate(self.assets):
            btn = CryptoButton(asset["name"], asset["symbol"], asset["icon"])
            btn.clicked.connect(lambda checked, s=asset["symbol"]: self.start_analysis(s))
            row = i // 5      # 0 για τα πρώτα 5, 1 για τα επόμενα 5
            col = i % 5       # στήλη 0-4
            crypto_grid.addWidget(btn, row, col)

        main_layout.addLayout(crypto_grid)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"QProgressBar {{ background: #1E2D4A; border: none; height: 4px; }} QProgressBar::chunk {{ background-color: {ACCENT_COLOR}; }}")
        self.progress.hide()
        main_layout.addWidget(self.progress)
        
        # Results Frame
        self.results_frame = QFrame()
        self.results_frame.setStyleSheet(f"background-color: {CARD_COLOR}; border-radius: 15px;")
        self.results_layout = QGridLayout(self.results_frame)
        self.results_layout.setContentsMargins(30, 30, 30, 30)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 5)
        self.results_frame.setGraphicsEffect(shadow)

        self.lbl_current = self.create_stat_label("Current Price", "$0.00")
        self.lbl_target = self.create_stat_label("AI Target Price", "$0.00")
        self.lbl_change = self.create_stat_label("Est. Change", "0.00%")
        self.lbl_signal = self.create_stat_label("Trading Signal", "WAITING")
        self.lbl_horizon = self.create_stat_label("Time Horizon", "-")
        self.lbl_mae = self.create_stat_label("AI Error Margin", "$0.00")

        self.results_layout.addLayout(self.lbl_current, 0, 0)
        self.results_layout.addLayout(self.lbl_target, 0, 1)
        self.results_layout.addLayout(self.lbl_change, 0, 2)
        self.results_layout.addLayout(self.lbl_signal, 1, 0)
        self.results_layout.addLayout(self.lbl_horizon, 1, 1)
        self.results_layout.addLayout(self.lbl_mae, 1, 2)
        
        main_layout.addWidget(self.results_frame)

       # --- Δημιουργία Scroll Area για τη Συμβουλή ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E2D4A;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #00E5FF;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Δημιουργία του Advice Label
        self.advice_label = QLabel("Επιλέξτε ένα νόμισμα από πάνω για να ξεκινήσει η ανάλυση της αγοράς.")
        self.advice_label.setWordWrap(True)
        self.advice_label.setFont(QFont("Segoe UI", 12))
        # Αφαιρούμε το padding από το QLabel γιατί θα το ελέγχει το ScrollArea
        self.advice_label.setStyleSheet(f"background-color: {CARD_COLOR}; color: {TEXT_COLOR}; padding: 25px; border-radius: 15px; border-left: 5px solid {ACCENT_COLOR};")
        self.advice_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Τοποθέτηση του label μέσα στο Scroll Area
        self.scroll_area.setWidget(self.advice_label)
        
        # Ορίζουμε ένα μέγιστο ύψος ώστε να μην "κρύβει" τα logos σε μικρές οθόνες
        self.scroll_area.setMaximumHeight(200) 
        
        main_layout.addWidget(self.scroll_area)

    def create_stat_label(self, title, value):
        layout = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {MUTED_TEXT}; font-size: 13px; font-weight: bold;")
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"color: {TEXT_COLOR}; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_lbl)
        layout.addWidget(val_lbl)
        return layout

    def update_stat_value(self, layout, text, color=TEXT_COLOR):
        lbl = layout.itemAt(1).widget()
        lbl.setText(text)
        lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")

    def start_analysis(self, symbol):
        for btn in self.findChildren(CryptoButton):
            btn.setEnabled(False)
            
        self.progress.show()
        self.advice_label.setText(f"📡 Ανάκτηση δεδομένων & εκπαίδευση Quant AI για {symbol.upper()}... Παρακαλώ περιμένετε.")
        self.advice_label.setStyleSheet(f"background-color: {CARD_COLOR}; color: {TEXT_COLOR}; padding: 25px; border-radius: 15px; border-left: 5px solid {ACCENT_COLOR};")
        
        self.worker = AnalysisWorker(symbol, self.risk_level)
        self.worker.finished.connect(self.on_analysis_complete)
        self.worker.start()

    def on_analysis_complete(self, result):
        for btn in self.findChildren(CryptoButton):
            btn.setEnabled(True)
            
        self.progress.hide()
        
        if "error" in result:
            self.advice_label.setText(f"❌ Υπήρξε Σφάλμα: {result['error']}")
            self.advice_label.setStyleSheet(f"background-color: {CARD_COLOR}; color: #FF5555; padding: 25px; border-radius: 15px; border-left: 5px solid #FF5555;")
            return

        curr = f"${result['current_price']:,.2f}"
        targ = f"${result['prediction']['target_price']:,.2f}"
        pct = result['price_change_pct']
        change_str = f"{'+' if pct > 0 else ''}{pct:.2f}%"
        change_color = "#00FF7F" if pct > 0 else "#FF5555"

        self.update_stat_value(self.lbl_current, curr)
        self.update_stat_value(self.lbl_target, targ, change_color)
        self.update_stat_value(self.lbl_change, change_str, change_color)
        self.update_stat_value(self.lbl_signal, result['prediction']['signal'], ACCENT_COLOR)
        self.update_stat_value(self.lbl_horizon, result['time_limit'])
        self.update_stat_value(self.lbl_mae, f"${result['error_margin']:,.2f}")

        self.advice_label.setText(f"🤖 AI Recommendation:\n{result['advice']}")
        self.advice_label.setStyleSheet(f"background-color: {CARD_COLOR}; color: {TEXT_COLOR}; padding: 25px; border-radius: 15px; border-left: 5px solid {change_color};")
        
        self.advice_label.setText(f"🤖 AI Recommendation:\n{result['advice']}")
        self.advice_label.setStyleSheet(f"background-color: {CARD_COLOR}; color: {TEXT_COLOR}; padding: 25px; border-radius: 15px; border-left: 5px solid {change_color};")
        #self.advice_label.setMinimumHeight(180)