"""
WordPress REST API クライアント
"""
import requests
from requests.auth import HTTPBasicAuth
from config.wordpress import WP_USER, WP_APP_PASSWORD, POSTS_ENDPOINT


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

    def get_posts(self, category: int = None, per_page: int = 10) -> list:
        """投稿一覧を取得"""
        params = {"per_page": per_page}
        if category:
            params["categories"] = category
        response = self.session.get(POSTS_ENDPOINT, params=params)
        response.raise_for_status()
        return response.json()
