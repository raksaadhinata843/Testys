import logging

from scraper import fetch_coins
from models import Coin
from database import save_coins


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting weather scraper pipeline")

    try:
        init_db()
        logger.info("Database initialized")

        raw_data = run_scraper()
        logger.info(f"Fetched {len(raw_data)} records")

        validated = []
        for item in raw_data:
            try:
                validated.append(Coin(**item))
            except Exception as e:
                logger.warning(f"Validation failed for item: {e}")

        if not validated:
            logger.error("No valid data to save. Aborting.")
            return

        upsert_coins(validated)
        logger.info(f"Saved {len(validated)} records to database")

    except Exception as e:
        logger.exception("Fatal error in main pipeline")
        raise  # biar CI/CD tetap fail


if __name__ == "__main__":

    main()
