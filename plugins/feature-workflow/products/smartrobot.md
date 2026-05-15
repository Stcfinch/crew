---
name: SmartRobot
stack: spring-boot-jpa
i18n_locales: [zh-TW, zh-CN, en-US, ja-JP]
login_types: [subadmin, admin]
---

# SmartRobot 產品知識庫

> 此文件為 plan-verify 的產品操作知識，讓驗證更精準。從 SmartRobotE2ETest 萃取。

## 頁面導航地圖

| 功能 | URL 路徑 | 登入方式 | 選單路徑 |
|------|----------|---------|----------|
| Dashboard | /dashboard | subadmin | Dashboard |
| 一般問答 | /qa/list | subadmin | 我的機器人 → 一般問答 |
| 同義詞 | /synonym/list | subadmin | 我的機器人 → 同義詞 |
| 意圖 | /intent/list | subadmin | 我的機器人 → 意圖 |
| 推播統計 | /push/stat | subadmin | 推播 → 統計 |
| 推播管理 | /push/list | subadmin | 推播 → 管理 |
| 短網址 | /shorturl/list | subadmin | 推播 → 短網址 |
| 使用者管理 | /user/list | subadmin | 使用者管理 |
| 標籤管理 | /tag/list | subadmin | 使用者管理 → 標籤 |
| 對話紀錄 | /chatlog/list | subadmin | 數據分析 → 對話紀錄 |
| API Log | /apilog/list | subadmin | 數據分析 → API Log |
| 檔案管理 | /file/list | subadmin | 我的機器人 → 檔案管理 |
| 貼圖管理 | /sticker/list | subadmin | 素材庫 → 貼圖 |
| 影片管理 | /video/list | subadmin | 素材庫 → 影片 |
| 語音管理 | /audio/list | subadmin | 素材庫 → 語音 |
| 角色管理 | /role/list | admin | 系統管理 → 角色 |
| 群組管理 | /group/list | admin | 系統管理 → 群組 |
| 帳號管理 | /account/list | admin | 系統管理 → 帳號 |
| 排程管理 | /schedule/list | admin | 系統管理 → 排程 |
| 廣播管理 | /broadcast/list | admin | 系統管理 → 廣播 |
| 語意搜尋 | /semantic/search | subadmin | 我的機器人 → 語意搜尋 |

## 常用 Selector

| 元素 | Selector | 備註 |
|------|----------|------|
| 搜尋框 | `#searchKeyword` | 全站通用 |
| 送出表單 | `#submitForm` | 全站通用 |
| 匯出按鈕 | `a.btn.btnBlue.btnExport` | class-based |
| 匯入按鈕 | `a.btn.btnBlue.btnImport` | class-based |
| 新增按鈕 | `[title="新增"]` 或 getText('add') | 需 i18n |
| 編輯按鈕 | `[title="編輯"]` 或 getText('edit') | 需 i18n |
| 刪除按鈕 | `[title="刪除"]` 或 getText('delete') | 需 i18n |
| 分頁下一頁 | `.pagination .next a` | 全站通用 |
| 分頁上一頁 | `.pagination .prev a` | 全站通用 |
| 刪除確認（SweetAlert2） | `.swal2-confirm` | 全站通用 |
| 刪除取消（SweetAlert2） | `.swal2-cancel` | 全站通用 |
| 主表格 | `table.dataTable` 或 `.table-responsive table` | 列表頁 |
| Sidebar toggle | `.sidebar-toggle` | 收合側邊欄 |
| 測試面板 toggle | `#testPanel` 或 `.test-panel-toggle` | 測試介面 |

## i18n 關鍵字對照（高頻操作用）

