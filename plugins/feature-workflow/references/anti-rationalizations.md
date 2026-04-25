# 反合理化參考

## 通用（所有 plan-* Skill 適用）

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| G1 | 「先跳過這步，之後再補」 | 之後不會補。每個跳過的步驟都是下游的隱性債務。 |
| G2 | 「使用者趕時間，精簡一下」 | 使用者沒說精簡。精簡 = 品質下降 = 之後花更多時間修。 |
| G3 | 「這太簡單不需要完整流程」 | 簡單的事會變複雜。流程保護的是未來，不是現在。 |

## plan-build 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| B1 | 「arch.md 不存在，我先快速產一個再繼續 build」 | arch.md 是 hard block。自動補產的架構沒有經過使用者審閱，錯誤的類別清單和介面定義會傳遞給所有 Teammate，錯誤被放大 5 倍。 |
| B2 | 「只有 3 個檔案要改，開 Agent Teams 太重了，我自己寫比較快」 | Leader 自己寫 code 會跟 Teammate 產出衝突（寫同一個檔案）。即使只有 3 個檔案，Subagent 模式仍然是正確的選擇。 |
| B3 | 「spec.md 太長了，我只讀 arch.md 就好」 | arch.md 定義「怎麼做」，spec.md 定義「做什麼」。跳過 spec.md 意味著 Teammate 不知道業務規則、驗證邏輯、錯誤處理策略。產出的 Service Impl 會全是空 TODO。 |
| B4 | 「掃描現有範本太慢，我直接根據技術棧定義產生」 | 技術棧定義只有框架和 ORM 類型，沒有 package 結構、import 順序、annotation 風格、命名慣例。跳過範本掃描的產出需要大量手動修正。 |
| B5 | 「Teammate prompt 已經夠長了，不需要再塞技術棧定義」 | 沒有技術棧定義的 Teammate 會用 Spring Boot 的預設風格，對 Spring MVC 4.x 專案會產出完全錯誤的程式碼（annotation 不同、配置方式不同）。 |
| B6 | 「files.md 只是紀錄，跳過不影響功能」 | plan-review 從 files.md 讀取審查範圍。沒有 files.md，Reviewer 要從 git diff 取得，可能包含不相關的檔案，審查品質下降。 |
| B7 | 「DB MCP 查詢太慢，跳過 DB 工程師直接讓後端開始」 | DB 工程師驗證表結構一致性。跳過意味著後端工程師可能根據過期的 db.md 產生 Entity，欄位名/型別與實際 DB 不符。 |
| B8 | 「退出驗證太嚴格，這次先跳過」 | 退出驗證是防止假完成的最後防線。跳過意味著 plan-review 和 plan-verify 要處理本該在 build 階段就擋住的問題。 |

## plan-review 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| R1 | 「程式碼很簡單，用 --quick 就好」 | --quick 只有邏輯審查，沒有品質和效能軸。簡單的程式碼最容易有 N+1 查詢和不一致的風格。 |
| R2 | 「交叉審查沒新發現，跳過合併步驟」 | 合併步驟不只是匯總，還要去重和排優先級。跳過會讓 review.md 充斥重複問題。 |
| R3 | 「verify.md 有 FAIL 項目但那是環境問題，不需要在 review 中提」 | Reviewer 應該判斷 FAIL 是程式碼問題還是環境問題，不是 Leader。把判斷責任留給 Reviewer。 |

## plan-verify 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| V1 | 「API 回傳 200 就算 PASS」 | HTTP 200 只代表沒有伺服器錯誤。用 curl 檢查回應 body 的格式、筆數、欄位完整性。 |
| V2 | 「snapshot 太長了，我只看前幾行」 | 用 `$B snapshot -D` 看 diff 而不是全文。diff 會高亮變化，不需要掃描整個 snapshot。 |
| V3 | 「這條驗收條件需要登入，太複雜了，標 SKIP」 | 用 `$B connect` 連接已登入的 Chrome，或 `$B cookie-import` 匯入 cookie。gstack 支援 CDP 模式，不需要重新登入。 |
| V4 | 「gstack browse 沒裝，改用 curl 手動測就好」 | curl 只能測 API，無法測 UI 互動、表單驗證、回應式。plan-verify 的核心價值是端到端驗證。 |
| V5 | 「Health Score 太低但功能有跑起來，算 PASS 吧」 | Health Score 是客觀指標。低分代表使用者體驗有問題。記錄實際分數，讓使用者決定是否接受。 |

## plan-security 專用

| # | AI 的內心獨白 | 為什麼不行 |
|---|-------------|-----------|
| S1 | 「這只是內部 API，不需要安全掃描」 | 內部 API 被 SSRF 攻擊時跟外部 API 一樣危險。而且「內部」定義會隨時間改變。 |
| S2 | 「這個 ${} 是用在 ORDER BY，不能用 #{}」 | 正確，但需要 allowlist 驗證。不是「不能用 #{}」就代表「可以用 ${}」，還有第三條路。 |
| S3 | 「專案已經有 ESAPI，安全應該 OK」 | ESAPI 存在不代表正確使用。最常見的問題是新程式碼忘記呼叫 ESAPI 方法。 |
| S4 | 「掃描結果太多 false positive，沒什麼用」 | Layer 1 是機械掃描，確實有 false positive。但 Layer 2 和 3 是上下文感知的，不能因為 Layer 1 有雜訊就跳過全部。 |
