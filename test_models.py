from validate import Coin

def test_valid_coin_should_pass():
    coin = Coin(
        name="Bitcoin",
        symbol="BTC",
        price=65000.0,
        market_cap=1_200_000_000_000,
        volume_24h=35_000_000_000
    )

    assert coin.name == "Bitcoin"
    assert coin.symbol == "BTC"