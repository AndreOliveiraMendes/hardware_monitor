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
        SELECT datetime(timestamp, 'localtime') as timestamp, dispositive_type, name, value
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

    for time, type_, name, value in rows:
        if type_ == "CPU":
            data["cpu"][name] = {"value":value, "time":time}
        elif type_ == "DISK":
            data["disk"][name] = {"value":value, "time":time}

    return data

def get_metrics(start, end, tipo, name):
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
        conditions.append("datetime(timestamp, 'localtime')  BETWEEN ? AND ?")
        params.extend([start, end])
    elif start:
        start = datetime.fromisoformat(start)
        conditions.append("datetime(timestamp, 'localtime') >= ?")
        params.append(start)
    elif end:
        end = datetime.fromisoformat(end)
        conditions.append("datetime(timestamp, 'localtime' <= ?")
        params.append(end)

    if tipo:
        conditions.append("dispositive_type = ?")
        params.append(tipo)

    if name:
        conditions.append("name = ?")
        params.append(name)

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

def get_names():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT name FROM metrics")
    names = [row[0] for row in cur.fetchall()]
    
    return names