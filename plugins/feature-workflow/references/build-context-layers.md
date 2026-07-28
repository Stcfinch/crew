# Delegate 脈絡分層策略

## Layer 0：共用核心脈絡（所有 Teammate 都收到）

Leader 從 CLAUDE.md、技術棧定義與 `.spec/{slug}/state.json`（取 `name` 與 `git.branch`；**只讀，寫入一律走 `crew-state.py`**）擷取，格式化為 5 行以內的摘要：

```
專案技術棧：{技術棧 ID}（{framework} + {orm} + {db}）
命名慣例：package prefix = {prefix}，欄位 = camelCase，表 = snake_case
scaffold：{scaffold 行為一句話}
禁止事項：{若有，如「禁止 Executors.newFixedThreadPool」}
Git branch：{branch}，任務：{name}
```

Token 預算：~200 tokens

## Layer 1：角色脈絡（按 Teammate 角色分配）

按 Teammate 角色，從 `.spec/{slug}/plan.md` 擷取**該角色需要的章節條目**（不是全文）；
表結構一律指向 `.spec/{slug}/deploy.sql`（唯一 SQL 事實來源），不在 prompt 裡抄一份欄位清單。

| Teammate | 從 plan.md 擷取的章節 | 額外脈絡 |
|----------|----------------------|----------|
| 後端工程師 | 目標與範圍、`[db]`／`[arch]` 決策條目、已知取捨與風險 | `deploy.sql` 相關表；指路節中 service 層的 `@code:` 錨點 |
| API 工程師 | 目標與範圍、`[spec]`／`[arch]` 決策條目 | 指路節中 Controller 層的 `@code:` 錨點 |
| 前端工程師 | 目標與範圍、驗收條件中的畫面／操作項 | 指路節中前端檔案的 `@code:` 錨點 |
| 測試工程師 | 驗收條件（`AC-n` 全列）、已知取捨與風險 | `deploy.sql` 的約束（NOT NULL、UNIQUE） |
| DB 工程師 | `[db]` 決策條目、已知取捨與風險 | `deploy.sql` 全文 |

- **錨點只給、不展開**：`@code:path#symbol` 原樣貼進 prompt，由 Teammate 自己 Read。抄一份進 prompt 等於製造第二個會漂移的副本。
- **plan.md 沒有的東西不要去 plan.md 找**：欄位清單、方法簽章、類別清單本來就不寫在 plan.md —— 去 `deploy.sql` 或錨點指到的程式碼看。

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

Leader 從 `deploy.sql` 與 `plan.md` 的驗收條件／決策紀錄提取跨角色約束，在**相關** Teammate 的 prompt 末尾附上：

| 約束來源 | 傳遞給 | 格式 |
|---------|--------|------|
| `deploy.sql` NOT NULL 欄位 | 後端、API、前端 | 「以下欄位不可為 null：user_name, phone, created_at」 |
| `deploy.sql` UNIQUE 約束 | API、後端 | 「以下欄位有唯一約束：email, id_number」 |
| `deploy.sql` 外鍵關聯 | 後端 | 「orders.user_id → users.id（CASCADE DELETE）」 |
| plan.md 驗收條件（`AC-n`） | 前端、API | 「AC-3 要求 startDate／endDate 必填，前端要先擋」 |
| plan.md `[spec]`／`[arch]` 決策條目 | 後端、API | 「D-6 決議 pageSize 上限 100、預設 20」 |

這一層是**唯一允許把值抄進 prompt** 的例外：約束是不可違反的邊界，Teammate 漏讀會直接寫出錯的程式碼。
抄的是短清單而非整份 DDL；有疑義一律回 `deploy.sql` 對答案。

Token 預算：~100-200 tokens per teammate
