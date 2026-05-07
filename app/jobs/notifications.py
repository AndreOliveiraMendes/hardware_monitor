from datetime import datetime, timedelta

from flask import current_app

from app.dao import get_pending_notifications, update_notification_status
from app.db import execute
from app.notifier.notifier import send_mail_safe, send_telegram
from config import ALERT_LEVELS


def process_notifications():
    notifications = get_pending_notifications()

    print(f"[notifications] processing {len(notifications)} notifications")

    for n in notifications:
        nid = n["id"]
        hip = n["host_ip"]
        dev = n["device_type"]
        name = n["name"]
        msg = n["msg"]
        level = n["level"]
        created_at = n["created_at"]

        try:
            print(
                f"[notifications:{nid}] "
                f"processing level={level} host={hip} device={dev} name={name} at {created_at}"
            )

            text = (
                f"[{level.upper()}] "
                f"{hip} / {dev} / {name} / {created_at}\n"
                f"{msg}"
            )

            send_telegram(text)
            print(f"[notifications:{nid}] telegram=ok")

            if level in ALERT_LEVELS:
                send_mail_safe(
                    "ao_mendes@hotmail.com",
                    level,
                    text
                )
                print(f"[notifications:{nid}] mail=ok")

            update_notification_status(nid, "sent")

            print(f"[notifications:{nid}] status=sent")

        except Exception as e:
            print(f"[notifications:{nid}] ERROR: {e}")

            current_app.logger.exception(
                f"erro ao processar notification {nid}"
            )

            update_notification_status(nid, "failed")
            schedule_retry(nid, n["retry_count"])

            print(f"[notifications:{nid}] status=failed")
            
def schedule_retry(nid, retry_count):
    delay = min(60 * (2 ** retry_count), 3600)

    next_retry = (datetime.now() + timedelta(seconds=delay)).isoformat()

    execute("""
        UPDATE notifications
        SET
            retry_count = retry_count + 1,
            next_retry_at = ?
        WHERE id = ?
    """, (next_retry, nid))