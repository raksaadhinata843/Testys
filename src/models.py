from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dateutil import parser as date_parser

class Coin(BaseModel):
    id: str
    symbol: str
    name: str
    image: Optional[str]
    current_price: float = Field(..., alias="current_price")
    market_cap: Optional[float]
    market_cap_rank: Optional[int]
    total_volume: Optional[float]
    high_24h: Optional[float]
    low_24h: Optional[float]
    price_change_24h: Optional[float]
    price_change_percentage_24h: Optional[float]
    market_cap_change_24h: Optional[float]
    circulating_supply: Optional[float]
    total_supply: Optional[float]
    ath: Optional[float]
    atl: Optional[float]
    last_updated: datetime

    @field_validator("last_updated", mode="before")
    def parse_last_updated(cls, v):
        if not v:
            return datetime.now   
            raise ValueError("last_updated is required")
        if isinstance(v, datetime):
            return v
        try:
            return date_parser.parse(v)
        except Exception as e:
            raise ValueError(f"invalid last_updated: {e}")
