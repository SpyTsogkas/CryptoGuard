import sqlite3
import pandas as pd
from datetime import datetime

class DataBaseManager:
    def __init__(self, db_path="database/crypto_guard.db"):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        with self._connect() as conn:
            # Predictions Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prediction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    timestamp DATETIME, 
                    symbol TEXT,
                    actual_price REAL, 
                    predicted_price REAL, 
                    signal_type TEXT, 
                    time_horizon TEXT, 
                    mae_score REAL
                )
            """)

            # User table with password
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    risk_level TEXT
                )
            """)
            conn.commit()

    # User System
    def register_user(self, username, password, risk="Moderate"):
        try:
            with self._connect() as conn:
                conn.execute("INSERT INTO users (username, password, risk_level) VALUES (?, ?, ?)", 
                             (username, password, risk))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False # Existing Username

    def authenticate_user(self, username, password):
        with self._connect() as conn:
            cursor = conn.execute("SELECT risk_level FROM users WHERE username = ? AND password = ?", 
                                 (username, password))
            row = cursor.fetchone()
            return row[0] if row else None

    # Predictions System
    def log_prediction(self, symbol, current_price, ai_output):
        query = """
            INSERT INTO prediction_logs 
            (timestamp, symbol, actual_price, predicted_price, signal_type, time_horizon, mae_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                datetime.now(), symbol, current_price,
                ai_output['target_price'], ai_output['signal'],
                ai_output['time_horizon'], ai_output['mae']
            ))
            conn.commit()