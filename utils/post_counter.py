"""
1日の投稿数カウンター
"""
import json
from datetime import date
from pathlib import Path

COUNTER_FILE = Path(__file__).parent.parent / "data" / "post_counter.json"


def _load() -> dict:
    if COUNTER_FILE.exists():
        return json.loads(COUNTER_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data: dict):
    COUNTER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_today_count(category: str) -> int:
    today = str(date.today())
    data = _load()
    return data.get(today, {}).get(category, 0)


def increment_count(category: str):
    today = str(date.today())
    data = _load()
    data.setdefault(today, {})[category] = data.get(today, {}).get(category, 0) + 1
    _save(data)
