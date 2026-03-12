"""
テキスト整形ユーティリティ
"""
import re


def format_html(text: str) -> str:
    """AIが生成したテキストをWordPress向けHTMLに整形"""
    # 余分な空白行を1行に統一
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 改行をpタグに変換（すでにHTMLタグがある場合はスキップ）
    if not re.search(r'<(h[1-6]|p|ul|ol|div)\b', text):
        paragraphs = [f"<p>{p.strip()}</p>" for p in text.split("\n\n") if p.strip()]
        text = "\n".join(paragraphs)
    return text.strip()


def strip_html(text: str) -> str:
    """HTMLタグを除去してプレーンテキストに変換"""
    return re.sub(r'<[^>]+>', '', text)


def truncate(text: str, max_length: int = 120) -> str:
    """指定文字数で切り詰め（メタディスクリプション用）"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
