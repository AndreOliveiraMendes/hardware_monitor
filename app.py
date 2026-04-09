import os
import sqlite3
from collections import defaultdict
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_prefix=1)

DB = os.getenv("DB_PATH", "metrics.db")
HOST = os.getenv("FLASK_HOST", "127.0.0.1")
PORT = os.getenv("FLASK_PORT", 5000)

# ==========================================================
# DB
# ==========================================================
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


# ==========================================================
# INSERT
# ==========================================================
def insert_metric(type_, name, value):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO metrics (type, name, value) VALUES (?, ?, ?)",
        (type_, name, value)
    )

    conn.commit()
    conn.close()


# ==========================================================
# QUERY (últimos valores)
# ==========================================================
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


# ==========================================================
# ROUTES
# ==========================================================
@app.route("/")
def home():
    data = get_latest_metrics()
    return render_template("index.html", data=data)


@app.route("/dashboard")
def dashboard():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT datetime(timestamp, 'localtime'), type, name, value
        FROM metrics
        ORDER BY timestamp DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    conn.close()

    return render_template("dashboard.html", rows=rows)


@app.route("/metrics")
def metrics():
    return jsonify(get_latest_metrics())


@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json()

    if isinstance(data, dict):
        data = [data]

    for item in data:
        insert_metric(item["type"], item["name"], item["value"])

    return jsonify({"status": "ok"})


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
