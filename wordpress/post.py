"""
記事投稿処理
"""
import logging
from datetime import date
from config.wordpress import CATEGORY_IDS
from config.settings import DEFAULT_POST_STATUS, DAILY_LIMITS
from .client import WPClient
from utils.post_counter import get_today_count, increment_count

logger = logging.getLogger(__name__)


def post_article(article: dict, status: str = None) -> dict | None:
    """
    article: generators が返す dict {"title", "content", "meta_description", "category"}
    Returns: WordPress APIのレスポンス or None（上限超過時）
    """
    category = article["category"]
    limit = DAILY_LIMITS.get(category, 0)

    if limit > 0:
        today_count = get_today_count(category)
        if today_count >= limit:
            logger.warning(f"[{category}] 本日の投稿上限({limit}件)に達しました。スキップします。")
            return None

    client = WPClient()
    payload = {
        "title": article["title"],
        "content": article["content"],
        "status": status or DEFAULT_POST_STATUS,
        "categories": [CATEGORY_IDS[category]],
        "meta": {"description": article.get("meta_description", "")},
    }

    result = client.create_post(payload)
    increment_count(category)
    logger.info(f"[{category}] 投稿完了: {article['title']} (ID: {result['id']})")
    return result
