# ADR-001：為何用 `.spec/` 本地規劃而非直接寫 Notion

- 日期：2026-04-25（CHANGELOG feature-workflow@4.10.0 推導）
- 狀態：已採用

## 背景

CREW 的核心場景是「規劃 → 設計 → 建造 → 驗證 → 結案」全生命週期。
設計文件（spec / db / arch / files / verify）需要可讀、可改、可 commit。

候選載體：
1. **Notion**：好讀、好分享、好搜尋
2. **本地 `.spec/{slug}/`**：好版控、好離線、好給 AI 讀

## 決策

採本地 `.spec/{slug}/` 為主，Notion 為「對外公開、跨團隊」的展示層。
plan-* 流程預設不呼叫 Notion API，只在 `/plan-start` 與 `/plan-close` 時做批次同步。

## 後果

**正面**：
- AI 讀寫 markdown 比讀寫 Notion blocks 簡單一個量級（直接 Read/Write 工具）
- 規劃中可離線（不依賴 Notion API 速率限制）
- 設計文件隨程式碼版控，PR 可同時 review 規劃 + 實作
- Notion API 呼叫次數從「每步幾十次」降為「每任務 3-5 次」（plan-start + plan-close）

**負面**：
- 規劃過程其他人在 Notion 看不到進度（需 plan-sync 中途手動同步）
- `.spec/` 預設不入版控（見 CONTRIBUTING.md「.spec/ 目錄規範」），個人 dogfood 不會同步

**中性**：
- Notion 仍是「正式記錄」場所，commit 進 plan-close 時批次寫入

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
| 完全 Notion-first | API 速率限制嚴重、AI 操作複雜、無法跟程式碼一起 PR review |
| `.git/notes` 或 commit message | 規劃內容太大、不適合 markdown 結構化文件 |
| 中央資料庫（PostgreSQL） | 部署複雜度爆增，每個使用者要自架 |
