import requests
import time
import logging

BASE_URL = "https://api.coingecko.com/api/v3/coins/markets"

PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 50,
    "sparkline": "false"
}

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "portfolio-scraper/1.0"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_page(page: int, retry: int = 3):
    params = PARAMS | {"page": page}

    for attempt in range(retry):
        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            wait = 2 ** attempt
            logger.warning(f"Rate limited. Sleeping {wait}s...")
            time.sleep(wait)
            continue

        response.raise_for_status()

    logger.error(f"Failed to fetch page {page}")
    return []


def run_scraper(max_pages: int = 3):
    all_data = []

    for page in range(1, max_pages + 1):
        logger.info(f"Fetching page {page}")
        data = fetch_page(page)

        if not data:
            break

        all_data.extend(data)
        time.sleep(1)  # rate limit ringan, cukup

    return all_data


if __name__ == "__main__":
    coins = run_scraper(max_pages=5)
    logger.info(f"Fetched {len(coins)} records")