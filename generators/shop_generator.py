"""
店舗紹介記事ジェネレーター
"""
from .base import BaseGenerator


class ShopGenerator(BaseGenerator):
    category = "shop"
    prompt_file = "shop.md"

    def generate(self, shop_data: str) -> dict:
        prompt = self.prompt_template.replace("{shop_data}", shop_data)
        raw = self._call_ai(prompt)
        return self._parse_output(raw)
