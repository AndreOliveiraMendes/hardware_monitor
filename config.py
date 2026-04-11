import os

from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "metrics.db")

FLASK_HOST = os.getenv("FLASK_HOST", "localhost")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
DEBUG_MODE = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")