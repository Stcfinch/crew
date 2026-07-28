# deploy-sql-guide — 設定檔模式表與 deploy.sql 格式契約

> 供 `plan-build/SKILL.md` 步驟 8b（比對設定檔模式）與 E7（deploy.sql 校驗）引用；
> `deploy.sql` 的**產出**者是 `/plan` 的 db pass，不是 plan-build。

## 8b 設定檔模式清單

將收集到的檔案路徑逐一比對以下模式清單：

| 模式 | 說明 |
|------|------|
| `**/mapper/**/*.xml` | MyBatis Mapper XML |
| `**/web.xml` | Web 應用設定 |
| `**/application.properties` | Spring Boot 設定 |
| `**/application*.yml` | Spring Boot YAML 設定 |
| `**/pom.xml` | Maven 依賴 |
| `**/build.gradle` | Gradle 依賴 |
| `**/Dockerfile` | Docker 映像 |
| `**/docker-compose*.yml` | Docker Compose |
| `**/*nginx*.conf` | Nginx 設定 |
| `**/scheduler/**` | 排程設定 |
| `**/*.cron` | Cron 設定 |
| `**/logback*.xml` | Log 設定 |
| `**/ehcache*.xml` | 快取設定 |

## deploy.sql 唯一性原則

`.spec/{slug}/deploy.sql` 是**唯一 SQL 事實來源**：

- **產出者只有一個** —— `/plan` 的 db pass（`feature-db-designer`，可用 Write 整檔寫）
- **DDL 只存在這一個檔案** —— 🔴 不得複製到 `plan.md`、不得另開 `db.sql`，plan.md 只用 `@sql:deploy.sql#{table}` 錨點指過去
- 🔴 **任何 skill 都不得「掃描文件的 SQL 區塊重新組裝一份」** —— 那正是同一份 DDL 出現三四次、然後各自漂移的來源

## E7 校驗邏輯（plan-build 用，只校驗不產出）

1. 讀 `plan.md` 決策紀錄的 `D-1 [spec] 範圍判斷` 的 `DB_REQUIRED` 值
2. 若為 `false` 或查無 → 跳過（`state.json` 的 `steps.db.status` 應為 `skipped`）
3. 若為 `true` 或 `insert-only` → 逐項校驗 `.spec/{slug}/deploy.sql`：
   - [ ] 檔案存在且非空 —— 不存在則 🔴 BLOCK，要求先跑 `/plan db`，**不要自己生一份**
   - [ ] 有 `-- Step N：{描述}` 分段，且 Step 數與 `state.json` 的 `deploy.steps_total` 一致（不一致用 `crew-state.py set --deploy-total` 更正）
   - [ ] 有「驗證 SQL」與「回滾 SQL」兩個註解區段
   - [ ] plan.md 的 `@sql:deploy.sql#{table}` 錨點都指得到（由 `check-spec-drift.py` 的 D5 檢查）
   - [ ] 本次產出的程式碼引用的表／欄位，`deploy.sql` 裡都有（缺漏 → ⚠️ 列出，請使用者決定補 SQL 或改碼）

## 檔案格式契約

db pass 產出、plan-build 校驗、`/plan-close` 初始化 Notion「🚀 部署狀態」都依賴這個格式
（`-- Step N：` 是切割 Step 的唯一依據）：

```sql
-- ================================================================
-- {功能名稱} — 部署 SQL
-- 執行時機：上線部署時，程式更版後執行
-- 資料庫：{DB 名稱}
-- ================================================================

-- Step 1：{描述}
{SQL}

-- Step 2：{描述}
{SQL}

-- ================================================================
-- 驗證 SQL（執行後確認）
-- ================================================================
{驗證 SQL}

-- ================================================================
-- 回滾 SQL（如需還原）
-- ================================================================
-- {回滾 SQL，預設註解}
```

- **表結構的錨點**：db pass 每產生一張新表，就在 plan.md「指路」節加一行 `- 資料表：\`@sql:deploy.sql#{table_name}\``（供漂移偵測 D5 比對）。
- **部署步驟數登記**：Step 數屬狀態，寫進 `state.json`（`crew-state.py set --deploy-total N --deploy-confirmed 0`），🔴 不再產生任何 checklist 文件。
- **執行回流**：DBA 實際跑完後由 `/plan-deploy-confirm` 更新 `--deploy-confirmed` 與 Notion「🚀 部署狀態」。
