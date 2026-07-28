# Leader 委派範例 — Agent Teams 協調模式

以下展示 Leader 在 plan-build 中如何有效分配任務和協調 Teammate，而不自己寫 code。

---

## 好的委派方式

### 啟動階段

```
Leader → 全體：
  「功能名稱：推播標籤查詢。規劃在 .spec/push-tag-query/plan.md，
   決策紀錄有 4 條 [arch] 條目定義分層歸屬。以下是分工：」

Leader → backend-engineer：
  「請先讀 plan.md 的「決策紀錄」（[arch]／[db] 條目）與 deploy.sql。
   參考現有的 PushService.java 和 TagMapper.java 作為風格範本。
   產出 POJO → Mapper → Service 共 6 個檔案。
   完成後告訴我每個 Service method 的簽名，我要拿去補「指路」錨點。」

Leader → api-engineer：
  「等後端工程師完成 Service 層後開始。讀 plan.md 的「驗收條件」
   （AC-1～AC-4）與 [spec] 決策條目，產出 Controller + DTO。
   API 路由前綴用 /ap/pushTagQuery/。」

Leader → frontend-engineer：
  「你可以和後端同時開始。讀 plan.md 的「目標與範圍」與畫面相關的
   AC 條目，參考現有的 push_analysis.jsp 作為風格範本。」

Leader → test-engineer：
  「等後端完成後開始。為 Service 層寫 JUnit 測試，
   至少覆蓋正常查詢、空結果、日期範圍邊界三種 case。」
```

### 中間協調

```
backend-engineer → Leader：
  「完成！Service 有 3 個 method：
   - queryByTag(String tag, Date start, Date end)
   - queryByDateRange(Date start, Date end)
   - getTagList()」

Leader → api-engineer：
  「後端 Service 已完成，簽名如上。請據此設計 DTO 和 Controller。」

Leader → test-engineer：
  「後端完成了，你可以開始。Service 檔案在
   com.xtremeapp.linebc.ap.service.PushTagQueryServiceImpl。」
```

### 收尾確認

```
Leader（所有人完成後）：
  「全員完成。我來做 API 契約交叉比對：
   - Controller 的 @RequestMapping 路徑 ✅ 和 AC-2 描述的端點一致
   - DTO 的欄位名 ✅ 和前端 AJAX 呼叫一致
   - 測試 import 的 Service ✅ package 路徑正確

   沒有不一致。接著把各層落點 append 到 plan.md 的「指路」節：
   `@code:.../PushTagQueryServiceImpl.java#queryByTag` 等，
   並用 crew-state.py 記錄本階段完成。改動檔案清單以 git diff 為準，不另建檔。」
```

---

## 常見的反模式（避免）

### ❌ Leader 自己寫 code

```
Leader：「我先幫大家把 POJO 寫好...」
→ 後端工程師的產出會和 Leader 寫的 POJO 風格不一致
→ 如果 Leader 寫的有誤，Teammate 會基於錯誤的 POJO 產出錯誤的下游程式碼
```

### ❌ 沒給具體的風格範本

```
Leader → backend-engineer：「產出 Service 層」
→ Teammate 不知道要學哪個範本的風格，可能產出和專案不一致的程式碼
```

正確做法：指定 1-2 個具體的現有檔案路徑作為風格參考。

### ❌ 所有 Teammate 同時開始

```
Leader：「大家同時開始吧！」
→ API 工程師不知道 Service method 簽名，會自己猜
→ 測試工程師不知道要測什麼 method
→ 最後 API 契約不一致，需要大量返工
```

正確做法：遵循依賴關係 — DB → 後端 → API/測試，前端可並行。
