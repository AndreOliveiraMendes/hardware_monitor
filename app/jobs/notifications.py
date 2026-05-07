from flask import current_app

from app.dao import get_pending_notifications, update_notification_status
from app.notifier.notifier import send_mail_safe, send_telegram
from config import ALERT_LEVELS


def process_notifications():
    notifications = get_pending_notifications()

    print(f"[notifications] pending={len(notifications)}")

    for n in notifications:
        nid = n["id"]

        try:
            print(
                f"[notifications:{nid}] "
                f"processing level={n['level']} "
                f"host={n['host_ip']} "
                f"device={n['device_type']} "
                f"name={n['name']}"
            )

            text = (
                f"[{n['level'].upper()}] "
                f"{n['host_ip']} / "
                f"{n['device_type']} / "
                f"{n['name']}\n"
                f"{n['msg']}"
            )

            send_telegram(text)
            print(f"[notifications:{nid}] telegram=ok")

            if n["level"] in ALERT_LEVELS:
                send_mail_safe(
                    "ao_mendes@hotmail.com",
                    n["level"],
                    text
                )
                print(f"[notifications:{nid}] mail=ok")

            update_notification_status(n["id"], "sent")

            print(f"[notifications:{nid}] status=sent")

        except Exception as e:
            print(f"[notifications:{nid}] ERROR: {e}")

            current_app.logger.exception(
                f"erro ao processar notification {nid}"
            )

            update_notification_status(n["id"], "failed")

            print(f"[notifications:{nid}] status=failed")