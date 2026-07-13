# deploy-sql-guide — 設定檔模式表與 E7 deploy.sql 模板

> 供 `plan-build/SKILL.md` 步驟 8b（比對設定檔模式）與 E7（部署 SQL 產出）引用。

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

## E7 詳細邏輯（部署 SQL 產出）

1. 讀取 spec.md 判斷區塊的 `DB_REQUIRED` 值
2. 若為 `false` 或不存在 → 跳過
3. 若為 `true` 或 `insert-only`：
   a. 檢查 `.spec/{slug}/deploy.sql` 是否存在
   b. 若不存在 → 掃描 spec.md、db.md、arch.md 中的 SQL 程式碼區塊（` ```sql `），擷取 INSERT / UPDATE / CREATE / ALTER 語句
   c. 組合成完整的 deploy.sql，格式如下：

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

   d. 寫入 `.spec/{slug}/deploy.sql`
   e. 在 files.md 追加「部署 SQL」區段
