# Architecture Decision Records

關鍵架構決策的紀錄，採 [ADR](https://adr.github.io/) 輕量格式。

| 編號 | 標題 | 狀態 |
|------|------|------|
| [ADR-001](./001-local-spec-vs-notion.md) | 為何用 `.spec/` 本地規劃而非直接寫 Notion | 已採用 |
| [ADR-002](./002-agent-teams-leader-delegate.md) | 為何採 Agent Teams leader-delegate 而非單 agent | 已採用 |
| [ADR-003](./003-playwright-default.md) | 為何 plan-verify 預設 Playwright 而非 chrome-devtools | 已採用 |
| [ADR-004](./004-shared-ref-duplication.md) | 為何兩 plugin 各自帶共用 reference（DRY 退讓給獨立性） | 已採用 |
| [ADR-005](./005-bug-investigate-main-entry.md) | 為何 bug-investigate 取代 bug-start 為主入口 | 已採用 |

## 寫新 ADR 的時機

當以下情況觸發新增 ADR：

- 在兩個合理方案間做選擇，且未來可能會被質疑「為什麼不選另一個」
- 推翻先前已 commit 的設計（舊 ADR 改 status: 已撤回，新 ADR 寫明）
- 為了配合外部限制（如 Notion API 設計、Claude Code skill 機制）做的妥協

不需要 ADR 的情況：
- 純風格決定（命名、格式）
- 顯而易見的選擇（如「用 Git 做版控」）
- 實作細節（屬於 SKILL.md 內的 Gotchas，不是架構決策）

## ADR 格式

每篇 ADR 用以下結構（盡量精簡）：

```markdown
# ADR-NNN：標題

- 日期：YYYY-MM-DD
- 狀態：草案 / 已採用 / 已撤回 / 已取代

## 背景

問題場景、約束、stakeholder。

## 決策

採什麼。

## 後果

正面 / 負面 / 中性影響。

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
```
