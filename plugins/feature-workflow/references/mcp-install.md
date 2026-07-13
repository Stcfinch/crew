# MCP 安裝指令片段

> 供 plan-setup、plan-verify 等 skill 引用，避免安裝指令散落多處各自維護。

## Playwright MCP（Microsoft 維護，瀏覽器操作／QA 驗收）

```bash
claude mcp add playwright --scope user -- \
  npx @playwright/mcp@latest
```

支援截圖、元素互動、表單填寫、頁面導航。安裝後**重啟 Claude Code**。

## chrome-devtools-mcp（Google 官方維護，console/network 除錯）

```bash
claude mcp add chrome-devtools --scope user -- \
  npx chrome-devtools-mcp@latest --autoConnect
```

提供 console log 串流、network 請求分析、performance trace。可連接已登入的 Chrome session，適合需要 SSO/VPN 的內部系統。安裝後**重啟 Claude Code**。

> 💡 兩者定位不同可同時安裝：Playwright 做 QA 驗收，chrome-devtools 做除錯診斷。
