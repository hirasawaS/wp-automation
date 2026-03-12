"""
キャンペーン・新着情報ジェネレーター
"""
from .base import BaseGenerator


class NewsGenerator(BaseGenerator):
    category = "news"
    prompt_file = "news.md"

    def generate(self, campaign_data: str) -> dict:
        prompt = self.prompt_template.replace("{campaign_data}", campaign_data)
        raw = self._call_ai(prompt)
        return self._parse_output(raw)
