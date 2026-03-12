"""
手動実行エントリーポイント
使い方:
  python main.py blog                  # SEO記事を1件生成・投稿
  python main.py migration             # 移籍記事を1件生成・投稿
  python main.py shop "店舗データ.md"  # 店舗記事を生成・投稿
  python main.py news "キャンペーン内容" # キャンペーン記事を生成・投稿
"""
import sys
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    article_type = sys.argv[1]

    if article_type == "blog":
        from generators import BlogGenerator
        from wordpress import post_article
        article = BlogGenerator().generate()
        result = post_article(article)

    elif article_type == "migration":
        from generators import MigrationGenerator
        from wordpress import post_article
        article = MigrationGenerator().generate()
        result = post_article(article)

    elif article_type == "shop":
        if len(sys.argv) < 3:
            print("使い方: python main.py shop <店舗データのテキストまたはファイルパス>")
            sys.exit(1)
        from pathlib import Path
        from generators import ShopGenerator
        from wordpress import post_article
        data = sys.argv[2]
        if Path(data).exists():
            data = Path(data).read_text(encoding="utf-8")
        article = ShopGenerator().generate(shop_data=data)
        result = post_article(article)

    elif article_type == "news":
        if len(sys.argv) < 3:
            print("使い方: python main.py news <キャンペーン内容>")
            sys.exit(1)
        from generators import NewsGenerator
        from wordpress import post_article
        article = NewsGenerator().generate(campaign_data=sys.argv[2])
        result = post_article(article)

    else:
        print(f"不明な記事タイプ: {article_type}")
        sys.exit(1)

    if result:
        print(f"投稿完了: {article['title']}")
        print(f"URL: {result.get('link', '')}")


if __name__ == "__main__":
    main()
