# ADR-002：為何採 Agent Teams leader-delegate 而非單 agent

- 日期：2026-04-25（plan-build 4.10.0 同期）
- 狀態：已採用

## 背景

`/plan-build` 要產出可用程式碼，覆蓋面從 DB migration、POJO、Mapper、Service、Controller、DTO、前端到測試。
單一 AI agent 接到完整任務有兩個明顯缺點：

1. **上下文過載**：所有 reference + spec + db + arch + 現有程式碼學習範本一次塞給 agent，注意力分散
2. **角色串味**：DBA 思維、後端思維、前端思維在同一 prompt 內互相干擾

## 決策

採 **leader-delegate** 模式：

- Leader（plan-build skill 本身）負責：
  - 讀設計文件、判斷團隊組成、分層脈絡準備
  - **不直接寫 code**
  - 透過 Agent Teams / Subagent 工具啟動 N 個 Teammate
- Teammate 各自負責特定角色：
  - db-engineer / backend-engineer / api-engineer / frontend-engineer / test-engineer
  - 每個只接到自己角色的脈絡（Layer 0-3）
  - 角色之間透過「Lead 通報」協調 API 契約

## 後果

**正面**：
- 每個 Teammate 接到的脈絡專注，產出風格一致性高
- 平行執行（Agent Teams 模式），速度比序列快
- 易於擴展：新角色（如 security-engineer）獨立加入即可
- DB MCP 工程師只在需要時加入，避免無用查詢

**負面**：
- 需要 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 環境變數啟用
- 兩個 Teammate 可能誤寫同一檔案（需明確劃分目錄職責）
- Leader 必須抗拒「我直接寫 code 更快」的衝動（已寫進 anti-rationalizations.md）

**中性**：
- Subagent 模式 fallback：1 人團隊時降回單 subagent，邏輯仍走 leader

## 考慮過的替代方案

| 方案 | 為何沒選 |
|------|---------|
| 單一 agent 接所有 | 上下文過載、角色串味、無法平行 |
| 序列 subagent（一個接一個） | 慢、後續 agent 看不到先前產出的「最新檔案狀態」 |
| MapReduce-style fan-out + Leader 整併 | 整併步驟複雜，且 Teammate 之間本就需要協調（API 契約），不如直接讓他們互通 |
