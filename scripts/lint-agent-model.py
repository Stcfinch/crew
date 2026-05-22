#!/usr/bin/env python3
"""Lint Agent model 參數使用方式。

來自 plan-common.md 的已知 gotcha：
  「prompt 中寫『使用 Opus 模型』只是自然語言指示，不保證生效。
   必須在 Agent tool 的 `model` 參數實際設定 `"opus"`。」

本 lint 對所有 SKILL.md 找出「Agent 呼叫描述」位置，並檢查附近
是否有結構化 model 標示，避免下個維護者忘了真正設 model 參數。

判定規則：
  - 出現「啟動 subagent」「啟動 Agent Teams」「使用 Agent tool」「Subagent 模式」
    這類 Agent 呼叫描述
  - 同位置前後 250 字元內必須有 `model: opus/sonnet/haiku` 或 `（model: ...）`
  - 否則列為錯誤

本 lint 預設為 **advisory**（return 0，列出但不阻擋）。
加 `--strict` 後違規會 return 1，可用於 CI 嚴格模式。

退出碼：
  0 = 通過，或 advisory 模式（即使有違規）
  1 = --strict 模式下有違規
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL_GLOB = "plugins/*/skills/*/SKILL.md"
WINDOW = 250

AGENT_CALL_RE = re.compile(
    r"(?:啟動\s*subagent"
    r"|啟動\s*Agent\s*Teams"
    r"|使用\s*Agent\s*tool"
    r"|Agent\s*tool\s*啟動"
    r"|Subagent\s*模式)",
    re.IGNORECASE,
)

STRUCTURED_RE = re.compile(
    r"model\s*[:=]\s*[\"']?(opus|sonnet|haiku)",
    re.IGNORECASE,
)


def main() -> int:
    strict = "--strict" in sys.argv
    findings: list[str] = []
    checked_files = 0
    checked_calls = 0

    for path in sorted(REPO.glob(SKILL_GLOB)):
        text = path.read_text(encoding="utf-8")
        checked_files += 1

        for m in AGENT_CALL_RE.finditer(text):
            checked_calls += 1
            start = max(0, m.start() - WINDOW)
            end = min(len(text), m.end() + WINDOW)
            window_text = text[start:end]

            if STRUCTURED_RE.search(window_text):
                continue

            line = text[:m.start()].count("\n") + 1
            rel = path.relative_to(REPO)
            findings.append(
                f"{rel}:{line} 「{m.group(0)}」附近 {WINDOW} 字元內未找到 "
                f"`model: opus/sonnet/haiku` 結構化標示"
            )

    marker = "❌" if strict else "⚠️ "
    for f in findings:
        print(f"{marker} {f}")

    summary = (
        f"\n檢查 {checked_files} 個 SKILL.md、{checked_calls} 個 Agent 呼叫，"
        f"{len(findings)} 個{'違規' if strict else '建議檢查項'}"
    )

    if findings:
        if strict:
            print(summary)
            return 1
        print(summary)
        print("（advisory 模式：不阻擋 CI；改 SKILL.md 加 `model: opus/sonnet/haiku` 標示後可清除）")
        return 0

    print(f"✅ 檢查 {checked_files} 個 SKILL.md、{checked_calls} 個 Agent 呼叫，全部附帶 model 參數")
    return 0


if __name__ == "__main__":
    sys.exit(main())
