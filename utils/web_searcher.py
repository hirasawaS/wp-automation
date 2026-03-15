"""
Web検索で最新の店舗・求人情報を取得するユーティリティ
"""
import os
import logging
import anthropic

logger = logging.getLogger(__name__)


def search_shop_info(topic: str) -> str:
    """
    トピックに関連する最新の夜職求人情報をWeb検索で収集して返す。
    Anthropic web_search ツールを使用。
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    prompt = f"""「{topic}」に関連するキャバクラ・ガールズバーの最新情報を検索してください。
時給相場・店舗名・待遇条件・移籍のポイントを箇条書きでまとめてください。
求人サイトやXのポストより、情報を取得してください。以下のサイトは鮮度が高いです。
- https://lounge-tapioca.com/
- https://www.lounge-baito.com/"""

    logger.info(f"[web_search] トピック「{topic}」の求人情報を検索中...")

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )

    result_text = ""
    for block in message.content:
        if hasattr(block, "text"):
            result_text += block.text

    logger.info("[web_search] 検索完了")
    return result_text
