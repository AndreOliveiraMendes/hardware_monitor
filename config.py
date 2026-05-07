import os

from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "metrics.db")

FLASK_HOST = os.getenv("FLASK_HOST", "localhost")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Telegram bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# smtp configuration
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"

# test token
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN")

# collect params
LEVEL_ORDER = {
    "ok": 0,
    "warning": 1,
    "high": 2,
    "critical": 3,
    "no temp": -1
}
ALERT_LEVELS = {
    "high",
    "critical"
}