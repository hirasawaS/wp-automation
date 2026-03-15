"""
移籍者向け記事ジェネレーター
"""
from pathlib import Path
from .base import BaseGenerator
from utils.random_selector import pick_unused_keyword, pick_random_topic
from utils.web_searcher import search_shop_info

KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
KNOWLEDGE_SHOP_DIR = KNOWLEDGE_DIR / "shop"

# エリア名とファイル名のマッピング
AREA_FILE_MAP = {
    "歌舞伎町": "歌舞伎町_新宿.md",
    "新宿": "歌舞伎町_新宿.md",
    "池袋": "池袋.md",
    "渋谷": "渋谷.md",
    "上野": "上野.md",
    "秋葉原": "秋葉原.md",
    "新橋": "新橋.md",
    "恵比寿": "恵比寿.md",
    "赤坂": "赤坂.md",
    "六本木": "その他エリア.md",
    "中野": "その他エリア.md",
    "大宮": "その他エリア.md",
    "浅草": "その他エリア.md",
    "神田": "その他エリア.md",
    "西新宿": "その他エリア.md",
}


def _load_shop_knowledge(topic: str = "") -> str:
    """
    baseナレッジ全部 + shopはトピックに関連するエリアファイルのみ読み込む。
    エリアが特定できない場合は index.md（概要）のみ。
    """
    parts = []

    # knowledge/base/ は全部読む
    for md_file in sorted((KNOWLEDGE_DIR / "base").glob("*.md")):
        parts.append(md_file.read_text(encoding="utf-8"))

    # shop: トピックに含まれるエリアのファイルを特定
    matched_files = set()
    for area, filename in AREA_FILE_MAP.items():
        if area in topic:
            matched_files.add(filename)

    if matched_files:
        for filename in sorted(matched_files):
            path = KNOWLEDGE_SHOP_DIR / filename
            if path.exists():
                parts.append(path.read_text(encoding="utf-8"))
    else:
        # エリア不明 → index.md（全店概要）だけ入れる
        index_path = KNOWLEDGE_SHOP_DIR / "index.md"
        parts.append(index_path.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(parts)


class MigrationGenerator(BaseGenerator):
    category = "migration"
    prompt_file = "migration.md"

    def generate(self, topic: str = None, shop_info: str = "") -> dict:
        if not topic:
            topic = pick_unused_keyword("migration")

        if not shop_info:
            # ナレッジDB（ローカル）+ Web検索（最新情報）を合わせて渡す
            local_knowledge = _load_shop_knowledge(topic)
            web_info = search_shop_info(topic)
            shop_info = f"## ナレッジDB（店舗情報）\n\n{local_knowledge}\n\n## Web検索（最新求人情報）\n\n{web_info}"

        prompt = (
            self.prompt_template
            .replace("{topic}", topic)
            .replace("{shop_info}", shop_info)
        )
        raw = self._call_ai(prompt)
        result = self._parse_output(raw)
        result["topic"] = topic
        if not result["title"]:
            result["title"] = topic
        return result
