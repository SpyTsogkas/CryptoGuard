import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QComboBox, QLabel, QTextEdit, QFrame, 
                             QGraphicsDropShadowEffect, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QStandardItemModel, QStandardItem, QCursor
from core.investment_advisor import InvestmentAdvisor

# --- LOGIN SCREEN (Authentication & Registration UI) ---
class LoginScreen(QWidget):
    def __init__(self, db, on_success):
        super().__init__()
        self.db = db
        self.on_success = on_success
        self.init_ui()

    def init_ui(self):
        # Set dark base theme for the login window
        self.setStyleSheet("background-color: #0b0e14;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # App Branding Logo
        logo = QLabel("🛡️ CryptoGuard")
        logo.setStyleSheet("font-size: 32px; font-weight: 900; color: #f0b90b; margin-bottom: 30px;")
        layout.addWidget(logo)

        # Username Input Field
        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText("Username")
        self.user_in.setFixedWidth(300)
        self.user_in.setStyleSheet("padding: 12px; background: #1e2329; border: 1px solid #2b3139; border-radius: 5px; color: white;")
        layout.addWidget(self.user_in)

        # Password Input Field
        self.pass_in = QLineEdit()
        self.pass_in.setPlaceholderText("Password")
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_in.setFixedWidth(300)
        self.pass_in.setStyleSheet("padding: 12px; background: #1e2329; border: 1px solid #2b3139; border-radius: 5px; color: white;")
        layout.addWidget(self.pass_in)

        # Horizontal layout for the two buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # Sign In Button
        self.login_btn = QPushButton("SIGN IN")
        self.login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
        self.login_btn.setFixedWidth(145)
        self.login_btn.setStyleSheet("background: #f0b90b; color: black; font-weight: bold; padding: 12px; border-radius: 5px;")
        self.login_btn.clicked.connect(self.do_login)

        # Register Button
        self.reg_btn = QPushButton("REGISTER")
        self.reg_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
        self.reg_btn.setFixedWidth(145)
        self.reg_btn.setStyleSheet("background: transparent; color: #f0b90b; border: 2px solid #f0b90b; font-weight: bold; padding: 10px; border-radius: 5px;")
        self.reg_btn.clicked.connect(self.handle_register)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.reg_btn)
        
        layout.addLayout(btn_layout)
        
        # Footer label
        footer = QLabel("Secure Algorithmic Trading Environment")
        footer.setStyleSheet("color: #474d57; font-size: 10px; margin-top: 20px;")
        layout.addWidget(footer, alignment=Qt.AlignmentFlag.AlignCenter)

    def do_login(self):
        """Validates credentials and moves to the dashboard"""
        username = self.user_in.text()
        password = self.pass_in.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "All fields are required for Login.")
            return

        # DB Authentication
        risk_profile = self.db.authenticate_user(username, password)
        
        if risk_profile:
            print(f"[AUTH] User {username} logged in.")
            self.on_success(username, risk_profile)
        else:
            QMessageBox.warning(self, "Access Denied", "Invalid username or password.")

    def handle_register(self):
        """Creates a new user record in the database"""
        username = self.user_in.text()
        password = self.pass_in.text()
        
        if len(username) < 3 or len(password) < 4:
            QMessageBox.warning(self, "Validation", "Username must be > 3 and Password > 4 chars.")
            return

        # Attempt to write to DB
        success = self.db.register_user(username, password, risk="Moderate")
        
        if success:
            QMessageBox.information(self, "Success", f"Account created for {username}!\nYou can now Sign In.")
        else:
            QMessageBox.critical(self, "Error", "Username already exists in the database.")

