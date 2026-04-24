import logging
import os
from logging.handlers import TimedRotatingFileHandler

if not os.path.exists("logs"):
    os.makedirs("logs")

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def setup_logging(app):
    # APP LOG
    app_handler = TimedRotatingFileHandler(
        "logs/app.log",
        when="midnight",
        interval=1,
        backupCount=90,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)

    app.logger.addHandler(app_handler)
    app.logger.setLevel(logging.INFO)
