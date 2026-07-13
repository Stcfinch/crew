---
name: crew-upgrade
description: 更新 CREW plugins（bug-workflow + feature-workflow）到最新版本並顯示更新摘要。當使用者提到 /crew-upgrade、「更新 CREW」、「升級 CREW plugin」時觸發此 Skill。
---

# crew-upgrade — 更新 CREW Plugins

一次更新 bug-workflow 和 feature-workflow 兩個 plugin，顯示版本變更和新功能摘要。

---

## 使用方式

```
/crew-upgrade              # 檢查並更新所有 CREW plugins
/crew-upgrade --check      # 只檢查版本，不更新
/crew-upgrade --changelog   # 只顯示 CHANGELOG
```

---

## 流程

### 1. 取得目前安裝版本

從 `installed_plugins.json` 讀取目前安裝的版本：

```bash
INSTALLED_FILE="$HOME/.claude/plugins/installed_plugins.json"
if [ ! -f "$INSTALLED_FILE" ]; then
  INSTALLED_FILE="$HOME/.claude-company/plugins/installed_plugins.json"
fi

if [ -f "$INSTALLED_FILE" ]; then
  echo "=== 目前安裝版本 ==="
  grep -A 5 '"bug-workflow@company-marketplace"' "$INSTALLED_FILE" | grep '"version"' | head -1
  grep -A 5 '"feature-workflow@company-marketplace"' "$INSTALLED_FILE" | grep '"version"' | head -1
else
  echo "找不到 installed_plugins.json"
fi
```

記錄：
- `BW_OLD_VER`：bug-workflow 目前版本
- `FW_OLD_VER`：feature-workflow 目前版本

### 2. 取得最新可用版本

從 marketplace 原始碼讀取最新版本：

```bash
MARKETPLACE_DIR="$HOME/.claude/plugins/marketplaces/company-marketplace"
if [ ! -d "$MARKETPLACE_DIR" ]; then
  MARKETPLACE_DIR="$HOME/.claude-company/plugins/marketplaces/company-marketplace"
fi
if [ ! -d "$MARKETPLACE_DIR" ]; then
  # 兩個候選路徑都不存在。若其中一個是 git repo 只是尚未拉到最新，
  # 才值得 git fetch；純粹「目錄不存在」則 fetch 也無效，直接 early-exit，
  # 不要再往下對死路徑 grep。
  echo "找不到 company-marketplace 原始碼（$HOME/.claude/plugins/marketplaces/company-marketplace 與 ~/.claude-company/... 皆不存在）。"
  echo "請先執行：claude plugin marketplace add company-marketplace"
  exit 1
fi
if [ -d "$MARKETPLACE_DIR/.git" ]; then
  git -C "$MARKETPLACE_DIR" fetch --quiet && git -C "$MARKETPLACE_DIR" pull --quiet
fi

# 從 plugin.json 讀取最新版本
BW_NEW=$(grep '"version"' "$MARKETPLACE_DIR/plugins/bug-workflow/.claude-plugin/plugin.json" | head -1 | sed 's/.*"version".*"\(.*\)".*/\1/')
FW_NEW=$(grep '"version"' "$MARKETPLACE_DIR/plugins/feature-workflow/.claude-plugin/plugin.json" | head -1 | sed 's/.*"version".*"\(.*\)".*/\1/')

echo "bug-workflow：$BW_OLD_VER → $BW_NEW"
echo "feature-workflow：$FW_OLD_VER → $FW_NEW"
```

若上面因找不到 marketplace 原始碼而 `exit 1`：流程在此中止，直接依「邊界情況」段落提示使用者，不進入步驟 3 之後的版本比較與更新。

### 3. 比較版本

用 `sort -V`（version sort）判斷是否可更新，不要用純字串比較（`3.5.0` 與 `3.10.0` 字串比較會誤判 3.10.0 較小）：

```bash
# 若 NEW 版本用 sort -V 排出來比 OLD 大，代表有可更新版本
is_newer() {
  # 用法：is_newer OLD NEW；回傳 0（可更新）或 1（已是最新/相同）
  [ "$1" = "$2" ] && return 1
  [ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | tail -1)" = "$2" ]
}

BW_STATUS="✅ 最新"
if is_newer "$BW_OLD_VER" "$BW_NEW"; then BW_STATUS="⬆️ 可更新"; fi

FW_STATUS="✅ 最新"
if is_newer "$FW_OLD_VER" "$FW_NEW"; then FW_STATUS="⬆️ 可更新"; fi
```

顯示版本比較結果：

