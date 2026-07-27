#!/usr/bin/env bash
# sync-shared-refs.sh — 共用 reference 單一來源同步（C9）
#
# 背景（見 docs/adr/004-shared-ref-duplication.md）：
#   為維持「plugin 可獨立安裝」核心契約，6 個共用 reference 在兩個 plugin
#   各存一份實體副本。ADR 004 選擇「雙份 + CI sha256 防漂移」，唯一負面是
#   「更新時要手動 cp 一次」。本腳本確立 bug-workflow/references/ 為單一
#   權威來源，單向同步到 feature-workflow，把手動 cp 升級為一鍵/可檢查機制。
#
# 為何 bug-workflow 為權威：
#   共用檔中 prerequisites.md、db-templates.md 原生於 bug-workflow，
#   且 bug-workflow 是較基礎的 plugin（crew-init 由其提供）。統一以它為準，
#   feature-workflow 那份一律視為同步產物，開發者只改 bug-workflow 那份。
#
# 用法：
#   ./scripts/sync-shared-refs.sh            # 以 bug-workflow 為準同步到 feature-workflow
#   ./scripts/sync-shared-refs.sh --check    # 只檢查是否一致（CI / push 前用），不修改
#   ./scripts/sync-shared-refs.sh -h | --help

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 共用檔清單（權威 = bug-workflow）。與 scripts/check-shared-refs.py 的清單一致。
SHARED_FILES=(
  prerequisites.md
  db-templates.md
  discipline-preamble.md
  notion-backend.md
  handoff-discipline.md
  model-policy.md
)
SRC_DIR="$REPO_ROOT/plugins/bug-workflow/references"
DST_DIR="$REPO_ROOT/plugins/feature-workflow/references"

usage() {
  cat <<'EOF'
用法：
  sync-shared-refs.sh            # 以 bug-workflow 為權威，同步 6 個共用 reference 到 feature-workflow
  sync-shared-refs.sh --check    # 僅檢查兩份是否一致（不修改；不一致 exit 1，CI / push 前用）
  sync-shared-refs.sh -h | --help

權威來源：plugins/bug-workflow/references/（只改這份，改完跑本腳本同步）
同步目標：plugins/feature-workflow/references/
共用檔：prerequisites.md、db-templates.md、discipline-preamble.md、notion-backend.md、handoff-discipline.md、model-policy.md
EOF
}

CHECK=0
case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --check)   CHECK=1 ;;
  "")        ;;
  *)         echo "❌ 未知參數：$1"; echo; usage; exit 2 ;;
esac

fail=0
changed=0
for f in "${SHARED_FILES[@]}"; do
  src="$SRC_DIR/$f"
  dst="$DST_DIR/$f"
  [ -f "$src" ] || { echo "❌ 權威檔不存在：$src"; exit 1; }
  [ -f "$dst" ] || { echo "❌ 目標檔不存在：$dst"; exit 1; }

  if cmp -s "$src" "$dst"; then
    [ "$CHECK" -eq 1 ] && echo "✅ 一致：$f"
  elif [ "$CHECK" -eq 1 ]; then
    echo "❌ 不一致：${f}（feature-workflow 那份與權威 bug-workflow 不同）"
    fail=1
  else
    cp "$src" "$dst"
    echo "🔄 已同步：$f"
    changed=$((changed + 1))
  fi
done

if [ "$CHECK" -eq 1 ]; then
  if [ "$fail" -eq 1 ]; then
    echo
    echo "修法：只改 plugins/bug-workflow/references/ 那份，再跑 ./scripts/sync-shared-refs.sh 同步。"
    exit 1
  fi
  echo "共用 reference 全部一致。"
  exit 0
fi

if [ "$changed" -eq 0 ]; then
  echo "共用 reference 已一致，無需同步。"
else
  echo "同步完成：$changed 個檔案自 bug-workflow 更新到 feature-workflow。"
  echo "請 git add 這些變更並一起 commit。"
fi