| Key | zh-TW | en-US | zh-CN | ja-JP |
|-----|-------|-------|-------|-------|
| myRobot | 我的機器人 | My Robot | 我的机器人 | マイロボット |
| generalQA | 一般問答 | General QA | 一般问答 | 一般Q&A |
| add | 新增 | Add | 新增 | 追加 |
| edit | 編輯 | Edit | 编辑 | 編集 |
| delete | 刪除 | Delete | 删除 | 削除 |
| save | 儲存 | Save | 保存 | 保存 |
| search | 搜尋 | Search | 搜索 | 検索 |
| confirm | 確認 | Confirm | 确认 | 確認 |
| cancel | 取消 | Cancel | 取消 | キャンセル |
| export | 匯出 | Export | 导出 | エクスポート |
| import | 匯入 | Import | 导入 | インポート |
| dashboard | Dashboard | Dashboard | 仪表板 | ダッシュボード |
| chatLog | 對話紀錄 | Chat Log | 对话记录 | チャットログ |
| dataAnalysis | 數據分析 | Data Analysis | 数据分析 | データ分析 |
| userManagement | 使用者管理 | User Management | 用户管理 | ユーザー管理 |
| tagManagement | 標籤管理 | Tag Management | 标签管理 | タグ管理 |
| pushNotification | 推播 | Push | 推送 | プッシュ |
| statistics | 統計 | Statistics | 统计 | 統計 |
| systemAdmin | 系統管理 | System Admin | 系统管理 | システム管理 |
| basicInfo | 基本資料 | Basic Info | 基本信息 | 基本情報 |
| answer | 回答 | Answer | 回答 | 回答 |
| testCase | 例句 | Test Case | 例句 | テストケース |
| testInterface | 測試介面 | Test Interface | 测试界面 | テストインターフェース |
| searchByQuestion | 依問題搜尋 | Search by Question | 按问题搜索 | 質問で検索 |
| refresh | 重新整理 | Refresh | 刷新 | 更新 |
| back | 返回 | Back | 返回 | 戻る |
| submit | 送出 | Submit | 提交 | 送信 |
| close | 關閉 | Close | 关闭 | 閉じる |
| selectAll | 全選 | Select All | 全选 | 全選択 |
| previousPage | 上一頁 | Previous | 上一页 | 前のページ |
| nextPage | 下一頁 | Next | 下一页 | 次のページ |
| assetLibrary | 素材庫 | Asset Library | 素材库 | 素材ライブラリ |
| sticker | 貼圖 | Sticker | 贴图 | スタンプ |
| semanticSearch | 語意搜尋 | Semantic Search | 语义搜索 | セマンティック検索 |
| fileManagement | 檔案管理 | File Management | 文件管理 | ファイル管理 |

## 特殊操作 Recipe

### CKEditor 富文字編輯器

回答欄位使用 CKEditor，不能直接 fill，必須用 JS API：

```javascript
// MCP 模式
evaluate_script({
  expression: `
    (() => {
      for (const name in window.CKEDITOR.instances) {
        if (name.toLowerCase().includes('answer')) {
          window.CKEDITOR.instances[name].setData('<p>{content}</p>');
          window.CKEDITOR.instances[name].updateElement();
          return name;
        }
      }
      return null;
    })()
  `
})
```

Fallback：若 CKEditor 未載入，改用 iframe 操作：
```
定位 iframe[title*="RTF 編輯器"] → contentFrame → body → click + fill
```

### SweetAlert2 確認框

刪除等危險操作使用 SweetAlert2，確認流程：
1. 點擊刪除按鈕 → SweetAlert2 彈窗出現
2. 等待 `.swal2-confirm` 可見
3. 點擊 `.swal2-confirm` 確認

### 表單提交

部分頁面使用 AJAX 提交（非 form action submit）：
- 儲存後不會有頁面跳轉
- 需等 `networkidle`（2-3 秒）
- 檢查是否有 success toast（`.toast-success` 或 SweetAlert2 success）

### 日期選擇器（Flatpickr）

部分頁面的日期欄位使用 Flatpickr：
1. 點擊日期 input
2. 等待 `.flatpickr-calendar.open` 出現
3. 選擇日期或直接 fill input

### contenteditable 同步

某些欄位使用 contenteditable + hidden input：
```javascript
evaluate_script({
  expression: `
    const input = document.querySelector('#form input[name="{fieldName}"]');
    if (input) input.value = '{value}';
  `
})
```

### 環境差異處理

| 項目 | Profile A (SE) | Profile B (Staging) | Profile C (開發) |
|------|---------------|--------------------|-----------------| 
| QA 審核欄位 | 有 | 無 | 無 |
| 問答語系欄位 | 有 | 有 | 視設定 |
| 多語系切換 | 有 | 有 | 有 |

驗證時先 `count() > 0` 檢查再操作，避免 timeout。

## API 回傳格式（Spring Boot JPA）

### 列表查詢（Pageable）

```json
{
  "content": [...],
  "totalElements": 100,
  "totalPages": 10,
  "size": 10,
  "number": 0
}
```

驗證分頁時檢查：
- `totalElements > 0`（有資料）
- `content.length == size`（非最後一頁時）
- `number` 正確遞增（0-based）
- `totalPages == Math.ceil(totalElements / size)`

### 儲存/更新

```json
{ "code": "0000", "message": "success", "data": {...} }
```

驗證：`code == "0000"`

### 刪除

```json
{ "code": "0000", "message": "success" }
```

### 錯誤

```json
{ "code": "9999", "message": "錯誤訊息" }
```
