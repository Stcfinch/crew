# 截圖穩定化策略

從 SmartRobotE2ETest 的 global-hooks.js 萃取的成熟測試策略，確保每次截圖結果可重現。

---

## 截圖前置步驟（每次截圖前強制執行）

無論使用 MCP 模式或 Bash 模式，截圖前必須依序執行以下 6 步驟：

| Step | 目的 | 操作 |
|------|------|------|
| 1 | 關閉 modal/dropdown/tooltip | `document.querySelectorAll('.modal.show, .swal2-container').forEach(el => el.remove())` 或按 ESC ×2（間隔 300ms） |
| 2 | 關閉測試面板 | 若 `#testPanel` 可見，點擊 toggle 關閉 |
| 3 | 回到頁面頂部 | `window.scrollTo(0, 0)` |
| 4 | 等待網路閒置 | `waitForLoadState('networkidle', timeout: 3000).catch(() => {})` — 不阻擋 |
| 5 | 等動畫結束 | `waitForTimeout(1500)` |
| 6 | 截圖 | `take fullPage screenshot` |

> **重點**：Step 4 的 networkidle 超時後不拋錯，避免長輪詢 API 阻擋截圖流程。

---

## 失敗重試策略

截圖可能因頁面狀態不穩定而失敗，採用漸進式重試：

| 重試次數 | 等待時間 | 說明 |
|---------|---------|------|
| 第 1 次 | 1500ms | 標準等待 |
| 第 2 次 | 2500ms | 額外多等 1s |
| 第 3 次 | 3500ms | 最後一次嘗試 |

每次重試後檢查：
- 截圖檔案是否存在
- 檔案 size > 0

3 次仍失敗 → 標記「(截圖不可用: {原因})」繼續流程，**不阻擋驗證**。

---

## MCP 模式實作

使用 Playwright MCP 工具時的對應呼叫：

```
# Step 1: 關閉浮層
evaluate_script({ expression: "document.querySelectorAll('.modal.show, .swal2-container').forEach(el => el.remove())" })

# Step 2: 關閉測試面板
evaluate_script({ expression: "const p = document.querySelector('#testPanel'); if (p && p.offsetParent !== null) { document.querySelector('#testPanelToggle')?.click() }" })

# Step 3: 回到頂部
evaluate_script({ expression: "window.scrollTo(0, 0)" })

# Step 4: 等待網路閒置（不阻擋）
browser_wait_for({ state: "networkidle", timeout: 3000 })

# Step 5: 等動畫（由 Step 4 的 timeout 隱含覆蓋，不足時補 waitForTimeout）

# Step 6: 截圖
browser_take_screenshot({ fullPage: true, path: "screenshots/{filename}.png" })
```

---

## Bash 模式實作

使用 `$CDP` 命令列工具時的對應呼叫：

```bash
# Step 1-3: 合併為單一 eval
$CDP eval {target} "document.querySelectorAll('.modal.show, .swal2-container').forEach(el => el.remove()); \
  (function(){ var p=document.querySelector('#testPanel'); if(p&&p.offsetParent!==null) document.querySelector('#testPanelToggle')?.click(); })(); \
  window.scrollTo(0,0)"

# Step 5: 等待
sleep 1.5

# Step 6: 截圖
$CDP shot {target} --output screenshots/{filename}.png
```

---

## 特殊頁面處理

| 頁面類型 | 調整策略 |
|---------|---------|
| 長表格頁面 | Step 3 改為 `scrollTo(tableElement.offsetLeft, tableElement.offsetTop)`，Step 6 不用 fullPage |
| iframe 內容 | 先切換到 iframe context（`frame.locator(...)` 或 `$CDP eval --frame ...`）再執行 Step 1-6 |
| 下載觸發頁面 | 等 download event 完成後再執行截圖步驟，避免瀏覽器 dialog 遮擋畫面 |
| SPA 路由切換 | Step 4 的 networkidle 尤其重要，確保新頁面資料載入完成 |
