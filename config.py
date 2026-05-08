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

# alert_params
TEMP_LEVELS = {
    "CPU":[
        {"value": 70, "color": "f1c40f", "label_bgcolor": "f1c40f", "label_color": "000"},
        {"value": 75, "color": "e67e22", "label_bgcolor": "e67e22", "label_color": "fff"},
        {"value": 80, "color": "e74c3c", "label_bgcolor": "e74c3c", "label_color": "fff"},
        {"value": 90, "color": "8b0000", "label_bgcolor": "8b0000", "label_color": "fff"},
    ],
    "HD":[
        
    ]
}

TEMP_RULES = {
    "CPU": [
        {"max": 35, "delta": -4},
        {"max": 50, "delta": -2},
        {"max": 60, "delta": -1},
        {"max": 70, "delta": 0},
        {"max": 75, "delta": +1},
        {"max": 80, "delta": +2},
        {"max": 90, "delta": +4},
        {"max": float("inf"), "delta": +8},
    ],
    "disk": [
        {"max": 35, "delta": -2},
        {"max": 40, "delta": -1},
        {"max": 45, "delta": +1},
        {"max": 50, "delta": +2},
        {"max": 55, "delta": +3},
        {"max": float("inf"), "delta": +5},
    ]
}

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