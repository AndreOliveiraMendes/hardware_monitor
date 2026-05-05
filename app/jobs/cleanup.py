from app.extension import get_connection


def cleanup(days=30):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            DELETE FROM metrics
            WHERE timestamp < datetime('now', ?)
        """, (f"-{days} days",))

        deleted = cur.rowcount
        
        conn.commit()
        
    print(f"[cleanup] removed {deleted} rows older than {days} days")
    return deleted