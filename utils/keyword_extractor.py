"""
キーワード抽出ユーティリティ
LINE相談ログ・X質問テキストからSEOキーワードを抽出する
"""
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_keywords(category: str) -> list[str]:
    """キーワードファイルから有効なキーワードを読み込む（#コメント行除外）"""
    path = DATA_DIR / "keywords" / f"{category}.txt"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]


def extract_keywords_from_text(text: str, min_length: int = 4) -> list[str]:
    """テキストから日本語フレーズを簡易抽出（LINE/Xログ解析用）"""
    # 句読点・記号で分割して一定長以上のフレーズを抽出
    phrases = re.split(r'[、。！？\n\r\t　 ]+', text)
    return [p.strip() for p in phrases if len(p.strip()) >= min_length]
