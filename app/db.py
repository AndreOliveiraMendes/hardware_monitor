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