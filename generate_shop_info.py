"""
店舗情報からWP記事とナレッジエントリーを生成するスクリプト

使い方:
  python generate_shop_info.py                    # prompts/temporary/ 以下を全件処理
  python generate_shop_info.py --shop グランクリュ  # 特定の店舗のみ
  python generate_shop_info.py --post             # WPにも投稿する

入力:  prompts/temporary/{店舗名}/ 以下の全ファイル（テキスト・Markdown）
出力:  posted/shop-info/{店舗名}/wp_post.html
       knowledge/shop/{エリア}.md に追記
"""
import argparse
import os
import re
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TEMPORARY_DIR = Path(__file__).parent / "temporary"
POSTED_DIR = Path(__file__).parent / "posted" / "shop-info"
KNOWLEDGE_DIR = Path(__file__).parent / "knowledge" / "shop"

# エリアキーワード → ナレッジファイルのマッピング
AREA_MAP = {
    "池袋": "池袋.md",
    "渋谷": "渋谷.md",
    "上野": "上野.md",
    "歌舞伎町": "歌舞伎町_新宿.md",
    "新宿": "歌舞伎町_新宿.md",
    "恵比寿": "恵比寿.md",
    "赤坂": "赤坂.md",
    "新橋": "新橋.md",
    "秋葉原": "秋葉原.md",
    "大宮": "その他エリア.md",
    "吉祥寺": "その他エリア.md",
    "中野": "その他エリア.md",
    "神田": "その他エリア.md",
}


def load_shop_data(shop_dir: Path) -> str:
    """店舗ディレクトリ内の全ファイルを結合して返す"""
    texts = []
    for f in sorted(shop_dir.iterdir()):
        if f.is_file() and f.suffix in (".md", ".txt", ".html", "") and not f.name.startswith("."):
            texts.append(f"### {f.name}\n{f.read_text(encoding='utf-8')}")
    return "\n\n".join(texts)


def detect_area_file(shop_data: str, shop_name: str) -> Path:
    """店舗データ・店舗名からエリアのナレッジファイルを特定する"""
    combined = shop_name + "\n" + shop_data
    for keyword, filename in AREA_MAP.items():
        if keyword in combined:
            return KNOWLEDGE_DIR / filename
    return KNOWLEDGE_DIR / "その他エリア.md"


def call_ai(prompt: str) -> str:
    import anthropic
    from config.settings import AI_MODEL
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model=AI_MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def generate_wp_article(shop_data: str) -> str:
    """WP用HTMLを生成して返す"""
    from generators import ShopGenerator
    gen = ShopGenerator()
    result = gen.generate(shop_data=shop_data)
    return result.get("content", ""), result.get("title", ""), result


def generate_knowledge_entry(shop_data: str) -> str:
    """ナレッジDBエントリーを生成して返す"""
    prompt_path = Path(__file__).parent / "prompts" / "shop_knowledge.md"
    prompt = prompt_path.read_text(encoding="utf-8").replace("{shop_data}", shop_data)
    return call_ai(prompt)


