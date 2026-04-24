import os
import sqlite3

from config import DB_PATH


def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT NOT NULL,
            source TEXT NOT NULL,
            host_name TEXT NOT NULL,
            host_ip TEXT NOT NULL,
            target TEXT,
            device_type TEXT,
            name TEXT,
            value REAL,
            value_text TEXT,
            meta TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS state (
            host_ip TEXT NOT NULL,
            device_type TEXT NOT NULL,
            name TEXT NOT NULL,
            heat_score REAL DEFAULT 0,
            level TEXT DEFAULT 'ok',
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (host_ip, device_type, name)
        )
    """)

    conn.commit()
    conn.close()
