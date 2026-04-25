# Bug Workflow 深層優化

- **type**: feature
- **name**: bug-deep-optimization
- **status**: 規格設計
- **branch**: feat/bug-deep-optimization
- **created**: 2026-04-24
- **slug**: bug-optimization

## 需求描述

參考 [gstack investigate](~/.claude/skills/gstack/investigate/SKILL.md) 的調查方法論和 [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) 的除錯工程紀律，對 CREW bug-workflow plugin 進行深層優化。

核心理念：**把 bug-workflow 從「記錄器」升級為「偵探夥伴」**。

1. **調查方法論**：新增 bug-investigate Skill，假說驅動、AI 協助定位根因
2. **修復紀律**：新增 bug-fix Skill，鐵律檢查 + 迴歸測試 + gstack 驗證
3. **結案強化**：bug-close 加入退出驗證門檻 + 學習捕捉
4. **起點優化**：bug-start 自動收集初始證據
5. **紀律護欄**：反合理化表 + 三層邊界（bug-workflow 自管理）

## 不包含

- bug-setup / project-add 的修改（已經成熟）
- Notion 資料庫 schema 變更（使用現有欄位）
- feature-workflow 的修改（見 `.spec/crew-optimization/`）
- 跨 plugin 的 references 共享機制（待後續版本）
