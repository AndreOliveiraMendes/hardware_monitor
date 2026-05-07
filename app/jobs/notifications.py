from flask import current_app

from app.dao import get_pending_notifications, update_notification_status
from app.notifier.notifier import send_mail_safe, send_telegram
from config import ALERT_LEVELS


def process_notifications():
    notifications = get_pending_notifications()

    print(f"[notifications] pending={len(notifications)}")

    for n in notifications:
        nid = n[0]
        hip = n[1]
        dev = n[2]
        name = n[3]
        msg = n[4]
        level = n[5]

        try:
            print(
                f"[notifications:{nid}] "
                f"processing level={level} "
                f"host={hip} "
                f"device={dev} "
                f"name={name}"
            )

            text = (
                f"[{level.upper()}] "
                f"{hip} / "
                f"{dev} / "
                f"{name}\n"
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

            print(f"[notifications:{nid}] status=failed")