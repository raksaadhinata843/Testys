from pathlib import Path
import sqlite3
import json
from typing import List, Optional
from src.models import Coin

DB_DIR = Path("data")
DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB = DB_DIR / "coins.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS coins (
    id TEXT PRIMARY KEY,
    symbol TEXT,
    name TEXT,
    current_price REAL,
    market_cap REAL,
    market_cap_rank INTEGER,
    total_volume REAL,
    high_24h REAL,
    low_24h REAL,
    price_change_24h REAL,
    price_change_percentage_24h REAL,
    market_cap_change_24h REAL,
    circulating_supply REAL,
    total_supply REAL,
    ath REAL,
    atl REAL,
    last_updated TEXT,
    raw_json TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def _get_conn(path: Path = DEFAULT_DB):
    conn = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(path: Path = DEFAULT_DB) -> None:
    conn = _get_conn(path)
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()

def _coin_to_row(coin: Coin) -> dict:
    d = coin.dict(by_alias=True)
    # Ensure last_updated serializable (ISO string)
    d["last_updated"] = d.get("last_updated")
    return d

def save_coins(coins: List[Coin], path: Path = DEFAULT_DB) -> None:
    """
    Upsert coins into SQLite DB. Uses `id` as primary key (replace on conflict).
    """
    init_db(path)
    conn = _get_conn(path)
    try:
        with conn:
            for coin in coins:
                row = _coin_to_row(coin)
                raw = json.dumps(row, default=str, ensure_ascii=False)
                conn.execute(
                    """
                    INSERT INTO coins (
                        id, symbol, name, current_price, market_cap, market_cap_rank,
                        total_volume, high_24h, low_24h, price_change_24h, price_change_percentage_24h,
                        market_cap_change_24h, circulating_supply, total_supply, ath, atl,
                        last_updated, raw_json, updated_at
                    ) VALUES (
                        :id, :symbol, :name, :current_price, :market_cap, :market_cap_rank,
                        :total_volume, :high_24h, :low_24h, :price_change_24h, :price_change_percentage_24h,
                        :market_cap_change_24h, :circulating_supply, :total_supply, :ath, :atl,
                        :last_updated, :raw_json, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT(id) DO UPDATE SET
                        symbol=excluded.symbol,
                        name=excluded.name,
                        current_price=excluded.current_price,
                        market_cap=excluded.market_cap,
                        market_cap_rank=excluded.market_cap_rank,
                        total_volume=excluded.total_volume,
                        high_24h=excluded.high_24h,
                        low_24h=excluded.low_24h,
                        price_change_24h=excluded.price_change_24h,
                        price_change_percentage_24h=excluded.price_change_percentage_24h,
                        market_cap_change_24h=excluded.market_cap_change_24h,
                        circulating_supply=excluded.circulating_supply,
                        total_supply=excluded.total_supply,
                        ath=excluded.ath,
                        atl=excluded.atl,
                        last_updated=excluded.last_updated,
                        raw_json=excluded.raw_json,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    {
                        **row,
                        "raw_json": raw
                    }
                )
    finally:
        conn.close()

def load_coins(path: Path = DEFAULT_DB) -> List[dict]:
    """
    Return list of raw JSON dicts from DB.
    """
    if not path.exists():
        return []
    conn = _get_conn(path)
    try:
        cur = conn.execute("SELECT raw_json FROM coins")
        rows = cur.fetchall()
        out = []
        for r in rows:
            try:
                out.append(json.loads(r["raw_json"]))
            except Exception:
                # fallback: skip invalid row
                continue
        return out
    finally:
        conn.close()
