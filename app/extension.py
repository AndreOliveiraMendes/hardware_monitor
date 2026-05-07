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
    
def get_connection():
    return sqlite3.connect(DB_PATH)

def column_exists(conn, table, column):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    return column in [row[1] for row in cur.fetchall()]


def migrate(conn):
    version = get_db_version(conn)
    cur = conn.cursor()

    while version < 5:
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

        # v4: indexes
        elif version == 3:
            # 🔥 principal: queries por tempo (time-series)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp
                ON metrics (timestamp DESC);
            """)

            # 🔥 filtro por host + tempo (muito comum)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_host_time
                ON metrics (host_ip, timestamp DESC);
            """)

            # 🔥 filtro por tipo (cpu, disk, etc)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_type_time
                ON metrics (type, timestamp DESC);
            """)

            # 🔥 filtro mais específico (device-level)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_device
                ON metrics (host_ip, device_type, name, timestamp DESC);
            """)

            # 🔥 state lookup (já tem PK, mas ajuda em queries parciais)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_state_host
                ON state (host_ip);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_state_level
                ON state (level);
            """)
        
        elif version == 4:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    host_ip TEXT,
                    device_type TEXT,
                    name TEXT,

                    msg TEXT NOT NULL,
                    level TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',

                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    sent_at TIMESTAMP NULL
                )
            """)

            # fila de envio
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_status
                ON notifications(status)
            """)

            # ordenação/cleanup
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_created_at
                ON notifications(created_at)
            """)

            # consultas por status + data
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_status_created
                ON notifications(status, created_at)
            """)

        version += 1
        set_db_version(conn, version)

    conn.commit()

def init_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    
    # aplica migrations
    migrate(conn)

    conn.commit()
    conn.close()
