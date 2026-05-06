import json
from datetime import datetime

from app.db import execute, query
from app.extension import get_connection


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
    with get_connection() as conn:
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
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT type, datetime(timestamp, 'localtime') as timestamp,
                   host_name, host_ip, device_type, name, value, meta
            FROM metrics
            WHERE id IN (
                SELECT MAX(id)
                FROM metrics
                GROUP BY type, device_type, host_ip, name
            )
        """)

        rows = cur.fetchall()

    data = {
        "temperature":{
            "cpu": {},
            "disk": {}
        },
        "health": {
            "cpu": {},
            "disk": {}
        },
        "battery": {},
        "network": {}
    }

    for info_type, time, hn, hip, device_type, name, value, meta in rows:
        # garante host
        for key in ["cpu", "disk", "battery", "network"]:
            if key not in ["battery", "cpu", "disk"]:
                data[key].setdefault(hip, {})
            elif key in ["cpu", "disk"]:
                data["temperature"][key].setdefault(hip, {})
                data["health"][key].setdefault(hip, {})

        if info_type == "temperature":
            dtype = device_type.lower()

            if dtype in ["cpu", "disk"]:
                # 👇 agora preserva "name" (core0, core1, sda1, etc)
                data[info_type][dtype][hip][name] = {
                    "hostname": hn,
                    "value": value,
                    "time": time,
                    "meta": meta
                }

        elif info_type == "health":
            data[info_type][dtype][hip][name] = {
                "hostname": hn,
                "value": value,
                "time": time,
                "meta": meta
            }

        elif info_type == "battery":
            data["battery"][hip] = {
                "hostname": hn,
                "value": value,
                "time": time,
                "meta": meta
            }

        elif info_type == "network":
            meta_dict = json.loads(meta or "{}")

            data["network"][hip][value] = {
                "hostname": hn,
                "name": name,
                "tailscale": meta_dict.get("tailscale"),
                "local": meta_dict.get("self"),
                "time": time
            }

    return data

def get_metrics(start, end, host_ip, tipo_info, tipo_disp, name, page=0, per_page=100):
    base_query = """
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

    if host_ip:
        conditions.append("host_ip = ?")
        params.append(host_ip)
        
    if tipo_info:
        conditions.append("type = ?")
        params.append(tipo_info)
        
    if tipo_disp:
        conditions.append("device_type = ?")
        params.append(tipo_disp)
        
    if name:
        conditions.append("name = ?")
        params.append(name)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # total count
    count_sql = "SELECT COUNT(*) " + base_query
    total = query(count_sql, params)[0][0]

    # dados paginados
    data_sql = f"""
        SELECT datetime(timestamp, 'localtime'), host_name, host_ip, type, device_type, name, value, meta
        {base_query}
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """

    params_data = params + [per_page, page * per_page]
    rows = query(data_sql, params_data)

    return {
        "data": rows,
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_next": (page + 1) * per_page < total,
        "has_prev": page > 0
    }

def get_filters(info_type, host_ip, device_type):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT type FROM metrics")
        info_types = [r[0] for r in cur.fetchall()]
        
        filters = []
        params = []
        
        if info_type:
            filters.append("type = ?")
            params.append(info_type)
            
        base_sql = "SELECT DISTINCT host_ip FROM metrics"
        if filters:
            base_sql += " WHERE " + " AND ".join(filters)
        
        cur.execute(base_sql, params)
        host_ips = [r[0] for r in cur.fetchall()]
        
        if host_ip:
            filters.append("host_ip = ?")
            params.append(host_ip)
            
        base_sql = "SELECT DISTINCT device_type FROM metrics"
        if filters:
            base_sql += " WHERE " + " AND ".join(filters)
            
        cur.execute(base_sql, params)
        device_types = [r[0] for r in cur.fetchall()]
        
        if device_type:
            filters.append("device_type = ?")
            params.append(device_type)
            
        base_sql = "SELECT DISTINCT name FROM metrics"
        if filters:
            base_sql += " WHERE " + " AND ".join(filters)
        
        cur.execute(base_sql, params)
        names = [r[0] for r in cur.fetchall() if r[0] != None]

        return info_types, host_ips, device_types, names

def get_daily_temperature_picks(host_ip = None, device_type=None, name=None, page=0, per_page=100):
    base_query = """
        FROM metrics
        WHERE type = 'temperature' and value IS NOT NULL
    """

    params = []
    
    if host_ip:
        base_query += " AND host_ip = ?"
        params.append(host_ip)

    if device_type:
        base_query += " AND device_type = ?"
        params.append(device_type)

    if name:
        base_query += " AND name = ?"
        params.append(name)

    group_by = " GROUP BY day, host_ip, device_type, name"

    # total
    count_query = f"""
        SELECT COUNT(*) FROM (
            SELECT 1
            {base_query}
            GROUP BY DATE(datetime(timestamp, 'localtime')), host_ip, device_type, name
        )
    """

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(count_query, params)
        total = cur.fetchone()[0]

        data_query = f"""
            SELECT
                DATE(datetime(timestamp, 'localtime')) as day,
                host_ip,
                device_type,
                name,
                MIN(value),
                MAX(value),
                AVG(value)
            {base_query}
            GROUP BY day, host_ip, device_type, name
            ORDER BY day DESC
            LIMIT ? OFFSET ?
        """

        cur.execute(data_query, params + [per_page, page * per_page])
        rows = cur.fetchall()

    return {
        "data": rows,
        "page": page,
        "per_page": per_page,
        "total": total,
        "has_next": (page + 1) * per_page < total,
        "has_prev": page > 0
    }
    
def get_temperature_series(host_ip=None, device_type=None, name=None, start=None, end=None, page=0, per_page=420):
    query_sql = """
        SELECT datetime(timestamp, 'localtime'), host_name, host_ip, device_type, name, value
        FROM metrics
        WHERE type = 'temperature' and value IS NOT NULL
    """

    params = []
    
    if host_ip:
        query_sql += " AND host_ip = ?"
        params.append(host_ip)

    if device_type:
        query_sql += " AND device_type = ?"
        params.append(device_type)

    if name:
        query_sql += " AND name = ?"
        params.append(name)

    if start:
        start = datetime.fromisoformat(start)
        query_sql += " AND datetime(timestamp, 'localtime') >= ?"
        params.append(start)

    if end:
        end = datetime.fromisoformat(end)
        query_sql += " AND datetime(timestamp, 'localtime') <= ?"
        params.append(end)

    query_sql += " ORDER BY timestamp LIMIT ?"
    params.append(per_page)
    
    if page:
        query_sql += f" OFFSET ?"
        params.append(page * per_page)

    return query(query_sql, params)
