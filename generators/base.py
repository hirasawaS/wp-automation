"""
記事生成の基底クラス
"""
import os
import anthropic
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class BaseGenerator:
    """全記事ジェネレーターの共通処理"""

    category: str = ""          # "blog" | "migration" | "shop" | "news"
    prompt_file: str = ""       # prompts/ 以下のファイル名

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.prompt_template = self._load_prompt()

    def _load_prompt(self) -> str:
        path = PROMPTS_DIR / self.prompt_file
        return path.read_text(encoding="utf-8")

    def _call_ai(self, prompt: str) -> str:
        from config.settings import AI_MODEL
        message = self.client.messages.create(
            model=AI_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    def generate(self, **kwargs) -> dict:
        """
        記事を生成して返す。
        Returns: {"title": str, "content": str, "meta_description": str, "category": str}
        """
        raise NotImplementedError

    def _parse_output(self, raw: str) -> dict:
        """AIの出力をパースしてdict形式に変換"""
        lines = raw.strip().split("\n")
        title = ""
        meta = ""
        content_lines = []
        in_content = False

        for line in lines:
            if line.startswith("タイトル："):
                title = line.replace("タイトル：", "").strip()
            elif line.startswith("メタディスクリプション："):
                meta = line.replace("メタディスクリプション：", "").strip()
            elif line.startswith("本文："):
                in_content = True
                rest = line.replace("本文：", "").strip()
                if rest:
                    content_lines.append(rest)
            elif in_content:
                content_lines.append(line)

        return {
            "title": title,
            "content": "\n".join(content_lines),
            "meta_description": meta,
            "category": self.category,
        }
