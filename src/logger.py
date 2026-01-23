import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "logs/coin_scraper.log")

# Ensure logs dir exists
from pathlib import Path
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

def get_logger(name: str = "coin_scraper"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # avoid adding handlers multiple times

    logger.setLevel(LOG_LEVEL)

    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    formatter = logging.Formatter(fmt)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Rotating file handler
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
