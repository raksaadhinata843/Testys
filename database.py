import sqlite3
import logging
from typing import Iterable, Dict

logger = logging.getLogger(__name__)


DB_PATH = "data/coins.db"


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Single entry point for database connection.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """
    Initialize database schema.
    """
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coins (
            id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            current_price REAL NOT NULL,
            market_cap REAL,
            market_cap_rank INTEGER,
            total_volume REAL,
            circulating_supply REAL,
            price_change_percentage_24h REAL,
            last_updated TEXT NOT NULL
        )
        """
    )

    conn.commit()


def upsert_coins(
    conn: sqlite3.Connection,
    coins: Iterable[Dict]
) -> None:
    """
    Insert or update coin snapshot data.
    """
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO coins (
            id,
            symbol,
            name,
            current_price,
            market_cap,
            market_cap_rank,
            total_volume,
            circulating_supply,
            price_change_percentage_24h,
            last_updated
        )
        VALUES (
            :id,
            :symbol,
            :name,
            :current_price,
            :market_cap,
            :market_cap_rank,
            :total_volume,
            :circulating_supply,
            :price_change_percentage_24h,
            :last_updated
        )
        ON CONFLICT(id) DO UPDATE SET
            symbol = excluded.symbol,
            name = excluded.name,
            current_price = excluded.current_price,
            market_cap = excluded.market_cap,
            market_cap_rank = excluded.market_cap_rank,
            total_volume = excluded.total_volume,
            circulating_supply = excluded.circulating_supply,
            price_change_percentage_24h = excluded.price_change_percentage_24h,
            last_updated = excluded.last_updated
        """,
        coins
    )

    conn.commit()