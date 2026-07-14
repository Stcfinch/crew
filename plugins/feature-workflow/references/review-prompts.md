# Agent Team Review Prompt 模板

> 此檔案由 plan-review 步驟 5「完整審查（Agent Teams）」按需載入。
> 模板中的 `{slug}` `{檔案清單}` 需替換為實際值。

## 完整審查（Agent Teams）

使用自然語言要求 Claude 建立 Agent Team：

```
建立一個 Agent Team 來做 Code Review，生成 3 個 Reviewer：

【Reviewer 1：邏輯正確性】Logic Reviewer
- 讀取專案 CLAUDE.md 了解架構慣例
- 讀取設計文件：
  * .spec/{slug}/spec.md（技術規格）
  * .spec/{slug}/arch.md（架構設計）
- 若 .spec/{slug}/verify.md 存在：
  * 讀取驗證結果，關注 ❌ FAIL 項目
  * 檢查失敗原因是否對應到程式碼問題
  * 審查報告中引用驗證結果作為佐證
- 讀取本次新增/修改的所有程式碼檔案：
  {檔案清單}
- 檢查：
  * API 參數驗證是否完整
  * 業務邏輯是否符合規格
  * 查詢條件是否正確
  * 例外處理是否恰當
  * 邊界條件是否考慮
  * 回傳格式是否一致
- 標記嚴重程度：🔴 嚴重 / 🟡 建議 / 🟢 良好
- 使用 Opus 模型
- 使用繁體中文

【Reviewer 2：程式碼品質】Quality Reviewer
- 掃描專案中 2-3 個同類型的現有檔案作為風格基準
- 讀取本次新增/修改的所有程式碼檔案：
  {檔案清單}
- 檢查：
  * 程式碼風格、命名規範是否與專案一致
  * package 結構和 import 順序
  * Lombok 使用方式
  * 註解風格和位置
  * Error handling 是否完善
  * 有沒有 edge case 沒處理（空數據、數據不足等）
- 標記：🟡 不一致 / 🟢 一致
- 可使用 Sonnet 模型
- 使用繁體中文

【Reviewer 3：效能審查】Performance Reviewer
- 讀取專案 CLAUDE.md 了解效能相關配置
- 讀取 .spec/{slug}/db.md 了解 DB 設計
- 讀取本次新增/修改的所有程式碼檔案：
  {檔案清單}
- 效能檢查：
  * N+1 查詢
  * 缺少分頁
  * 缺少索引
  * 迴圈內 DB 呼叫
  * 大量資料未串流
  * 潛在的效能問題（大數據量回測）
  * 查詢執行計畫分析（若 DB MCP 可用）
  * 效能指標預估（回應時間、吞吐量）
  * 快取策略建議
  * 連線池配置
- 標記：🔴 效能瓶頸 / 🟡 效能風險 / 🟢 良好
- 使用 Opus 模型
- 使用繁體中文

三位 Reviewer 完成後請互相分享各自的發現，
看看有沒有交叉觀點或遺漏（如邏輯問題可能導致安全風險），
最後由 Lead 彙整產出完整的 Review Report。

請使用 delegate mode，Lead 只負責協調，不要自己寫 code。
所有輸出使用繁體中文。
```
