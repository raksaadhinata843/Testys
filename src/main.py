import os
import signal
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from .scraper import fetch_coins, SimpleRateLimiter
from .database import save_coins
from .logger import get_logger

logger = get_logger(__name__)

# Config via environment variables for flexibility
SCHEDULE_MINUTES = int(os.getenv("SCHEDULE_MINUTES", "60"))   # default every 60 minutes
RATE_LIMIT_INTERVAL_SECONDS = float(os.getenv("RATE_LIMIT_INTERVAL_SECONDS", "1.0"))
PER_PAGE = int(os.getenv("PER_PAGE", "50"))
PAGE = int(os.getenv("PAGE", "1"))

_rate_limiter = SimpleRateLimiter(min_interval=RATE_LIMIT_INTERVAL_SECONDS)

def job():
    logger.info("Starting scheduled job at %s", datetime.utcnow().isoformat())
    try:
        coins = fetch_coins(per_page=PER_PAGE, page=PAGE, rate_limiter=_rate_limiter)
        logger.info("Job fetched %d coins", len(coins))
        if coins:
            save_coins(coins)
            logger.info("Saved %d coins to disk", len(coins))
    except Exception as e:
        logger.exception("Job failed: %s", e)

def run_once():
    logger.info("Running scraper once (no scheduler)")
    job()

def run_scheduler():
    scheduler = BlockingScheduler()
    # Schedule job every SCHEDULE_MINUTES
    scheduler.add_job(job, 'interval', minutes=SCHEDULE_MINUTES, id="coin_scrape_job", max_instances=1)
    logger.info("Starting scheduler: interval=%s minutes", SCHEDULE_MINUTES)

    def _shutdown(signum, frame):
        logger.info("Received shutdown signal, stopping scheduler...")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    scheduler.start()

if __name__ == "__main__":
    mode = os.getenv("MODE", "daemon")  # "daemon" or "once"
    if mode == "once":
        run_once()
    else:
        run_scheduler()
