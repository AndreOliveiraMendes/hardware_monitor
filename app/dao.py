import json
from datetime import datetime

from app.db import execute, query
from app.extension import get_conn


def insert_metric(**kwargs):
    fields = list(kwargs.keys())
    values = list(kwargs.values())

    sql = f"""
        INSERT INTO metrics ({', '.join(fields)})
        VALUES ({', '.join(['?'] * len(values))})
    """

    execute(sql, values)
        
def get_heat_score(host_ip, device_type, name):
    return query("""
        SELECT heat_score, level
        FROM state
        WHERE host_ip = ? AND device_type = ? AND name = ?
    """, (host_ip, device_type, name))

def get_all_heat_scores():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT host_ip, device_type, name, heat_score, level,
                   datetime(last_update, 'localtime') as timestamp
            FROM state
        """)
        return cur.fetchall()
        
def update_heat_score(host_ip, device_type, name, score, level):
    execute("""
        INSERT INTO state (host_ip, device_type, name, heat_score, level)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(host_ip, device_type, name)
        DO UPDATE SET
            heat_score = excluded.heat_score,
            level = excluded.level,
            last_update = CURRENT_TIMESTAMP
    """, (host_ip, device_type, name, score, level))
    
def get_latest_metrics():
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT type, datetime(timestamp, 'localtime') as timestamp,
                   device_type, name, value, meta
            FROM metrics
            WHERE id IN (
                SELECT MAX(id)
                FROM metrics
                GROUP BY device_type, name
            )
        """)

        rows = cur.fetchall()

    data = {"cpu": {}, "disk": {}, "battery": None, "network": {}}

    for info_type, time, device_type, name, value, meta in rows:
        if info_type == "temperature":
            if device_type.lower() == "cpu":
                data["cpu"][name] = {"value":value, "time":time}
            elif device_type.lower() == "disk":
                data["disk"][name] = {"value":value, "time":time}
        elif info_type == "battery":
            data["battery"] = {"value":value, "time":time}
        elif info_type == "network":
            meta_dict = json.loads(meta)
            data["network"][value] = {"name":name, "tailscale":meta_dict["tailscale"], "local":meta_dict["local"], "time":time}

    return data

def get_metrics(start, end, tipo_info, tipo_temp, name, page=0):
    query_sql = """
        SELECT datetime(timestamp, 'localtime'), type, device_type, name, value, meta
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

    if tipo_info == "battery":
        conditions.append("type = ?")
        params.append(tipo_info)
    elif tipo_info == "temperature":
        conditions.append("type = ?")
        params.append(tipo_info)
        if tipo_temp:
            conditions.append("device_type = ?")
            params.append(tipo_temp)
        if name:
            conditions.append("name = ?")
            params.append(name)

    if conditions:
        query_sql += " WHERE " + " AND ".join(conditions)

    query_sql += " ORDER BY timestamp DESC LIMIT 100"

    if page:
        query_sql += " OFFSET ?"
        params.append(100 * page)

    return query(query_sql, params)

def get_filters(info_type, device_type):
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT type FROM metrics")
        info_types = [r[0] for r in cur.fetchall()]

        device_types = []
        if info_type == "temperature" or not info_type:
            cur.execute("""
                SELECT DISTINCT device_type
                FROM metrics
                WHERE type = 'temperature'
            """)
            device_types = [r[0] for r in cur.fetchall()]

        names = []

        if info_type == "temperature":
            if device_type:
                cur.execute("""
                    SELECT DISTINCT name
                    FROM metrics
                    WHERE type = 'temperature'
                    AND device_type = ?
                """, (device_type,))
            else:
                cur.execute("""
                    SELECT DISTINCT name
                    FROM metrics
                    WHERE type = 'temperature'
                """)
            names = [r[0] for r in cur.fetchall()]
        elif info_type == "battery":
            names = []
        elif info_type == "network":
            cur.execute("""
                SELECT DISTINCT name
                FROM metrics
                WHERE type = 'network'
            """)
            names = [r[0] for r in cur.fetchall()]
        else:
            cur.execute("SELECT DISTINCT name FROM metrics WHERE name IS NOT NULL")
            names = [r[0] for r in cur.fetchall()]

        return info_types, device_types, names

def get_daily_temperature_picks(device_type=None, name=None, page=0):
    query = """
        SELECT
            DATE(datetime(timestamp, 'localtime')) as day,
            device_type,
            name,
            MIN(value) as min_temp,
            MAX(value) as max_temp,
            AVG(value) as avg
        FROM metrics
        WHERE type = 'temperature'
    """

    params = []

    if device_type:
        query += " AND device_type = ?"
        params.append(device_type)

    if name:
        query += " AND name = ?"
        params.append(name)

    query += " GROUP BY day, device_type, name ORDER BY day DESC"
    query += " LIMIT 100"

    if page:
        query += " OFFSET ?"
        params.append(100 * page)

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()