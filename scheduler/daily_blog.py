"""
初心者SEO記事 定常投稿スクリプト（1日10記事）
実行: python -m scheduler.daily_blog
"""
import logging
from config.settings import DAILY_LIMITS
from generators import BlogGenerator
from wordpress import post_article

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run():
    limit = DAILY_LIMITS["blog"]
    generator = BlogGenerator()
    success = 0

    for i in range(limit):
        try:
            article = generator.generate()
            result = post_article(article)
            if result:
                success += 1
                logger.info(f"[{i+1}/{limit}] 完了: {article['title']}")
            else:
                logger.warning(f"[{i+1}/{limit}] スキップ（上限到達）")
                break
        except Exception as e:
            logger.error(f"[{i+1}/{limit}] エラー: {e}")

    logger.info(f"完了: {success}/{limit} 件投稿")


if __name__ == "__main__":
    run()
