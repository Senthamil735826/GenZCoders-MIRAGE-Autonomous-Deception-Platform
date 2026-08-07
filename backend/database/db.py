import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "mirage.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT,
            event_type TEXT,
            severity TEXT,
            details TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")

def log_event(source_ip, event_type, severity, details):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (timestamp, source_ip, event_type, severity, details) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), source_ip, event_type, severity, details)
    )
    conn.commit()
    conn.close()