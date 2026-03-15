# wp-automation

WordPress × Claude AI を使った夜職メディア向け自動投稿システム。

SEOキーワード・店舗情報から記事を自動生成し、WordPress REST API で投稿まで行う。

---

## 目次

- [概要](#概要)
- [ディレクトリ構造](#ディレクトリ構造)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
- [自動化（cron設定）](#自動化cron設定)
- [記事タイプと投稿先](#記事タイプと投稿先)
- [カスタマイズ](#カスタマイズ)

---

## 概要

以下4種類の記事を生成・投稿できる。

| 記事タイプ | カテゴリ | 投稿数 | 自動化 |
|-----------|---------|--------|--------|
| 初心者SEO記事 | `blog` | 1日10件 | cron自動 |
| 移籍者向け記事 | `migration` | 1日5件 | cron自動 |
| 店舗紹介記事 | `shop` | 不定期 | 手動 |
| キャンペーン情報 | `information` | 不定期 | 手動 |

**技術スタック**
- Python 3.11+
- Claude API（記事生成）
- WordPress REST API（投稿）

---

## ディレクトリ構造

```
wp-automation/
├── config/
│   ├── settings.py          # 投稿数上限・AIモデル設定
│   └── wordpress.py         # WordPress URL・認証・カテゴリID
│
├── data/
│   ├── keywords/
│   │   ├── blog_seo.txt     # 初心者SEO記事用キーワード（1行1件）
│   │   └── migration.txt    # 移籍記事用キーワード（1行1件）
│   ├── migration/
│   │   └── topics.md        # 移籍ネタ素材
│   ├── line_logs/           # LINE相談ログ置き場（テキスト追加OK）
│   └── x_questions/         # X質問データ置き場
│
├── prompts/
│   ├── blog.md              # 初心者SEO記事プロンプト
│   ├── migration.md         # 移籍者向け記事プロンプト
│   ├── shop.md              # 店舗紹介記事プロンプト
│   └── news.md              # キャンペーン記事プロンプト
│
├── generators/
│   ├── base.py              # 共通基底クラス（AI呼び出し・出力パース）
│   ├── blog_generator.py    # 初心者SEO記事生成
│   ├── migration_generator.py # 移籍者向け記事生成
│   ├── shop_generator.py    # 店舗紹介記事生成
│   └── news_generator.py    # キャンペーン記事生成
│
├── wordpress/
│   ├── client.py            # WordPress REST APIクライアント
│   └── post.py              # 投稿処理・1日上限チェック
│
├── scheduler/
│   ├── daily_blog.py        # 毎日10件 SEO記事自動投稿
│   ├── daily_migration.py   # 毎日5件 移籍記事自動投稿
│   └── cron_setup.sh        # cron登録ガイドスクリプト
│
├── utils/
│   ├── text_formatter.py    # HTML整形・テキスト加工
│   ├── keyword_extractor.py # キーワードファイル読み込み・テキスト抽出
│   ├── random_selector.py   # 未使用キーワードのランダム選択
│   └── post_counter.py      # 1日の投稿数カウント管理
│
├── knowledge/               # 店舗知識ベース（エリア別Markdown）
├── word-press/              # 投稿済みHTMLアーカイブ
├── logs/                    # 実行ログ出力先
├── main.py                  # 手動実行エントリーポイント
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## セットアップ

### 1. リポジトリのクローン・依存インストール

```bash
git clone <repo-url>
cd wp-automation

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を編集して以下を設定：

```env
# WordPress設定
WP_URL=https://your-site.com
WP_USER=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

**WordPress アプリケーションパスワードの取得方法**
1. WordPress管理画面 → ユーザー → プロフィール
2. 「アプリケーションパスワード」欄で新しいパスワードを生成
3. 生成されたパスワード（スペース区切り）をそのまま `WP_APP_PASSWORD` に設定

### 3. WordPress カテゴリIDの設定

`config/wordpress.py` の `CATEGORY_IDS` を実際のWordPress上のカテゴリIDに更新する。

```python
CATEGORY_IDS = {
    "blog": 1,        # ← WordPress管理画面で確認
    "news": 2,
    # "migration": ,
    # "shop": 3,
}
```

カテゴリIDは WordPress管理画面 → 投稿 → カテゴリー → 各カテゴリのURLパラメータ `tag_ID=X` で確認できる。

---

## 使い方

### 手動実行（1件ずつ）

```bash
# 初心者SEO記事を1件生成・投稿
python main.py blog

# 移籍記事を1件生成・投稿
python main.py migration

# 店舗紹介記事（knowledge/のMarkdownを指定）
python main.py shop knowledge/shop/池袋.md

# キャンペーン情報
python main.py news "【期間限定】入店祝い金10万円！〇〇ラウンジが新人募集中"
```

> デフォルトは `status: draft`（下書き）で投稿される。
> `config/settings.py` の `DEFAULT_POST_STATUS = "publish"` に変更すると即公開になる。

### キーワードの追加

`data/keywords/blog_seo.txt` または `data/keywords/migration.txt` に1行1キーワードで追記するだけ。

```
キャバクラ 同伴 マナー
キャバクラ ドレスコード
```

`#` 始まりの行はコメントとしてスキップされる。

---

## 自動化（cron設定）

```bash
bash scheduler/cron_setup.sh
```

スクリプトに表示されるコマンドをそのまま実行すると cron に登録される。

| 時刻 | 処理 |
|------|-----|
| 毎朝 9:00 | SEO記事 10件自動投稿 |
| 毎朝 10:00 | 移籍記事 5件自動投稿 |

ログは `logs/blog.log` / `logs/migration.log` に出力される。

---

## 記事タイプと投稿先

### blog（初心者SEO記事）
- キーワードから自動選択 → Claude に記事生成依頼
- 未使用キーワードを優先（全消化したら自動リセット）
- 1日10件まで自動投稿

### migration（移籍者向け記事）
- `data/keywords/migration.txt` のトピックから生成
- `knowledge/shop/` の店舗データを参考情報として注入可能
- 1日5件まで自動投稿

### shop（店舗紹介）
- `knowledge/shop/` 以下のMarkdownを引数に渡して生成
- 手動実行のみ（上限なし）

### news（キャンペーン情報）
- キャンペーン内容を文字列で渡して生成
- 手動実行のみ（上限なし）

---

## カスタマイズ

### 投稿数の変更

`config/settings.py`:

```python
DAILY_LIMITS = {
    "blog": 20,      # ← ここを変更
    "migration": 20,
}
```

### プロンプトの調整

`prompts/` 以下のMarkdownを直接編集するだけ。コードを変更する必要はない。

### AIモデルの変更

`config/settings.py`:

```python
AI_MODEL = "claude-opus-4-6"   # より高品質
# AI_MODEL = "claude-haiku-4-5-20251001"  # より高速・低コスト
```
