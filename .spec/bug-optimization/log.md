# 開發日誌

### [2026-04-24] 探索階段完成
- 深度研究三個系統：CREW bug-workflow v3.4.0、gstack investigate、agent-skills debugging
- 識別核心問題：bug-workflow 是「記錄器」不是「偵探」
- 確定五個優化方向：調查方法論、修復紀律、結案強化、起點優化、紀律護欄
- 決策：bug-investigate 和 bug-fix 拆分為獨立 Skill
- 決策：學習系統採進階用法（investigate 時自動搜尋歷史）
- 決策：反合理化表由 bug-workflow 自管理（非跨 plugin 共享）

### [2026-04-24] 技術規格書完成
- 產出 spec.md，含 3 Phase × 6 項優化
- Phase 1（P0）：bug-investigate Skill + bug-patterns + 反合理化表 + 三層邊界
- Phase 2（P1）：bug-fix Skill + bug-close 退出驗證 + 學習捕捉
- Phase 3（P2）：bug-start 初始證據 + 學習系統 schema
- 新增 6 個檔案、修改 3 個檔案
- bug-investigate 含五階段流程、3-Strike 升級、知識庫 + 學習搜尋
- bug-fix 含鐵律檢查、迴歸測試、gstack browse UI 驗證
- 學習系統含 JSONL 格式、過時偵測、進階 AI 搜尋
