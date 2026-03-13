"""
投稿数・スケジュール設定
"""

# 1日あたりの投稿数上限
DAILY_LIMITS = {
    "blog": 10,        # 初心者SEO記事
    "migration": 5,    # 移籍者向け記事
    "shop": 0,         # 手動 or 不定期 (0=制限なし・手動)
    "news": 0,         # キャンペーン・不定期 (0=制限なし・手動)
}

# 投稿ステータス: "publish" | "draft" | "private"
DEFAULT_POST_STATUS = "draft"

# 記事生成に使うAIモデル
AI_MODEL = "claude-sonnet-4-6"

# ランダム選択時のシード（None=毎回ランダム）
RANDOM_SEED = None

# blog記事生成時に参照する外部URL
BLOG_REFERENCE_URLS = [
    "https://lounge-tapioca.com/",
    "https://www.lounge-baito.com/",
]