# --- THE MAIN DASHBOARD ---
class DashBoardUI(QMainWindow):
    def __init__(self, username, risk_level):
        super().__init__()
        self.setWindowTitle(f"CryptoGuard Terminal - {username}")
        self.setMinimumSize(1200, 850)
        
        # Core data initialization
        self.advisor = InvestmentAdvisor(risk_profile=risk_level)
        self.current_theme = "dark"
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets images')
        
        self.coin_data = {
            "bitcoin": ("BITCOIN", "Bitcoin.png"),
            "ethereum": ("ETHEREUM", "Ethereum.png"),
            "solana": ("SOLANA", "Solana.png"),
            "binancecoin": ("BNB", "Binance-Coin.png"),
            "cardano": ("CARDANO", "Cardano.png")
        }

        self.init_ui()
        self.apply_theme()

    def create_shadow(self):
        """Creates professional depth effects for UI elements"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        return shadow

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        s_layout = QVBoxLayout(self.sidebar)
        s_layout.setContentsMargins(20, 40, 20, 40)

        logo = QLabel("🛡️ CryptoGuard")
        logo.setStyleSheet("font-size: 22px; font-weight: 900; color: #f0b90b; margin-bottom: 30px;")
        s_layout.addWidget(logo)

        for item in ["📊 Dashboard", "💹 Markets", "💼 Portfolio"]:
            btn = QPushButton(item)
            btn.setObjectName("navBtn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
            s_layout.addWidget(btn)
        
        s_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        # Dashboard Workspace
        self.container = QWidget()
        self.container.setObjectName("mainView")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(40, 30, 40, 40)

        # Header Section
        header = QHBoxLayout()
        title = QLabel("Algorithmic Risk Terminal")
        title.setStyleSheet("font-size: 28px; font-weight: 800; color: white;")
        
        self.theme_btn = QPushButton("🌓 LIGHT MODE")
        self.theme_btn.setObjectName("themeBtnTop")
        self.theme_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
        self.theme_btn.setFixedSize(150, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.theme_btn)
        layout.addLayout(header)

        # Control Card (Asset selection)
        self.ctrl_card = QFrame()
        self.ctrl_card.setObjectName("card")
        self.ctrl_card.setGraphicsEffect(self.create_shadow())
        ctrl_lay = QHBoxLayout(self.ctrl_card)
        ctrl_lay.setContentsMargins(25, 25, 25, 25)

        v_asset = QVBoxLayout()
        v_asset.addWidget(QLabel("SELECT ASSET"))
        self.coin_box = QComboBox()
        self.coin_box.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
        self.coin_box.setIconSize(QSize(24, 24))
        
        model = QStandardItemModel()
        for api_id, (name, icon_file) in self.coin_data.items():
            item = QStandardItem(name)
            item.setData(api_id, Qt.ItemDataRole.UserRole)
            icon_path = os.path.join(self.assets_path, icon_file)
            if os.path.exists(icon_path): item.setIcon(QIcon(icon_path))
            model.appendRow(item)
        self.coin_box.setModel(model)
        v_asset.addWidget(self.coin_box)

        self.btn_run = QPushButton("⚡ RUN ANALYSIS")
        self.btn_run.setObjectName("runBtn")
        self.btn_run.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Hover cursor
        self.btn_run.clicked.connect(self.start_analysis)
        
        ctrl_lay.addLayout(v_asset)
        ctrl_lay.addStretch()
        ctrl_lay.addWidget(self.btn_run)
        layout.addWidget(self.ctrl_card)

        # Display Section
        res_row = QHBoxLayout()
        
        self.adv_card = QFrame()
        self.adv_card.setObjectName("card")
        self.adv_card.setGraphicsEffect(self.create_shadow())
        adv_lay = QVBoxLayout(self.adv_card)
        adv_lay.addWidget(QLabel("💡 AI GENERATED ADVICE"))
        self.advice_display = QTextEdit()
        self.advice_display.setReadOnly(True)
        adv_lay.addWidget(self.advice_display)
        
        self.stats_card = QFrame()
        self.stats_card.setObjectName("card")
        self.stats_card.setGraphicsEffect(self.create_shadow())
        st_lay = QVBoxLayout(self.stats_card)
        st_lay.addWidget(QLabel("LIVE MARKET STATUS"))
        self.price_label = QLabel("$ --")
        self.price_label.setObjectName("bigPrice")
        st_lay.addWidget(self.price_label)
        self.change_label = QLabel("Syncing...")
        self.change_label.setObjectName("changeText")
        st_lay.addWidget(self.change_label)
        st_lay.addStretch()

        res_row.addWidget(self.adv_card, 2)
        res_row.addWidget(self.stats_card, 1)
        layout.addLayout(res_row)
        self.main_layout.addWidget(self.container)

    def toggle_theme(self):
        """Toggles between Dark and Light color palettes"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.theme_btn.setText("🌓 DARK MODE" if self.current_theme == "light" else "🌓 LIGHT MODE")
        self.apply_theme()

    def start_analysis(self):
        """Executes AI logic and updates labels with live data"""
        symbol = self.coin_box.currentData(Qt.ItemDataRole.UserRole)
        data = self.advisor.generate_advice(symbol)
        
        self.price_label.setText(f"${data['current_price']:,}")
        self.advice_display.setText(data['advice'])
        pct = data['price_change_pct']
        self.change_label.setText(f"{'+' if pct > 0 else ''}{pct}% (24h)")
        
        # Color coding based on market performance
        color = '#27ae60' if pct >= 0 else '#e74c3c'
        self.change_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: 900;")

    def apply_theme(self):
        """Global CSS definitions for application styling"""
        if self.current_theme == "dark":
            style = """
                QMainWindow { background-color: #0b0e14; }
                #sidebar { background-color: #12151c; border-right: 1px solid #1e222d; }
                #navBtn { color: #848e9c; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 8px; }
                #navBtn:hover { background-color: #2b3139; color: white; }
                #card { background-color: #1e2329; border-radius: 15px; border: 1px solid #2b3139; }
                #runBtn { background-color: #f0b90b; color: black; border-radius: 10px; padding: 15px; font-weight: 900; }
                #runBtn:hover { background-color: #fcd535; }
                #bigPrice { color: white; font-size: 42px; font-weight: 900; }
                QComboBox { background-color: #2b3139; color: white; border-radius: 8px; padding: 8px; border: 1px solid #474d57; font-weight: bold; }
                QTextEdit { background: transparent; color: white; border: none; font-size: 15px; }
                QLabel { color: #848e9c; font-weight: bold; }
            """
        else:
            style = """
                QMainWindow { background-color: #f0f2f5; }
                #sidebar { background-color: #ffffff; border-right: 1px solid #dcdfe4; }
                #navBtn { color: #474d57; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 8px; }
                #navBtn:hover { background-color: #f0f2f5; }
                #card { background-color: #ffffff; border-radius: 15px; border: 1px solid #e0e3e7; }
                #runBtn { background-color: #f0b90b; color: black; border-radius: 10px; padding: 15px; font-weight: 900; }
                #bigPrice { color: #1e2329; font-size: 42px; font-weight: 900; }
                QComboBox { background-color: #ffffff; color: #1e2329; border: 1px solid #cfd3d8; padding: 8px; border-radius: 8px; }
                QTextEdit { background: transparent; color: #1e2329; border: none; }
                QLabel { color: #474d57; font-weight: bold; }
            """
        self.setStyleSheet(style)