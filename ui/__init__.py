from PyQt6.QtWidgets import QMainWindow, QLabel

class DashBoardUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crypto Guard")
        self.label = QLabel("Welcome to Crypto Guard", self)
        self.setCentralWidget(self.label)