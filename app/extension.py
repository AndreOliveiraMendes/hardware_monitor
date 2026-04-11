import sqlite3
import os

from config import DB_PATH

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            host_name TEXT,
            host_ip TEXT,
            dispositive_type TEXT,
            name TEXT,
            value REAL
        )
    """)

    conn.commit()
    conn.close()
