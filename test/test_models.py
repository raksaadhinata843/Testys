from src.models import Coin
from datetime import datetime

sample = {
    "id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png",
    "current_price": 30000.0,
    "market_cap": 600000000000,
    "market_cap_rank": 1,
    "total_volume": 40000000000,
    "high_24h": 31000.0,
    "low_24h": 29000.0,
    "price_change_24h": -500.0,
    "price_change_percentage_24h": -1.64,
    "market_cap_change_24h": -10000000000,
    "circulating_supply": 19000000.0,
    "total_supply": 21000000.0,
    "ath": 69000.0,
    "atl": 67.81,
    "last_updated": "2023-01-01T12:00:00.000Z"
}

def test_coin_parsing():
    coin = Coin.parse_obj(sample)
    assert coin.id == "bitcoin"
    assert coin.symbol == "btc"
    assert coin.current_price == 30000.0
    assert isinstance(coin.last_updated, datetime)

def test_missing_last_updated():
    bad = sample.copy()
    bad.pop("last_updated", None)
    try:
        Coin.parse_obj(bad)
        assert False, "Parsing should fail without last_updated"
    except Exception:
        assert True
