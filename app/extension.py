import os
import sqlite3

from config import DB_PATH

def get_db_version(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA user_version;")
    return cur.fetchone()[0]

def set_db_version(conn, version):
    cur = conn.cursor()
    cur.execute(f"PRAGMA user_version = {version};")
    
def get_conn():
    return sqlite3.connect(DB_PATH)

def column_exists(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return column in [row[1] for row in cur.fetchall()]


def migrate(conn):
    version = get_db_version(conn)
    cur = conn.cursor()

    while version < 3:
        if version:
            print(f"Migrating to v{version + 1}...")
        else:
            print("db not started, starting at v1")

        # v1: criar metrics
        if version == 0:
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

        # v2: criar state
        elif version == 1:
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

        # v3: upgrade metrics
        elif version == 2:
            if not column_exists(conn, "metrics", "metric"):
                cur.execute("ALTER TABLE metrics ADD COLUMN metric TEXT;")

            if not column_exists(conn, "metrics", "value_type"):
                cur.execute("ALTER TABLE metrics ADD COLUMN value_type TEXT;")

            if not column_exists(conn, "metrics", "scope"):
                cur.execute("ALTER TABLE metrics ADD COLUMN scope TEXT;")

        version += 1
        set_db_version(conn, version)

    conn.commit()

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_conn()
    
    # aplica migrations
    migrate(conn)

    conn.commit()
    conn.close()
