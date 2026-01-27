import json
from pathlib import Path
from typing import List
from src.models import Coin

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_FILE = DATA_DIR / "coins.json"

def save_coins(coins: List[Coin], path: Path = DEFAULT_FILE) -> None:
    serializable = [c.dict(by_alias=True) for c in coins]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, default=str, indent=2)

def load_coins(path: Path = DEFAULT_FILE) -> List[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
