"""
WordPress REST API クライアント
"""
import logging
import requests
from requests.auth import HTTPBasicAuth
from config.wordpress import WP_USER, WP_APP_PASSWORD, POSTS_ENDPOINT, MEDIA_ENDPOINT, TAGS_ENDPOINT

logger = logging.getLogger(__name__)


class WPClient:
    def __init__(self):
        self.auth = HTTPBasicAuth(WP_USER, WP_APP_PASSWORD)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({"Content-Type": "application/json"})

    def create_post(self, payload: dict) -> dict:
        """記事を投稿してレスポンスを返す"""
        response = self.session.post(POSTS_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()

    def upload_media(self, image_bytes: bytes, filename: str) -> int:
        """画像をWPメディアライブラリにアップロードしてIDを返す"""
        res = requests.post(
            MEDIA_ENDPOINT,
            auth=self.auth,
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Type": "image/jpeg",
            },
            data=image_bytes,
        )
        res.raise_for_status()
        media_id = res.json()["id"]
        logger.info(f"[media] アップロード完了: {filename} (ID: {media_id})")
        return media_id

    def find_or_create_tag(self, name: str) -> int:
        """タグ名でIDを探す。なければ作成して返す"""
        res = self.session.get(TAGS_ENDPOINT, params={"search": name})
        res.raise_for_status()
        for tag in res.json():
            if tag["name"] == name:
                return tag["id"]
        res = self.session.post(TAGS_ENDPOINT, json={"name": name})
        res.raise_for_status()
        return res.json()["id"]

    def get_posts(self, category: int = None, per_page: int = 10) -> list:
        """投稿一覧を取得"""
        params = {"per_page": per_page}
        if category:
            params["categories"] = category
        response = self.session.get(POSTS_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
