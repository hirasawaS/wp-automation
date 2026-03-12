#!/bin/bash
# cron設定スクリプト
# 実行: bash scheduler/cron_setup.sh

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_DIR="$PROJECT_DIR/logs"

# cronに追加するジョブ定義
CRON_BLOG="0 9 * * * cd $PROJECT_DIR && $PYTHON -m scheduler.daily_blog >> $LOG_DIR/blog.log 2>&1"
CRON_MIGRATION="0 10 * * * cd $PROJECT_DIR && $PYTHON -m scheduler.daily_migration >> $LOG_DIR/migration.log 2>&1"

echo "以下のcronジョブを追加します："
echo "  $CRON_BLOG"
echo "  $CRON_MIGRATION"
echo ""
echo "追加するには以下を実行してください："
echo "  (crontab -l 2>/dev/null; echo \"$CRON_BLOG\"; echo \"$CRON_MIGRATION\") | crontab -"
