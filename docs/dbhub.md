# DB MCP（DBHub）— 進階設定

`/project-add` 偵測到 DB 類型後，可選安裝 [DBHub](https://github.com/bytebase/dbhub)
讓 Claude Code 直接查詢資料庫。

---

## 支援的資料庫

| DB | DSN 格式 |
|----|---------|
| **MSSQL** | `sqlserver://user:pwd@host:1433/database` |
| **MySQL** | `mysql://user:pwd@host:3306/database` |
| **PostgreSQL** | `postgresql://user:pwd@host:5432/database` |
| **MariaDB** | `mysql://user:pwd@host:3306/database` |
| **SQLite** | `sqlite:///path/to/database.db` |
| **Oracle** | `oracle://user:pwd@host:1521/service` |

---

## 安裝方式

```bash
# 專案級安裝（推薦，密碼不跨專案）
claude mcp add dbhub --scope project -- \
  npx @bytebase/dbhub --transport stdio \
  --dsn "sqlserver://user:password@host:1433/database"
```

> ⚠️ 安裝後需**重啟 Claude Code**。
> 密碼存放在 `.claude/settings.local.json`，確保已加入 `.gitignore`。

---

## 進階設定：TOML 設定檔

建立 `dbhub.toml` 精確控制讀寫權限：

```toml
[[sources]]
id = "mydb"
dsn = "sqlserver://${DB_USER}:${DB_PASSWORD}@host:1433/database"

# 唯讀工具（日常查詢，推薦）
[[tools]]
name = "execute_sql"
source = "mydb"
readonly = true          # 只能 SELECT / SHOW / DESCRIBE / EXPLAIN
max_rows = 1000

# 讀寫工具（需要修改資料時用）
[[tools]]
name = "execute_sql_write"
source = "mydb"
readonly = false         # 允許 INSERT / UPDATE / DELETE
```

使用設定檔安裝：

```bash
claude mcp add dbhub --scope project -- \
  npx @bytebase/dbhub --transport stdio --config ./dbhub.toml
```

> 💡 支援環境變數插值（`${DB_USER}`）和 Hot Reload（HTTP 模式下修改 TOML 立即生效）。

---

## 管理指令

```bash
claude mcp list              # 查看已安裝的 MCP
claude mcp remove dbhub      # 移除 DBHub
```
