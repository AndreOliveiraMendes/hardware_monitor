from flask import current_app

from app.dao import get_pending_notifications, update_notification_status
from app.notifier.notifier import send_mail_safe, send_telegram
from config import ALERT_LEVELS


def process_notifications():
    notifications = get_pending_notifications()

    for n in notifications:
        try:
            text = (
                f"[{n['level'].upper()}] "
                f"{n['host_ip']} / "
                f"{n['device_type']} / "
                f"{n['name']}\n"
                f"{n['msg']}"
            )

            send_telegram(text)

            if n["level"] in ALERT_LEVELS:
                send_mail_safe(
                    "ao_mendes@hotmail.com",
                    n["level"],
                    text
                )

            update_notification_status(n["id"], "sent")

        except Exception as e:
            current_app.logger.error(
                f"erro ao processar notification {n['id']}: {e}"
            )

            update_notification_status(n["id"], "failed")