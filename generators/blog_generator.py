"""
初心者SEO記事ジェネレーター
"""
import json
import logging
import re
from pathlib import Path
import urllib.request
from html.parser import HTMLParser
from .base import BaseGenerator
from utils.random_selector import pick_unused_keyword

INTERNAL_LINKS_FILE = Path(__file__).parent.parent / "data" / "internal_links.json"

logger = logging.getLogger(__name__)
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge" / "base"


class _TextExtractor(HTMLParser):
    """HTMLからテキストのみ抽出するシンプルなパーサー"""
    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer", "header"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "header"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            text = data.strip()
            if text:
                self._parts.append(text)

    def get_text(self):
        return "\n".join(self._parts)


class BlogGenerator(BaseGenerator):
    category = "blog"
    prompt_file = "blog.md"

    def _apply_internal_links(self, html: str) -> str:
        """internal_links.json を元に店舗名・キーワードをリンクに置換する"""
        if not INTERNAL_LINKS_FILE.exists():
            return html
        mapping: dict = json.loads(INTERNAL_LINKS_FILE.read_text(encoding="utf-8"))

        def replace_outside_tags(keyword: str, url: str, text: str) -> tuple[str, int]:
            """<a>タグの外にあるキーワードを最初の1件だけリンクに置換する"""
            result = []
            replaced = 0
            # タグとテキストに分割して処理
            parts = re.split(r"(<[^>]+>)", text)
            in_anchor = False
            for part in parts:
                if re.match(r"<a[\s>]", part, re.IGNORECASE):
                    in_anchor = True
                    result.append(part)
                elif re.match(r"</a>", part, re.IGNORECASE):
                    in_anchor = False
                    result.append(part)
                elif part.startswith("<"):
                    result.append(part)
                else:
                    if not in_anchor and not replaced:
                        new_part, n = re.subn(
                            re.escape(keyword),
                            f'<a href="{url}">{keyword}</a>',
                            part,
                            count=1,
                        )
                        result.append(new_part)
                        replaced += n
                    else:
                        result.append(part)
            return "".join(result), replaced

        # 長いキーワードを優先してマッチ（短いものが先にヒットするのを防ぐ）
        for keyword in sorted(mapping, key=len, reverse=True):
            url = mapping[keyword]
            html, count = replace_outside_tags(keyword, url, html)
            if count:
                logger.debug(f"内部リンク挿入: {keyword} → {url}")
        return html

    def _load_knowledge(self) -> str:
        files = sorted(KNOWLEDGE_DIR.glob("*.md"))
        return "\n\n".join(f.read_text(encoding="utf-8") for f in files)

    def _fetch_url(self, url: str, max_chars: int = 3000) -> str:
        """URLのテキストコンテンツを取得して返す"""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as res:
                html = res.read().decode("utf-8", errors="ignore")
            parser = _TextExtractor()
            parser.feed(html)
            text = parser.get_text()
            # 空行を圧縮して文字数制限
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text[:max_chars]
        except Exception as e:
            logger.warning(f"URL取得失敗: {url} ({e})")
            return ""

    def generate(self, keyword: str = None) -> dict:
        from config.settings import BLOG_REFERENCE_URLS
        if not keyword:
            keyword = pick_unused_keyword("blog")

        knowledge = self._load_knowledge()

        web_texts = []
        for url in BLOG_REFERENCE_URLS:
            text = self._fetch_url(url)
            if text:
                web_texts.append(f"### 参照: {url}\n{text}")
        web_knowledge = "\n\n".join(web_texts)

        full_knowledge = knowledge + ("\n\n## 外部サイト参考情報\n" + web_knowledge if web_knowledge else "")
        prompt = self.prompt_template.replace("{keyword}", keyword).replace("{knowledge}", full_knowledge)
        raw = self._call_ai(prompt)
        result = self._parse_output(raw)
        result["content"] = self._apply_internal_links(result["content"])
        result["keyword"] = keyword
        return result
