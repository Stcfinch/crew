# i18n 驗證指引

plan-verify 的多語系驗證策略，涵蓋語系偵測、元素定位、報告語言規則。

---

## 支援語系

| 語系 | 代碼 | 優先順序 | 說明 |
|------|------|---------|------|
| 繁體中文 | zh-TW | 1（預設） | 台灣市場主要語系 |
| 簡體中文 | zh-CN | 2 | 中國大陸市場 |
| 英文 | en-US | 3 | 國際版本 |
| 日文 | ja-JP | 4 | 日本市場 |

---

## 語系偵測順序

依以下優先順序判定測試語系，命中即停：

1. **spec.md 明確指定**：驗收條件中有「測試英文版」「在日文環境驗證」等語句 → 使用指定語系
2. **頁面 DOM 偵測**：`evaluate: document.documentElement.lang` → 取得當前頁面語系
3. **產品知識庫預設**：`products/{id}.md` 的 `i18n_locales[0]` → 該產品的預設語系
4. **全域預設**：zh-TW

```
# 偵測範例（MCP 模式）
evaluate_script({ expression: "document.documentElement.lang" })
# 回傳 "en-US" → 測試語系為 en-US
```

---

## 產品模式定位策略

當 `projects/{repo-id}.md` 有 `product_id` 時，啟用產品模式。

### 翻譯文字定位（優先）

載入 `products/{id}.md` 的 i18n 對照表，用翻譯後的文字定位元素：

```
# 範例：產品對照表定義
# 「會員管理」→ en-US: "Member Management" → ja-JP: "会員管理"

# 繁體中文環境
getByRole('link', { name: '會員管理' })

# 英文環境
getByRole('link', { name: 'Member Management' })

# 日文環境
getByRole('link', { name: '会員管理' })
```

### Fallback 定位順序

當翻譯文字定位失敗時，依序嘗試：

| 順序 | 策略 | 範例 | 適用場景 |
|------|------|------|---------|
| 1 | 穩定 selector | `#member-list`, `input[name="email"]` | 有 id 或 name 屬性 |
| 2 | CSS selector | `.nav-item:nth-child(3)` | 結構固定的 UI |
| 3 | URL 導航 | 直接 navigate 到目標頁面 | 無法透過 UI 定位 |

### 截圖與報告

- 截圖：反映**實際測試語系**的畫面
- 報告：永遠使用**繁體中文**撰寫

---

## 通用模式定位策略

當無 `product_id` 時，採用語言無關的定位策略。

### 定位優先順序

| 順序 | 策略 | 範例 | 說明 |
|------|------|------|------|
| 1 | 穩定 selector（語言無關） | `#submit-btn`, `input[name="username"]`, `.login-form` | 不依賴文字，跨語系自然有效 |
| 2 | Snapshot + AI 解讀 | `browser_snapshot()` → 分析 a11y tree | 從可及性樹狀結構辨識元素 |
| 3 | evaluate DOM 查詢 | `document.querySelector('[data-testid="nav"]')` | 使用 data 屬性定位 |
| 4 | 位置/結構定位 | `:nth-child()`, 相對位置 | 最後手段 |

### 設計原則

- **不依賴文字內容**：selector 使用 id、name、data-testid、class
- **跨語系自然有效**：同一套 selector 在任何語系都能找到目標元素
- **避免硬編碼文字**：不使用 `getByText('登入')` 這類依賴語系的定位

---

## 多語系驗收條件處理

### spec.md 語系指定

驗收條件可能指定特定語系進行驗證：

```markdown
# spec.md 範例
## 驗收條件
- AC-1: 在繁體中文版確認導航選單正確顯示
- AC-2: 切換至英文版，確認所有按鈕文字已翻譯
- AC-3: 在日文環境測試表單提交功能
```

### 語系切換操作

當需要在測試中切換語系時：

| 方法 | 操作 | 適用場景 |
|------|------|---------|
| URL 參數 | `navigate({ url: '...?lang=en-US' })` | 支援 query string 切換的產品 |
| Cookie 設定 | `evaluate: document.cookie = 'lang=en-US'` + 重新整理 | Cookie-based 語系管理 |
| UI 操作 | 點擊語系選單 → 選擇目標語系 | 有語系切換 UI 的產品 |
| Header 設定 | `Accept-Language: en-US` | API 層級語系控制 |

### 跨語系驗收流程

1. 記錄初始語系
2. 切換到目標語系
3. 等待頁面重載完成（networkidle）
4. 執行驗收步驟
5. 截圖（反映目標語系畫面）
6. 切換回初始語系（若後續步驟需要）

---

## 報告語言規則

無論測試哪個語系，報告產出一律遵循以下規則：

| 產出物 | 語言 | 說明 |
|--------|------|------|
| verify.md | 繁體中文 | 驗證報告主體，所有描述使用繁體中文 |
| human_steps | 繁體中文 | 操作步驟描述，即使操作的是英文版頁面 |
| 截圖 | 實際測試語系 | 截圖反映真實畫面，不做語系轉換 |
| Word 報告 | 繁體中文 | 文字描述繁體中文，標注「測試語系: {locale}」 |
| Excel 報告 | 繁體中文 | 文字描述繁體中文，標注「測試語系: {locale}」 |

### human_steps 撰寫範例

```markdown
# ✅ 正確：操作描述用繁體中文，畫面內容維持原語系
- 步驟 1: 開啟首頁，確認導航列顯示「Member Management」（英文版）
- 步驟 2: 點擊「Settings」按鈕，進入設定頁面
- 步驟 3: 確認頁面標題為「Account Settings」

# ❌ 錯誤：把畫面文字翻譯成中文
- 步驟 1: 開啟首頁，確認導航列顯示「會員管理」
```

### 報告標注格式

在報告摘要區標注測試語系：

```markdown
## 摘要
- 驗證日期：2024-01-15
- 測試環境：UAT
- 測試語系：en-US（英文）
- 驗測工具：Playwright MCP
```
