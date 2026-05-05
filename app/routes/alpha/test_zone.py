from flask import Blueprint, request, jsonify

from app.notifier.notifier import send_mail, send_telegram
from config import INTERNAL_TOKEN

bp = Blueprint("test", __name__)

@bp.route("/test/notify")
def test_notify():
    token = request.args.get("token")

    if not token:
        return {"error": "token is required"}, 400
    elif not INTERNAL_TOKEN:
        return {"error": "internal token not configured"}, 500
    elif token != INTERNAL_TOKEN:
        return {"error": "unauthorized"}, 403
    to = request.args.get("to")
    msg = request.args.get("msg", "teste de notificação")

    success = 0
    msg = ""
    try:
        if to:
            send_mail(to, "Teste hardware_monitor", msg)
            success += 1
    except Exception as e:
        msg += f"Failed to send email: {e}\n"
        
    try:
        send_telegram(msg)
        success += 1
    except Exception as e:
        msg += f"Failed to send Telegram message: {e}\n"

    return jsonify({"status": "ok", "success": success, "msg": msg})