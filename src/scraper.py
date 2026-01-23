import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .models import Coin

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

class ScraperError(Exception):
    pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type((requests.RequestException, ScraperError)))
def fetch_coins(vs_currency: str = "usd", order: str = "market_cap_desc",
                per_page: int = 50, page: int = 1, sparkline: bool = False, timeout: int = 10) -> List[Coin]:
    params = {
        "vs_currency": vs_currency,
        "order": order,
        "per_page": per_page,
        "page": page,
        "sparkline": str(sparkline).lower()
    }
    resp = requests.get(BASE_URL, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise ScraperError(f"unexpected status code: {resp.status_code} - {resp.text}")
    data = resp.json()
    coins = []
    for item in data:
        try:
            coin = Coin.parse_obj(item)
            coins.append(coin)
        except Exception as e:
            # If a single item fails validation, skip it but log (print) the issue
            print(f"[scraper] validation failed for item {item.get('id')}: {e}")
    return coins