def update_index(knowledge_entry: str, area_filename: str):
    """knowledge/shop/index.md の店舗数・一覧を更新する"""
    index_path = KNOWLEDGE_DIR / "index.md"
    content = index_path.read_text(encoding="utf-8")

    # エントリーから店舗名・エリア・業態を抽出
    name_match = re.search(r"^## (.+)", knowledge_entry, re.MULTILINE)
    area_match = re.search(r"\*\*場所\*\*[：:]\s*(.+)", knowledge_entry)
    type_match = re.search(r"\*\*業態\*\*[：:]\s*(.+)", knowledge_entry)
    shop_name = name_match.group(1).strip() if name_match else "不明"
    area = area_match.group(1).strip() if area_match else ""
    shop_type = type_match.group(1).strip() if type_match else ""

    # ファイルテーブルの該当行の店舗数をインクリメント
    def increment_count(m):
        prefix, num, suffix = m.group(1), int(m.group(2)), m.group(3)
        return f"{prefix}{num + 1}{suffix}"

    area_base = area_filename.replace(".md", "")
    content = re.sub(
        rf"(\[{re.escape(area_base)}\.md\][^\n]+?)(\d+)(店舗)",
        increment_count,
        content,
    )

    # 合計店舗数をインクリメント
    content = re.sub(
        r"\*\*合計: (\d+)店舗\*\*",
        lambda m: f"**合計: {int(m.group(1)) + 1}店舗**",
        content,
    )

    # 業態セクションに店舗を追加
    section_map = {
        "キャバクラ": "### キャバクラ",
        "ガールズバー": "### ガールズバー",
        "コンカフェ": "### コンカフェ",
        "朝キャバ": "### 朝キャバ",
    }
    section_header = next((v for k, v in section_map.items() if k in shop_type), None)
    if section_header and section_header in content:
        # セクションの末尾（次の ### の手前）に追記
        insert_line = f"- {shop_name}（{area}）"
        content = re.sub(
            rf"({re.escape(section_header)}\n(?:- .+\n)*)",
            lambda m: m.group(1) + insert_line + "\n",
            content,
        )

    index_path.write_text(content, encoding="utf-8")
    logger.info(f"  index.md 更新: {shop_name}（{shop_type} / {area}）")


def already_posted(shop_name: str) -> bool:
    return (POSTED_DIR / shop_name).exists()


def process_shop(shop_dir: Path, do_post: bool = False) -> bool:
    shop_name = shop_dir.name

    if already_posted(shop_name):
        logger.info(f"スキップ（投稿済み）: {shop_name}")
        return False

    logger.info(f"処理開始: {shop_name}")

    shop_data = load_shop_data(shop_dir)
    if not shop_data.strip():
        logger.warning(f"  情報ファイルが空のためスキップ: {shop_name}")
        return False

    # WP記事生成
    logger.info(f"  WP記事を生成中...")
    html_content, title, article = generate_wp_article(shop_data)

    # posted/shop-info/{店舗名}/wp_post.html に保存
    out_dir = POSTED_DIR / shop_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "wp_post.html"
    out_file.write_text(html_content, encoding="utf-8")
    logger.info(f"  保存: {out_file}")

    # ナレッジエントリー生成・追記
    logger.info(f"  ナレッジエントリーを生成中...")
    knowledge_entry = generate_knowledge_entry(shop_data)
    area_file = detect_area_file(shop_data, shop_name)
    with area_file.open("a", encoding="utf-8") as f:
        f.write(f"\n\n{knowledge_entry.strip()}\n")
    logger.info(f"  追記: {area_file.name}")
    update_index(knowledge_entry, area_file.name)

    # WP投稿（--post 指定時のみ）
    if do_post:
        from wordpress import post_article
        result = post_article(article)
        url = result.get("link", "") if result else ""
        logger.info(f"  WP投稿完了: {url}")

    return True


def main():
    parser = argparse.ArgumentParser(description="店舗情報からWP記事・ナレッジを生成")
    parser.add_argument("--shop", help="特定の店舗名（省略時は全件処理）")
    parser.add_argument("--post", action="store_true", help="WordPressにも投稿する")
    args = parser.parse_args()

    if args.shop:
        shop_dir = TEMPORARY_DIR / args.shop
        if not shop_dir.is_dir():
            print(f"ディレクトリが見つかりません: {shop_dir}")
            return
        shops = [shop_dir]
    else:
        shops = [d for d in sorted(TEMPORARY_DIR.iterdir()) if d.is_dir() and not d.name.startswith(".")]

    if not shops:
        print(f"処理対象の店舗が見つかりません: {TEMPORARY_DIR}")
        return

    success, skipped, failed = 0, 0, 0
    for shop_dir in shops:
        try:
            processed = process_shop(shop_dir, do_post=args.post)
            if processed:
                success += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(f"  エラー: {shop_dir.name} → {e}")
            failed += 1

    print(f"\n完了: {success} 件生成 / {skipped} 件スキップ / {failed} 件失敗")


if __name__ == "__main__":
    main()
