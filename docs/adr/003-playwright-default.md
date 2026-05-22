# ADR-003：為何 plan-verify 預設 Playwright 而非 chrome-devtools

- 日期：2026-04-25（plan-verify 4.11.0）
- 狀態：已採用

## 背景

`/plan-verify` 用瀏覽器自動化驗證驗收條件。兩個可選 MCP：

- **Playwright MCP**（Anthropic 官方）：截圖、元素互動、表單填寫、頁面導航
- **chrome-devtools-mcp**（Google 官方）：連接已登入的 Chrome session、console log 串流、network 請求分析、performance trace

兩者各有強項。

## 決策

預設使用 **Playwright MCP**，chrome-devtools 改為 `--deep` 模式的除錯輔助。

理由：
1. Playwright 是隔離的 headless browser，每次驗證起點明確（無殘留 state）
2. 截圖品質與穩定性高（Anthropic 官方持續優化）
3. chrome-devtools 連線到使用者 Chrome 會被 popup、SSO、其他分頁干擾
4. 「驗收」場景重點是「乾淨 reproduce」，不需要使用者既有登入狀態
5. 「除錯」場景才需要連到使用者已登入的 Chrome，這是 `--deep` 模式

## 後果

**正面**：
- 驗收驗證可重現（不同人跑出同樣截圖）
- 不污染使用者瀏覽器 session
- console/network 除錯仍可用（`--deep` 觸發 chrome-devtools）

**負面**：
- 需要使用者額外設定登入流程（Playwright 不繼承使用者 Chrome 的登入）
- SSO/VPN 內部系統首次設定較麻煩
- 兩個 MCP 都需安裝才能用 `--deep` 模式

**中性**：
- /crew-doctor 同時檢查兩者，告知使用者哪個影響哪個功能

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
| 預設 chrome-devtools | 受使用者瀏覽器 state 干擾、無法 headless |
| 兩者並存無預設 | 使用者要選，增加心智負擔 |
| 自家寫 verify runner（不依賴 MCP） | 重造輪子，且 MCP 生態才剛起飛該擁抱 |
