import sqlite3
import pandas as pd
from datetime import datetime

class DataBaseManager:
    def __init__(self, db_path = "database/crypto_guard.db"):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Creates tables for users and AI prediction history."""
        with self._connect() as conn:
            # Table of the predictions history (Metrics Support)
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

            # User Table (SRS/SDD)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    risk_level TEXT
                )
            """)

            conn.commit()
        
    def log_prediction(self, symbol, current_price, ai_output):
        """
        Saves the Quant-Pro AI results.
        ai_output: dictionary {target_price, signal, time_horizon, mae}
        """
        query = """
            INSERT INTO prediction_logs 
            (timestamp, symbol, actual_price, predicted_price, signal_type, time_horizon, mae_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._connect() as conn:
            conn.execute(query, (
                datetime.now(),
                symbol,
                current_price,
                ai_output['target_price'],
                ai_output['signal'],
                ai_output['time_horizon'],
                ai_output['mae']
            ))
            conn.commit()

    def get_performance_data(self):
        """Returns data for the 'Application of Metrics' deliverable."""
        with self._connect() as conn:
            return pd.read_sql_query("SELECT * FROM prediction_logs", conn)