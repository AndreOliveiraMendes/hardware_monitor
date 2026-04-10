import os
import sqlite3

DB = os.getenv("DB_PATH", "metrics.db")

def get_conn():
    return sqlite3.connect(DB)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            type TEXT,
            name TEXT,
            value REAL
        )
    """)

    conn.commit()
    conn.close()

def insert_metric(type_, name, value):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO metrics (type, name, value) VALUES (?, ?, ?)",
        (type_, name, value)
    )

    conn.commit()
    conn.close()

def get_latest_metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT type, name, value
        FROM metrics
        WHERE id IN (
            SELECT MAX(id)
            FROM metrics
            GROUP BY type, name
        )
    """)

    rows = cur.fetchall()
    conn.close()

    data = {"cpu": {}, "disk": {}}

    for type_, name, value in rows:
        if type_ == "CPU":
            data["cpu"][name] = value
        elif type_ == "DISK":
            data["disk"][name] = value

    return data
