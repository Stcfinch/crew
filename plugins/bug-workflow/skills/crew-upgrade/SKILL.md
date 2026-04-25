---
name: crew-upgrade
description: 更新 CREW plugins（bug-workflow + feature-workflow）到最新版本，顯示更新內容摘要。當使用者提到「crew-upgrade」、「更新 crew」、「update crew」、「升級 crew」、「更新 plugin」時觸發此 Skill。
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
INSTALLED_FILE="$HOME/.claude-company/plugins/installed_plugins.json"
if [ ! -f "$INSTALLED_FILE" ]; then
  INSTALLED_FILE="$HOME/.claude/plugins/installed_plugins.json"
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
MARKETPLACE_DIR="$HOME/.claude-company/plugins/marketplaces/company-marketplace"
if [ ! -d "$MARKETPLACE_DIR" ]; then
  echo "找不到 company-marketplace，嘗試 git fetch..."
fi

# 從 plugin.json 讀取最新版本
BW_NEW=$(grep '"version"' "$MARKETPLACE_DIR/plugins/bug-workflow/.claude-plugin/plugin.json" | head -1 | sed 's/.*"version".*"\(.*\)".*/\1/')
FW_NEW=$(grep '"version"' "$MARKETPLACE_DIR/plugins/feature-workflow/.claude-plugin/plugin.json" | head -1 | sed 's/.*"version".*"\(.*\)".*/\1/')

echo "bug-workflow：$BW_OLD_VER → $BW_NEW"
echo "feature-workflow：$FW_OLD_VER → $FW_NEW"
```

### 3. 比較版本

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

## Gotchas

- **marketplace 原始碼路徑**：company-marketplace 的原始碼在 `~/.claude-company/plugins/marketplaces/company-marketplace/`，但安裝的 plugin cache 在 `~/.claude-company/plugins/cache/company-marketplace/`。版本比較要用 cache 中的 `installed_plugins.json`，不是原始碼。
- **`claude plugin update` 需要網路**：若 marketplace 是 GitHub repo，更新時需要 git fetch。離線環境會失敗。
- **更新後 skill 不會立即生效**：Claude Code 在 session 啟動時載入 skill，更新後必須重啟才能使用新版本。這是 Claude Code 的限制，不是 CREW 的問題。
- **版本比較是字串比較**：`3.5.0` vs `3.4.0` 的比較用字串排序。若版本號格式不一致（如 `3.5` vs `3.5.0`），可能判斷錯誤。統一使用三段式版本號。
- **雞生蛋問題**：crew-upgrade 本身在 bug-workflow 裡。如果 bug-workflow 的更新改了 crew-upgrade 的邏輯，當前 session 用的仍是舊版。這不影響功能，因為實際更新是 `claude plugin update` 執行的。

---

## 邊界情況

- **只安裝了 bug-workflow 沒有 feature-workflow**：只更新 bug-workflow，跳過 feature-workflow
- **marketplace 原始碼不存在**：提示先執行 `claude plugin marketplace add`
- **installed_plugins.json 找不到**：提示重裝 plugin
- **更新後版本沒變**：可能 marketplace 尚未推送新版，顯示「已是最新」
- **網路錯誤**：顯示錯誤，建議檢查網路連線或手動更新
- **CHANGELOG.md 不存在**：跳過摘要顯示，只顯示版本號變化
