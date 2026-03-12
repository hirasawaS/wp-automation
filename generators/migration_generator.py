"""
移籍者向け記事ジェネレーター
"""
from .base import BaseGenerator
from utils.random_selector import pick_unused_keyword, pick_random_topic


class MigrationGenerator(BaseGenerator):
    category = "migration"
    prompt_file = "migration.md"

    def generate(self, topic: str = None, shop_info: str = "") -> dict:
        if not topic:
            topic = pick_unused_keyword("migration")

        prompt = (
            self.prompt_template
            .replace("{topic}", topic)
            .replace("{shop_info}", shop_info)
        )
        raw = self._call_ai(prompt)
        result = self._parse_output(raw)
        result["topic"] = topic
        return result
