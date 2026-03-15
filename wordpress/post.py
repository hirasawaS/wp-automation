"""
記事投稿処理
"""
import logging
from datetime import date
from config.wordpress import CATEGORY_IDS
from config.settings import DEFAULT_POST_STATUS, DAILY_LIMITS
from .client import WPClient
from utils.post_counter import get_today_count, increment_count
from utils.image_fetcher import fetch_pexels_image

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

    # タグのID解決
    tag_ids = [client.find_or_create_tag(t) for t in article.get("tags", [])]

    # アイキャッチ画像
    topic = article.get("topic", article.get("title", ""))
    image_result = fetch_pexels_image()
    featured_media_id = client.upload_media(*image_result) if image_result else None

    payload = {
        "title": article["title"],
        "content": article["content"],
        "excerpt": article.get("excerpt", ""),
        "status": status or DEFAULT_POST_STATUS,
        "categories": [CATEGORY_IDS[category]],
        "tags": tag_ids,
        "meta": {"description": article.get("meta_description", "")},
    }
    if featured_media_id:
        payload["featured_media"] = featured_media_id

    result = client.create_post(payload)
    increment_count(category)
    logger.info(f"[{category}] 投稿完了: {article['title']} (ID: {result['id']})")
    return result
