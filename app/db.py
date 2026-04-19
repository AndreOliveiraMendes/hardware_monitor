from datetime import datetime

from app.extension import get_conn


def insert_metric(**kwargs):
    # unpack kwargs into fields and values for the SQL query
    fields = []
    values = []
    for key, value in kwargs.items():
        fields.append(key)
        values.append(value)
    
    # create the SQL query string with placeholders for values
    query = f"INSERT INTO metrics ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(values))})"
    
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(values))
        conn.commit()
    
def get_latest_metrics():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT type, datetime(timestamp, 'localtime') as timestamp, device_type, name, value
        FROM metrics
        WHERE id IN (
            SELECT MAX(id)
            FROM metrics
            GROUP BY device_type, name
        )
    """)

    rows = cur.fetchall()
    conn.close()

    data = {"cpu": {}, "disk": {}, "battery": None}

    for info_type, time, device_type, name, value in rows:
        if info_type == "temperature":
            if device_type.lower() == "cpu":
                data["cpu"][name] = {"value":value, "time":time}
            elif device_type.lower() == "disk":
                data["disk"][name] = {"value":value, "time":time}
        elif info_type == "battery":
            data["battery"] = {"value":value, "time":time}

    return data

def get_metrics(start, end, tipo, name):
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT datetime(timestamp, 'localtime'), type, device_type, name, value
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
        conditions.append("datetime(timestamp, 'localtime') <= ?")
        params.append(end)

    if tipo:
        conditions.append("device_type = ?")
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
    
    cur.execute("SELECT DISTINCT device_type FROM metrics WHERE type = 'temperature'")
    types = [row[0] for row in cur.fetchall()]
    
    return types

def get_names():
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT name FROM metrics WHERE type = 'temperature'")
    names = [row[0] for row in cur.fetchall()]
    
    return names
