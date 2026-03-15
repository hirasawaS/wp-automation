"""
Pexels APIから画像を取得してWPにアップロードするユーティリティ
"""
import logging
import requests
from config.settings import PEXELS_API_KEY

logger = logging.getLogger(__name__)

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"

# migration記事用のデフォルト検索クエリ
DEFAULT_QUERY = "night club lounge bar woman"


def fetch_pexels_image(query: str = DEFAULT_QUERY) -> tuple[bytes, str] | None:
    """Pexelsで画像を検索して (バイナリ, ファイル名) を返す。失敗時はNone。"""
    if not PEXELS_API_KEY:
        logger.warning("PEXELS_API_KEY が未設定のためアイキャッチをスキップします")
        return None

    try:
        res = requests.get(
            PEXELS_SEARCH_URL,
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=10,
        )
        res.raise_for_status()
        photos = res.json().get("photos", [])
        if not photos:
            logger.warning(f"Pexelsで画像が見つかりませんでした: {query}")
            return None

        photo = photos[0]
        img_res = requests.get(photo["src"]["large"], timeout=15)
        img_res.raise_for_status()
        filename = f"pexels-{photo['id']}.jpg"
        logger.info(f"[image] 画像取得完了: {filename}")
        return img_res.content, filename

    except Exception as e:
        logger.warning(f"[image] Pexels取得エラー: {e}")
        return None
