"""
一括記事生成スクリプト
使い方:
  python bulk_generate.py --type blog --count 30
  python bulk_generate.py --type migration --count 30
"""
import argparse
import time
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(message)s")

DELAY_SECONDS = 10  # 記事間のウェイト（APIレート制限対策）


def main():
    parser = argparse.ArgumentParser(description="WordPress記事一括生成")
    parser.add_argument("--type", required=True, choices=["blog", "migration"], help="記事タイプ")
    parser.add_argument("--count", type=int, default=30, help="生成件数（デフォルト: 30）")
    args = parser.parse_args()

    if args.type == "blog":
        from generators import BlogGenerator
        generator = BlogGenerator()
    else:
        from generators import MigrationGenerator
        generator = MigrationGenerator()

    from wordpress import post_article

    success, failure = 0, 0
    failed_items = []

    print(f"\n{args.type} 記事を {args.count} 件生成します\n{'─' * 40}")

    for i in range(1, args.count + 1):
        print(f"[{i}/{args.count}] 生成中...", end=" ", flush=True)
        try:
            article = generator.generate()
            result = post_article(article)
            url = result.get("link", "") if result else ""
            print(f"✓ {article['title']}")
            if url:
                print(f"       {url}")
            success += 1
        except Exception as e:
            print(f"✗ エラー: {e}")
            failure += 1
            failed_items.append(f"[{i}] {e}")

        if i < args.count:
            time.sleep(DELAY_SECONDS)

    print(f"\n{'─' * 40}")
    print(f"完了: {success} 件成功 / {failure} 件失敗")
    if failed_items:
        print("\n失敗一覧:")
        for item in failed_items:
            print(f"  {item}")


if __name__ == "__main__":
    main()
