# Notion 資料庫架構

`/bug-setup` 可從零建立所有資料庫（含 Views + Relation），
解決首次使用者沒有資料庫的問題。

---

## ER 圖

```mermaid
erDiagram
    PROJECT["專案資料庫"] {
        title Name
        url GitRepo
        select TechStack
        status Status
    }
    TASK["任務追蹤工具"] {
        title TaskName
        status Status
        multiselect TaskType
        select Priority
        select RootCause
    }
    BUG_KB["Bug 知識庫"] {
        title Name
        multiselect Tags
        select Difficulty
    }
    FEATURE_KB["功能設計庫"] {
        title Name
        multiselect Tags
        select DesignType
    }

    PROJECT ||--o{ TASK : "任務追蹤工具"
    PROJECT ||--o{ BUG_KB : "bug處理方式"
    PROJECT ||--o{ FEATURE_KB : "專案資料庫"
```

---

## 建立順序（解決 Relation 循環依賴）

1. **第一輪**：建立 4 個資料庫（不含 Relation）
2. **第二輪**：補上跨庫 Relation（含雙向 DUAL）

詳細 Schema 見 [plugins/bug-workflow/references/db-templates.md](../plugins/bug-workflow/references/db-templates.md)
（feature-workflow 內含同步副本，CI 自動防漂移）。
