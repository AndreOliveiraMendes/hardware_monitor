import json
from datetime import datetime

from app.db import execute, query, query_dict
from app.extension import get_connection
from app.helpers.time import timeslice

# notification

def push_notification(host_ip, device_type, name, msg, level):
    execute("""
        INSERT INTO notifications (
            host_ip,
            device_type,
            name,
            msg,
            level,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        host_ip,
        device_type,
        name,
        msg,
        level,
        'pending'
    ))
    
def get_pending_notifications(limit=10):
    return query_dict("""
        SELECT
            id,
            host_ip,
            device_type,
            name,
            msg,
            level,
            retry_count,
            datetime(created_at, 'localtime') as created_at
        FROM notifications
        WHERE
            status = 'pending'
            OR (
                status = 'failed'
                AND retry_count < 5
                AND (
                    next_retry_at IS NULL
                    OR datetime(next_retry_at) <= datetime(CURRENT_TIMESTAMP, 'localtime')
                )
            )
        ORDER BY created_at
        LIMIT ?
    """, (limit,))
    
def update_notification_status(notification_id, status):
    execute("""
        UPDATE notifications
        SET status = ?,
            sent_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (status, notification_id))

# states
        
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

# metrics

def insert_metric(**kwargs):
    fields = list(kwargs.keys())
    values = list(kwargs.values())

    sql = f"""
        INSERT INTO metrics ({', '.join(fields)})
        VALUES ({', '.join(['?'] * len(values))})
    """

    execute(sql, values)
    
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
            dtype = device_type.lower()
            
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

def get_temperature_series(host_ip=None, device_type=None, name=None, start=None, end=None, page=0, time_window=1):
    
    filters = ["type = ? and value IS NOT NULL"]
    params = ['temperature']
    
    if host_ip:
        filters.append("host_ip = ?")
        params.append(host_ip)

    if device_type:
        filters.append("device_type = ?")
        params.append(device_type)

    if name:
        filters.append("name = ?")
        params.append(name)

    if start:
        #start = datetime.fromisoformat(start)
        filters.append("datetime(timestamp, 'localtime') >= ?")
        params.append(start)

    if end:
        #end = datetime.fromisoformat(end)
        filters.append("datetime(timestamp, 'localtime') <= ?")
        params.append(end)

    window_sql = "SELECT min(datetime(timestamp, 'localtime')), max(datetime(timestamp, 'localtime')) FROM metrics"

    window = query(window_sql + " WHERE " + " AND ".join(filters), params)
    if window[0][0] and window[0][1]:
        min_time, max_time = window[0][0], window[0][1]
        start_obj, end_obj = datetime.strptime(min_time, "%Y-%m-%d %H:%M:%S"), datetime.strptime(max_time, "%Y-%m-%d %H:%M:%S")
        slices = timeslice(start_obj, end_obj, time_window)
        
        first = 1
        last = len(slices)
        prev = page - 1 if page > first else None
        next = page + 1 if page < last else None
        try:
            page = min(last, max(first, page))
        except (ValueError, TypeError):
            page = 1
            
        query_sql = "SELECT datetime(timestamp, 'localtime'), host_name, host_ip, device_type, name, value FROM metrics"
        
        start_obj, end_obj = slices[page - 1]
        new_start, new_end = start_obj.isoformat(), end_obj.isoformat()
        op = "<"
        if page == last:
            op = "<="
        
        filters.append(f"datetime(timestamp, 'localtime') >= datetime(?) AND datetime(timestamp, 'localtime') {op} datetime(?)")
        params.append(new_start)
        params.append(new_end)
        
        data = [
            {
                "timestamp": r[0],
                "hostname": r[1],
                "host_ip": r[2],
                "device_type": r[3],
                "name": r[4],
                "value": r[5]
            }
            for r in query(query_sql + " WHERE " + " AND ".join(filters) + " ORDER BY timestamp ASC", params)
        ]

    else:
        first = None
        last = None
        prev = None
        next = None
        data = None
    
    return {
        "first": first,
        "last": last,
        "prev": prev,
        "next": next,
        "page": page,
        "data": data
    }