```
CREW 版本檢查：

  Plugin           目前版本    最新版本    狀態
  ─────────────    ────────    ────────    ────
  bug-workflow     {BW_OLD}    {BW_NEW}    {✅ 最新 / ⬆️ 可更新}
  feature-workflow {FW_OLD}    {FW_NEW}    {✅ 最新 / ⬆️ 可更新}
```

若 `--check` 模式 → 顯示後結束，不執行更新。

若兩者都是最新 → 顯示「CREW 已是最新版本！」並結束。

### 4. 確認更新

若有可更新的 plugin：

```
以下 plugin 有新版本可用：

  • bug-workflow：{BW_OLD} → {BW_NEW}
  • feature-workflow：{FW_OLD} → {FW_NEW}

確認更新？[Y/n]
```

### 5. 執行更新

依序更新有變更的 plugin：

```bash
# 更新 bug-workflow
claude plugin update bug-workflow@company-marketplace

# 更新 feature-workflow
claude plugin update feature-workflow@company-marketplace
```

若更新失敗 → 顯示錯誤訊息，建議手動重裝：
```
更新失敗，可嘗試手動重裝：
  claude plugin uninstall {plugin}@company-marketplace
  claude plugin install {plugin}@company-marketplace
```

### 6. 讀取 CHANGELOG 並顯示摘要

從 marketplace 目錄讀取 `CHANGELOG.md`：

```bash
CHANGELOG="$MARKETPLACE_DIR/CHANGELOG.md"
if [ -f "$CHANGELOG" ]; then
  echo "CHANGELOG_FOUND=true"
else
  echo "CHANGELOG_FOUND=false"
fi
```

使用 Read tool 讀取 CHANGELOG.md，找出本次更新涉及的版本區塊（從舊版本到新版本之間的所有條目），AI 摘要為 5-7 個重點。

顯示格式（仿 gstack）：

```
CREW 更新完成！

  bug-workflow     {BW_OLD} → {BW_NEW}
  feature-workflow {FW_OLD} → {FW_NEW}

更新重點：

- {重點 1：最重要的新功能}
- {重點 2}
- {重點 3}
- {重點 4}
- {重點 5}

⚠️  請重啟 Claude Code 使新版生效。
```

若 `--changelog` 模式 → 直接讀取並顯示完整 CHANGELOG，不執行更新。

### 7. 重啟提醒

```
⚠️  更新完成，請重啟 Claude Code 使新版生效。

方式：
  • 關閉當前 Claude Code 視窗，重新開啟
  • 或在終端執行：claude（重新啟動 session）
```

---

## 何時不用

- 更新其他 plugin（如 playwright）→ 該 plugin 管道 / claude plugin 指令
- 更新 gstack → 個人 gstack-upgrade
- CREW 首次設定 → /crew-init
- CREW 環境健診 → /crew-doctor

---

## Gotchas

- **marketplace 原始碼路徑**：company-marketplace 的原始碼在 `~/.claude/plugins/marketplaces/company-marketplace/`（若不存在則 fallback 到 `~/.claude-company/plugins/marketplaces/company-marketplace/`）。已安裝版本紀錄在 `~/.claude/plugins/installed_plugins.json`（根層，非 cache/ 子目錄），版本比較要讀這個檔案，不是原始碼。
- **`claude plugin update` 需要網路**：若 marketplace 是 GitHub repo，更新時需要 git fetch。離線環境會失敗。
- **更新後 skill 不會立即生效**：Claude Code 在 session 啟動時載入 skill，更新後必須重啟才能使用新版本。這是 Claude Code 的限制，不是 CREW 的問題。
- **版本比較用 `sort -V`，不是純字串比較**：純字串排序會誤判（例："3.10.0" 字串上小於 "3.9.0"）。步驟 3 已用 `sort -V` 的 `is_newer` 函式處理。若版本號格式不一致（如 `3.5` vs `3.5.0`），仍可能判斷錯誤，統一使用三段式版本號可避免。
- **雞生蛋問題**：crew-upgrade 本身在 bug-workflow 裡。如果 bug-workflow 的更新改了 crew-upgrade 的邏輯，當前 session 用的仍是舊版。這不影響功能，因為實際更新是 `claude plugin update` 執行的。

---

## 邊界情況

- **只安裝了 bug-workflow 沒有 feature-workflow**：只更新 bug-workflow，跳過 feature-workflow
- **marketplace 原始碼不存在**：提示先執行 `claude plugin marketplace add`
- **installed_plugins.json 找不到**：提示重裝 plugin
- **更新後版本沒變**：可能 marketplace 尚未推送新版，顯示「已是最新」
- **網路錯誤**：顯示錯誤，建議檢查網路連線或手動更新
- **CHANGELOG.md 不存在**：跳過摘要顯示，只顯示版本號變化
