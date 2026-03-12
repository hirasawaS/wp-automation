"""
初心者SEO記事ジェネレーター
"""
from .base import BaseGenerator
from utils.random_selector import pick_unused_keyword


class BlogGenerator(BaseGenerator):
    category = "blog"
    prompt_file = "blog.md"

    def generate(self, keyword: str = None) -> dict:
        if not keyword:
            keyword = pick_unused_keyword("blog")

        prompt = self.prompt_template.replace("{keyword}", keyword)
        raw = self._call_ai(prompt)
        result = self._parse_output(raw)
        result["keyword"] = keyword
        return result
