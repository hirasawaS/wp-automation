"""
記事生成の基底クラス
"""
import os
import re
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
        # タイトル（同行 or 次行どちらでも対応）
        title_match = re.search(r"タイトル[：:][^\S\n]*\n?\s*(.+)", raw)
        title = title_match.group(1).strip() if title_match else ""

        # メタディスクリプション（同行 or 次行どちらでも対応）
        meta_match = re.search(r"メタディスクリプション[：:][^\S\n]*\n?\s*(.+)", raw)
        meta = meta_match.group(1).strip() if meta_match else ""

        # 本文: ```html...``` ブロック優先、なければ 本文：以降、なければ --- 以降
        html_block = re.search(r"```html\s*([\s\S]+?)```", raw)
        if html_block:
            content = html_block.group(1).strip()
        else:
            body_match = re.search(r"本文[：:]\s*([\s\S]+?)(?:メタディスクリプション[：:]|$)", raw)
            if body_match:
                content = body_match.group(1).strip()
            else:
                # --- 以降をフォールバックとして使用
                parts = re.split(r"\n---+\n", raw, maxsplit=1)
                content = parts[1].strip() if len(parts) > 1 else ""

        return {
            "title": title,
            "content": content,
            "meta_description": meta,
            "category": self.category,
        }
