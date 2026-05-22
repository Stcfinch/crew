# Windows 使用者指南

CREW 完整支援 Windows，但需注意以下環境差異。

---

## Claude Code 執行環境（擇一）

| 方式 | 適用情境 | 說明 |
|------|---------|------|
| **Claude Code 桌面版**（推薦） | 一般開發 | 直接安裝，內建終端支援 |
| **VS Code / JetBrains 擴充** | IDE 整合 | 透過 IDE 內建終端執行 |
| **WSL2 + CLI** | 進階使用者 | Linux 環境，所有工具原生支援 |

---

## 必要工具安裝

| 工具 | Windows 安裝方式 |
|------|-----------------|
| Node.js | [nodejs.org](https://nodejs.org/) 下載 LTS 版，安裝時勾選 **Add to PATH** |
| Git | [git-scm.com](https://git-scm.com/download/win) 下載，或 `winget install Git.Git` |
| python3 | [Microsoft Store](https://apps.microsoft.com/detail/9NRWMJP3717K) 安裝，或 `winget install Python.Python.3.12` |
| curl | Windows 10+ 內建，無需安裝 |

---

## 常見問題

- **`npx` 找不到**：Node.js 安裝後需**重啟終端**（或重啟 Claude Code），PATH 才會生效
- **`grep` / `find` 不可用**：Windows 原生 CMD 沒有這些指令。解法：
  - 使用 Claude Code 桌面版（自帶 shell 環境）
  - 或安裝 [Git for Windows](https://git-scm.com/download/win)（附帶 Git Bash，含 grep/find）
  - 或使用 WSL2
- **Chrome DevTools MCP 連線失敗**：確認 Chrome 啟動時有加 `--remote-debugging-port=9222` 參數
- **路徑分隔符**：CREW 使用 `/` 路徑（Unix 風格），Claude Code 會自動處理轉換，一般不需手動調整

> `/bug-setup` 和 `/plan-setup` 會自動偵測作業系統，在安裝引導中顯示對應的指令。
