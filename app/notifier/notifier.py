import subprocess
import urllib.parse
import urllib.request

from config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


def send_mail(to, subject, body):
    lines = [
        "From: seu@email.com",
        f"To: {to}",
        f"Subject: {subject}",
        "",
        body
    ]

    msg = "\n".join(lines)

    subprocess.run(
        ["/usr/sbin/sendmail", "-t", "-i"],
        input=msg.encode("utf-8"),
        check=True
    )

def send_telegram(msg):
    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }).encode()

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    req = urllib.request.Request(url, data=data)
    urllib.request.urlopen(req)