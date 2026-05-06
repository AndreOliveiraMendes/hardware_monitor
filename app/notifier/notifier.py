import smtplib
import urllib.parse
import urllib.request
from email.mime.text import MIMEText

from config import (SMTP_FROM, SMTP_HOST, SMTP_PASS, SMTP_PORT, SMTP_TLS,
                    SMTP_USER, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)


def send_mail(to, subject, body):
    if not SMTP_HOST:
        raise RuntimeError("SMTP_HOST não configurado")

    from_addr = SMTP_FROM or SMTP_USER
    if not from_addr:
        raise RuntimeError("SMTP_FROM ou SMTP_USER precisa estar definido")

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
        if SMTP_TLS:
            server.starttls()

        if SMTP_USER and SMTP_PASS:
            server.login(SMTP_USER, SMTP_PASS)

        server.send_message(msg)
        
def send_mail_safe(to, subject, body):
    try:
        send_mail(to, subject, body)
        return True
    except Exception as e:
        print(f"mail error: {e}")
        return False

def send_telegram(msg):
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }).encode()

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    req = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req)