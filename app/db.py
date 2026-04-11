from datetime import datetime

from app.extension import get_conn

def insert_metric(dispositive_type, hostname, hostip, name, value):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO metrics (dispositive_type, host_name, host_ip, name, value) VALUES (?, ?, ?, ?, ?)",
        (dispositive_type, hostname, hostip, name, value)
    )

    conn.commit()
    conn.close()
    
def get_latest_metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT dispositive_type, name, value
        FROM metrics
        WHERE id IN (
            SELECT MAX(id)
            FROM metrics
            GROUP BY dispositive_type, name
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

def get_metrics(start, end, tipo):
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT datetime(timestamp, 'localtime'), dispositive_type, name, value
        FROM metrics
    """

    conditions = []
    params = []

    if start and end:
        start = datetime.fromisoformat(start)
        end = datetime.fromisoformat(end)
        conditions.append("timestamp BETWEEN ? AND ?")
        params.extend([start, end])
    elif start:
        start = datetime.fromisoformat(start)
        conditions.append("timestamp >= ?")
        params.append(start)
    elif end:
        end = datetime.fromisoformat(end)
        conditions.append("timestamp <= ?")
        params.append(end)

    if tipo:
        conditions.append("dispositive_type = ?")
        params.append(tipo)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY timestamp DESC LIMIT 100"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_types():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT dispositive_type FROM metrics")
    types = [row[0] for row in cur.fetchall()]
    
    return types