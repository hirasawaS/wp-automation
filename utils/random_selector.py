"""
ランダム選択ユーティリティ
使用済みキーワードを除外しながらランダム選択する
"""
import random
import json
from pathlib import Path
from .keyword_extractor import load_keywords

STATE_FILE = Path(__file__).parent.parent / "data" / "used_keywords.json"


def _load_used() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_used(used: dict):
    STATE_FILE.write_text(json.dumps(used, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_unused_keyword(category: str) -> str:
    """未使用キーワードをランダムに1つ選択。全て使用済みならリセット"""
    all_keywords = load_keywords(category)
    if not all_keywords:
        raise ValueError(f"キーワードファイルが空です: data/keywords/{category}.txt")

    used = _load_used()
    used_for_category = set(used.get(category, []))
    unused = [k for k in all_keywords if k not in used_for_category]

    if not unused:
        # 全キーワード使用済み → リセット
        used[category] = []
        unused = all_keywords

    selected = random.choice(unused)
    used.setdefault(category, []).append(selected)
    _save_used(used)
    return selected


def pick_random_topic(filepath: str) -> str:
    """マークダウンファイルから行をランダムに1つ選択"""
    path = Path(filepath)
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    return random.choice(lines) if lines else ""
