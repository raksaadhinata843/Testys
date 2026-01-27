import requests
import time
import threading
from typing import List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.models import Coin
from src.logger import get_logger
import os

logger = get_logger(__name__)

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

class ScraperError(Exception):
    pass

class SimpleRateLimiter:
    """
    Very small rate limiter: ensures at least `min_interval` seconds between consecutive requests.
    Thread-safe.
    """
    def __init__(self, min_interval: float = 1.0):
        self.min_interval = float(min_interval)
        self._lock = threading.Lock()
        self._last_call = 0.0

    def acquire(self):
        with self._lock:
            now = time.time()
            wait_for = self.min_interval - (now - self._last_call)
            if wait_for > 0:
                logger.debug("RateLimiter: sleeping %.3fs to respect rate limit", wait_for)
                time.sleep(wait_for)
            self._last_call = time.time()

# default can be overridden by environment variable RATE_LIMIT_INTERVAL_SECONDS
_default_rate_limit = float(os.getenv("RATE_LIMIT_INTERVAL_SECONDS", "1.0"))
_global_rate_limiter = SimpleRateLimiter(min_interval=_default_rate_limit)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type((requests.RequestException, ScraperError)))
def fetch_coins(vs_currency: str = "usd", order: str = "market_cap_desc",
                per_page: int = 50, page: int = 1, sparkline: bool = False,
                timeout: int = 10, rate_limiter: Optional[SimpleRateLimiter] = None) -> List[Coin]:
    """
    Fetch one page of coins and return validated Pydantic objects.
    Use `rate_limiter` to ensure we don't hit the API too frequently.
    """
    rl = rate_limiter or _global_rate_limiter
    rl.acquire()
    params = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": str(sparkline).lower()
    }
    logger.info("Requesting CoinGecko: page=%s per_page=%s", page, per_page)
    try:
        resp = requests.get(BASE_URL, params=params, timeout=timeout)
    except Exception as e:
        logger.exception("Network error when fetching coins: %s", e)
        raise

    if resp.status_code != 200:
        logger.error("Unexpected status code %s: %s", resp.status_code, resp.text)
        raise ScraperError(f"unexpected status code: {resp.status_code} - {resp.text}")

    try:
        data = resp.json()
    except Exception as e:
        logger.exception("Failed to decode JSON response: %s", e)
        raise ScraperError("invalid json response")

    coins: List[Coin] = []
    for item in data:
        try:
            coin = Coin.parse_obj(item)
            coins.append(coin)
        except Exception as e:
            # Skip invalid items but log details
            logger.warning("Validation failed for item id=%s: %s", item.get("id"), e)
    logger.info("Fetched %d valid coins from page %s", len(coins), page)
    return coins
