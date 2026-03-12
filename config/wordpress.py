"""
WordPress REST API 設定
"""
import os
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://your-site.com")
WP_USER = os.getenv("WP_USER", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")  # WordPress アプリケーションパスワード

# WordPress カテゴリスラッグ → カテゴリID のマッピング
# 実際のIDはWordPress管理画面で確認してください
CATEGORY_IDS = {
    "blog": 1,        # 初心者SEO記事
    "migration": 2,   # 移籍者向け記事
    "shop": 3,        # 店舗紹介
    "news": 4,        # キャンペーン・新着
}

# REST API エンドポイント
API_BASE = f"{WP_URL}/wp-json/wp/v2"
POSTS_ENDPOINT = f"{API_BASE}/posts"
MEDIA_ENDPOINT = f"{API_BASE}/media"
