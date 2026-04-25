# Delegate 脈絡分層策略

## Layer 0：共用核心脈絡（所有 Teammate 都收到）

Leader 從 CLAUDE.md 和技術棧定義中擷取，格式化為 5 行以內的摘要：

```
專案技術棧：{技術棧 ID}（{framework} + {orm} + {db}）
命名慣例：package prefix = {prefix}，欄位 = camelCase，表 = snake_case
scaffold：{scaffold 行為一句話}
禁止事項：{若有，如「禁止 Executors.newFixedThreadPool」}
Git branch：{branch}，任務：{name}
```

Token 預算：~200 tokens

## Layer 1：角色脈絡（按 Teammate 角色分配）

按 Teammate 角色，從 .spec/ 文件中擷取**該角色需要的段落**（不是全文）：

| Teammate | 從 spec.md 擷取 | 從 db.md 擷取 | 從 arch.md 擷取 |
|----------|----------------|---------------|----------------|
| 後端工程師 | 業務邏輯規則 | 全部表結構 | 類別清單 + 介面定義 |
| API 工程師 | API 端點設計 + 錯誤處理 | — | Controller 方法清單 |
| 前端工程師 | 畫面需求 + 操作流程 | — | — |
| 測試工程師 | 驗收條件 | 約束清單（NOT NULL、UNIQUE） | 介面定義 |
| DB 工程師 | — | 全文 | — |

Token 預算：~500-1000 tokens per teammate

## Layer 2：範本脈絡（Leader 預篩選後嵌入）

**不再只給路徑，Leader 要預篩選並嵌入關鍵片段。**

步驟：
1. 用 Glob 找到同層級的候選範本（如 3 個 Service 檔案）
2. 讀取每個候選，選出**最簡單、最標準的那個**
   - 排除：有特殊 annotation、非標準命名、過長、有大量 TODO
   - 優先：短小、清晰、典型
3. 擷取關鍵片段：
   - class 宣告（含 annotation）
   - 1 個代表性方法
   - import 區塊的前 5 行
4. 附帶學習重點指引

格式範例：

```
## 風格參考（已預篩選）

來源：src/main/java/com/xxx/service/impl/UserServiceImpl.java

```java
package com.xxx.service.impl;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
// ...

@Service
public class UserServiceImpl implements UserService {
    @Autowired
    private UserMapper userMapper;

    @Override
    public ApiResult<UserDTO> findById(Long id) {
        User user = userMapper.selectByPrimaryKey(id);
        if (user == null) {
            return ApiResult.fail("使用者不存在");
        }
        return ApiResult.success(BeanUtils.toDTO(user));
    }
}
```

學習重點：
- Service 分 Interface + Impl
- 注入用 @Autowired field injection
- 回傳用 ApiResult<T> 包裝
- 錯誤用 ApiResult.fail()
- 轉換用 BeanUtils.toDTO()
```

Token 預算：~300-500 tokens per teammate

## Layer 3：交叉引用脈絡（跨角色需知道的約束）

Leader 從設計文件中提取跨角色約束，在**相關** Teammate 的 prompt 末尾附上：

| 約束來源 | 傳遞給 | 格式 |
|---------|--------|------|
| db.md NOT NULL 欄位 | 後端、API、前端 | 「以下欄位不可為 null：user_name, phone, created_at」 |
| db.md UNIQUE 約束 | API、後端 | 「以下欄位有唯一約束：email, id_number」 |
| spec.md API 必填參數 | 前端 | 「以下 API 參數為必填：startDate, endDate, userId」 |
| db.md 外鍵關聯 | 後端 | 「orders.user_id → users.id（CASCADE DELETE）」 |
| spec.md 分頁限制 | 後端、API | 「pageSize 上限 100，預設 20」 |

Token 預算：~100-200 tokens per teammate
