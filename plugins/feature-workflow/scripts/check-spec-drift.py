#!/usr/bin/env python3
"""偵測 .spec/{slug}/plan.md 內的程式碼錨點是否失效（文件漂移）。

CREW v2 的設計靈魂是「文件只寫程式碼裡看不到的東西，『是什麼』一律用錨點指過去」。
代價是產生新的漂移形式：**指標本身會失效**（檔案改名、符號被刪）。本 script 就是接住
這個問題的防線，掛在 /plan-drift、plan-review R0、plan-close 硬關卡與 CI 上。

錨點語法
--------
    @code:<relpath>[#<symbol>]        T1 僅路徑 / T2 路徑+符號（預設）
    @code:<relpath>#<symbol>@sha1:ab12cd   T3 內容指紋（極少數關鍵不變量，僅 WARN）
    @sql:deploy.sql#<table>

行號提示 `(L88)` **刻意放在 token 外面**：它是給人看的提示，本 script 只回報新行號、
絕不 FAIL。符號比對用 word-boundary 字串比對，**不做 AST 解析** —— 要能跨
Java/XML/SQL/YAML，而且 AST 才是誤判來源。

檢查碼
------
    D1  錨點檔案不存在（含 git -M 改名偵測）      FAIL（偵測到改名 → 可自動修，級別仍是 FAIL）
    D2  錨點符號不在檔內                          FAIL
    D3  行號提示位移                              INFO（可自動修）
    D4  T3 內容 hash 不符                         WARN
    D5  @sql: 指向 deploy.sql 沒有的表 → FAIL；表在程式碼查無引用 → WARN
    D6  文件落後程式碼（錨點檔案在 verified_at_commit 之後有變更，plan.md 卻沒動） WARN
    D7  缺 verified_at_commit / 零錨點（過渡期）  WARN，每份文件只報一次

D1 偵測到改名時仍維持 FAIL（不降 INFO）：此刻文件裡寫的路徑真的不存在，plan-close 不該
在指標是死的狀態下蓋章；--fix 一行就修好，摩擦極小。要改判 INFO 只需動 check_code_anchor。

D6 的三個靜默條件（全部是為了避免誤報）：
  1. 變更只有 R100／C100（純改名、內容一字未改）—— 指標問題由 D1 負責，不是文件落後
  2. plan.md 有未提交的修改 —— 使用者正在更新文件中
  3. plan.md 最後一次 commit 不早於動到錨點檔案的那個 commit

退出碼
------
    0 = 乾淨
    1 = 有 FAIL（或 --strict / drift_policy: strict 下出現 WARN）
    2 = 只有 WARN
    3 = 環境問題（非 git 工作區、git 不可用、verified_at_commit 不在歷史、檔案讀不到）
        **3 永遠不等於漂移** —— 這類訊息只說「無法檢查」。

逃生閥
------
  * plan.md frontmatter `drift_policy: strict | normal | off`（off = 整份跳過）
  * 行內 `<!-- drift-ignore: D2 reason=已改用新介面 -->`
    寫在錨點那一行或其上一行；**沒寫 reason 就不生效**（防止無腦全域關閉）。

自動修（--fix）
--------------
只修**機械型**：D1 的改名（git -M 偵測到新路徑）與 D3 的行號位移。
D2/D4/D5/D6 一律不自動修 —— 符號消失可能代表決策變了，該改的是決策紀錄而非指標。

誤報控制：寧可漏報，不可誤報（誤報會導致大家把檢查關掉）。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------- 常數與樣式

LEVEL_ICON = {"FAIL": "❌", "WARN": "⚠️", "INFO": "ℹ️", "ENV": "🚧"}

# 錨點：@code:path[#symbol][@sha1:xxxx] / @sql:path#table
ANCHOR_RE = re.compile(
    r"@(?P<kind>code|sql):"
    r"(?P<path>[^\s`'\"()\[\]<>#]+)"
    r"(?:#(?P<symbol>[^\s`'\"()\[\]<>@]+))?"
    r"(?:@sha1:(?P<sha1>[0-9a-fA-F]{4,40}))?"
)

# 行號提示：緊接在錨點之後（可跨一個收尾 backtick 與空白）的 (L88)
HINT_RE = re.compile(r"\A`?[ \t]*\(L(?P<line>\d+)\)")

# 逃生閥：<!-- drift-ignore: D2 reason=... -->
IGNORE_RE = re.compile(r"<!--\s*drift-ignore:(?P<body>[^>]*?)-->")
REASON_RE = re.compile(r"reason\s*=\s*(?P<reason>\S.*?)\s*\Z")

FRONTMATTER_RE = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|\Z)", re.DOTALL)
FENCE_RE = re.compile(r"^[ \t]*(?:```|~~~).*$", re.MULTILINE)

# git grep 找表名引用時排除的路徑（宣告處與文件不算「程式碼引用」）
SQL_REF_EXCLUDES = [":!.spec", ":!*.sql", ":!*.md"]

JSON_FIELDS = ("code", "level", "spec", "line", "anchor", "detail", "fix", "autofixable")


class EnvProblem(Exception):
    """環境問題：無法檢查，不是漂移。"""


# ---------------------------------------------------------------- git 小工具


def run_git(root: Path, args: list[str], timeout: int = 30) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:  # git 不在 PATH
        raise EnvProblem("找不到 git 指令（不在 PATH）") from exc
    except subprocess.TimeoutExpired as exc:
        raise EnvProblem(f"git 指令逾時：git {' '.join(args)}") from exc


def git_toplevel(root: Path) -> Path:
    if not root.is_dir():
        raise EnvProblem(f"路徑不存在或不是目錄：{root}")
    proc = run_git(root, ["rev-parse", "--show-toplevel"])
    if proc.returncode != 0:
        raise EnvProblem(f"{root} 不在 git 工作區內，無法做改名／落後偵測")
    return Path(proc.stdout.strip())


_RENAME_CACHE: dict[tuple[str, str | None], dict[str, str]] = {}


def rename_map(root: Path, base: str | None) -> dict[str, str]:
    """全樹改名對照表 {舊路徑: 新路徑}。

    不用 `git log -- <舊路徑>`：pathspec 過濾發生在改名偵測之前，只給舊路徑抓不到 R 記錄。
    有 verified_at_commit 就比 base..HEAD；沒有就掃最近 200 個 commit 的改名。
    """
    key = (str(root), base)
    if key in _RENAME_CACHE:
        return _RENAME_CACHE[key]
    if base:
        args = ["diff", "--name-status", "-M", f"{base}..HEAD"]
    else:
        args = ["log", "-M", "--diff-filter=R", "--name-status", "--format=", "-n", "200"]
    mapping: dict[str, str] = {}
    try:
        proc = run_git(root, args)
    except EnvProblem:
        proc = None
    if proc is not None and proc.returncode == 0:
        for line in proc.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].startswith("R"):
                mapping.setdefault(parts[1], parts[2])
    _RENAME_CACHE[key] = mapping
    return mapping


def detect_rename(root: Path, relpath: str, base: str | None = None) -> str | None:
    """找出錨點檔案改名後的新路徑（可跟 3 段連續改名）；找不到回 None。"""
    for candidate_base in ([base] if base else []) + [None]:
        mapping = rename_map(root, candidate_base)
        current = relpath
        for _ in range(3):
            nxt = mapping.get(current)
            if not nxt or nxt == current:
                break
            current = nxt
            if (root / current).exists():
                return current
    return None


# ---------------------------------------------------------------- 文字解析


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group("body").split("\n"):
        if line.startswith(("#", " ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = re.sub(r"\s+#.*\Z", "", value).strip().strip("\"'")
        fm[key.strip()] = value
    return fm


def fenced_spans(text: str) -> list[tuple[int, int]]:
    """```/~~~ 圍起來的區塊範圍（範例碼裡的錨點不檢查，避免誤報）。"""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for m in FENCE_RE.finditer(text):
        if start is None:
            start = m.start()
        else:
            spans.append((start, m.end()))
            start = None
    if start is not None:
        spans.append((start, len(text)))
    return spans


def parse_ignores(text: str) -> dict[int, set[str]]:
    """回傳 {行號: {檢查碼}}；沒寫 reason= 的一律不生效。"""
    out: dict[int, set[str]] = {}
    for lineno, line in enumerate(text.split("\n"), 1):
        for m in IGNORE_RE.finditer(line):
            body = m.group("body")
            rm = REASON_RE.search(body)
            if not rm or not rm.group("reason").strip():
                continue  # 沒寫 reason → 抑制不生效
            codes = {
                c.strip().upper()
                for c in re.split(r"[,\s]+", body[: rm.start()])
                if c.strip()
            }
            if codes:
                out.setdefault(lineno, set()).update(codes)
    return out


def is_ignored(ignores: dict[int, set[str]], code: str, line: int | None) -> bool:
    def hit(codes: set[str]) -> bool:
        return code in codes or "*" in codes or "ALL" in codes

    if line:
        return any(hit(ignores[ln]) for ln in (line, line - 1) if ln in ignores)
    return any(hit(codes) for codes in ignores.values())  # 檔案級（D7）


def scan_anchors(text: str) -> list[dict]:
    """掃出所有錨點（略過 fenced code block）。"""
    skip = fenced_spans(text)
    anchors: list[dict] = []
    for m in ANCHOR_RE.finditer(text):
        if any(s <= m.start() < e for s, e in skip):
            continue
        raw_path = m.group("path").rstrip(".,;:、，。")
        if not raw_path:
            continue
        path_end = m.start("path") + len(raw_path)
        hint = HINT_RE.match(text[m.end():])
        anchors.append(
            {
                "kind": m.group("kind"),
                "path": raw_path,
                "symbol": m.group("symbol"),
                "sha1": m.group("sha1"),
                "token": m.group(0),
                "line": text.count("\n", 0, m.start()) + 1,
                "path_span": (m.start("path"), path_end),
                "hint": int(hint.group("line")) if hint else None,
                # 只涵蓋數字本身，--fix 換掉數字即可，保留 (L…) 外框
                "hint_span": (
                    (m.end() + hint.start("line"), m.end() + hint.end("line"))
                    if hint
                    else None
                ),
            }
        )
    return anchors


def symbol_lines(text: str, symbol: str) -> list[int]:
    """word-boundary 字串比對，回傳符號出現的行號（1-based）。"""
    pat = re.compile(r"(?<![0-9A-Za-z_])" + re.escape(symbol) + r"(?![0-9A-Za-z_])")
    return [i for i, line in enumerate(text.split("\n"), 1) if pat.search(line)]


def read_text_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        return None


def snake_variants(name: str) -> set[str]:
    """table_name → {table_name, tableName, TableName}，降低 D5 WARN 誤報。"""
    parts = [p for p in name.split("_") if p]
    if len(parts) <= 1:
        return {name}
    camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
    return {name, camel, camel[:1].upper() + camel[1:]}


# ---------------------------------------------------------------- 檢查主體


FIX_HINTS = {
    "D1": "確認檔案是否已刪除或搬移；改指到新位置；若該決策已作廢，改寫「決策紀錄」那一條",
    "D2": "先讀該檔確認符號是改名還是刪除；若是決策變了，改寫「決策紀錄」而不是硬改指標（本項不自動修）",
    "D3": "跑 --fix 自動更新行號提示（行號只是給人看的提示，不影響判定）",
    "D4": "確認該行內容變更是否為預期；預期就更新 @sha1: 前綴，非預期就修程式碼",
    "D5F": "在 deploy.sql 補上該表的 DDL，或把錨點改指到正確表名",
    "D5W": "確認該表是否已無人使用；已廢棄就從 deploy.sql 與錨點一併移除，否則忽略本則",
    "D6": "讀過這些檔案的變更後更新 plan.md（決策紀錄／指路），再跑 /plan-drift 重新蓋章 verified_at_commit",
    "D7": "在「指路」章節補上 @code: 錨點，並由 /plan-drift 或 plan-close 寫入 verified_at_commit",
}


def make_finding(
    code: str,
    level: str,
    spec: str,
    line: int | None,
    anchor: str,
    detail: str,
    fix: str,
    autofixable: bool = False,
    edit: tuple[int, int, str] | None = None,
) -> dict:
    return {
        "code": code,
        "level": level,
        "spec": spec,
        "line": line,
        "anchor": anchor,
        "detail": detail,
        "fix": fix,
        "autofixable": autofixable,
        "_edit": edit,
    }


def resolve_anchor_path(anchor: dict, root: Path, spec_dir: Path) -> tuple[Path, str]:
    """回傳（實際檢查的路徑, 相對 root 的顯示路徑）。

    @sql: 先找 .spec/{slug}/ 再找 repo root；@code: 反之。兩邊都試可降低誤報。
    """
    raw = anchor["path"]
    order = [spec_dir, root] if anchor["kind"] == "sql" else [root, spec_dir]
    chosen = (order[0] / raw)
    for base in order:
        cand = base / raw
        if cand.exists():
            chosen = cand
            break
    try:
        rel = os.path.relpath(chosen, root)
    except ValueError:
        rel = str(chosen)
    return chosen, rel


def check_sql_anchor(
    anchor: dict, target: Path, rel: str, spec_rel: str, root: Path
) -> list[dict]:
    """D5：表不在 deploy.sql → FAIL；表在程式碼查無引用 → WARN。"""
    findings: list[dict] = []
    table = anchor["symbol"]
    if not table:
        return findings
    content = read_text_safe(target)
    if content is None:
        return findings
    if not symbol_lines(content, table):
        findings.append(
            make_finding(
                "D5", "FAIL", spec_rel, anchor["line"], anchor["token"],
                f"`{rel}` 內找不到表 `{table}`（deploy.sql 是 SQL 的唯一事實來源）",
                FIX_HINTS["D5F"],
            )
        )
        return findings

    args = ["grep", "-l", "-w", "-F", "-I"]
    for variant in sorted(snake_variants(table)):
        args += ["-e", variant]
    args += ["--", *SQL_REF_EXCLUDES]
    try:
        proc = run_git(root, args)
    except EnvProblem:
        return findings
    if proc.returncode == 1 and not proc.stdout.strip():  # git grep：1 = 沒找到
        findings.append(
            make_finding(
                "D5", "WARN", spec_rel, anchor["line"], anchor["token"],
                f"表 `{table}` 在程式碼中查無引用（已排除 .spec/、*.sql、*.md）",
                FIX_HINTS["D5W"],
            )
        )
    return findings


def check_code_anchor(
    anchor: dict, target: Path, rel: str, spec_rel: str, root: Path, base: str | None
) -> list[dict]:
    findings: list[dict] = []
    symbol = anchor["symbol"]

    # D1：檔案不存在（含改名偵測）
    if not target.exists():
        try:
            new_path = detect_rename(root, rel, base)
        except EnvProblem:
            new_path = None
        if new_path:
            findings.append(
                make_finding(
                    "D1", "FAIL", spec_rel, anchor["line"], anchor["token"],
                    f"錨點檔案 `{rel}` 不存在；git 偵測到已改名為 `{new_path}`",
                    "跑 --fix 自動把錨點改指到新路徑",
                    autofixable=True,
                    edit=(anchor["path_span"][0], anchor["path_span"][1], new_path),
                )
            )
        else:
            findings.append(
                make_finding(
                    "D1", "FAIL", spec_rel, anchor["line"], anchor["token"],
                    f"錨點檔案 `{rel}` 不存在，且 git 查不到改名紀錄",
                    FIX_HINTS["D1"],
                )
            )
        return findings

    if target.is_dir() or not symbol:
        return findings  # T1 錨點（僅路徑）到此為止

    content = read_text_safe(target)
    if content is None:
        return findings  # 讀不到（binary 等）→ 寧可漏報

    lines = symbol_lines(content, symbol)
    loose = False
    if not lines and "." in symbol:
        # Foo.bar 形式：退一步只比對最後一段，寧可漏報
        lines = symbol_lines(content, symbol.rsplit(".", 1)[-1])
        loose = bool(lines)

    # D2：符號不在檔內
    if not lines:
        findings.append(
            make_finding(
                "D2", "FAIL", spec_rel, anchor["line"], anchor["token"],
                f"`{rel}` 內找不到符號 `{symbol}`（word-boundary 字串比對）",
                FIX_HINTS["D2"],
            )
        )
        return findings

    # D3：行號提示位移（只回報新行號，永不 FAIL）
    if anchor["hint"] is not None and anchor["hint"] not in lines and not loose:
        findings.append(
            make_finding(
                "D3", "INFO", spec_rel, anchor["line"], anchor["token"],
                f"行號提示 (L{anchor['hint']}) 已位移，`{symbol}` 現在在 L{lines[0]}",
                FIX_HINTS["D3"],
                autofixable=True,
                edit=(anchor["hint_span"][0], anchor["hint_span"][1], str(lines[0])),
            )
        )

    # D4：T3 內容指紋（僅 WARN）
    if anchor["sha1"]:
        body = content.split("\n")[lines[0] - 1].strip()
        actual = hashlib.sha1(body.encode("utf-8")).hexdigest()
        if not actual.startswith(anchor["sha1"].lower()):
            findings.append(
                make_finding(
                    "D4", "WARN", spec_rel, anchor["line"], anchor["token"],
                    f"T3 指紋不符：`{symbol}` 所在行的 sha1 為 {actual[:len(anchor['sha1'])]}，"
                    f"錨點寫 {anchor['sha1'].lower()}",
                    FIX_HINTS["D4"],
                )
            )
    return findings


def check_lag(
    root: Path, base: str, anchor_rels: list[str], spec_path: Path, spec_rel: str
) -> list[dict]:
    """D6：錨點檔案在 verified_at_commit 之後有變更，而 plan.md 沒跟著動。"""
    if not anchor_rels:
        return []
    proc = run_git(root, ["rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"])
    if proc.returncode != 0:
        raise EnvProblem(
            f"{spec_rel}: verified_at_commit `{base}` 不在這個 repo 的歷史裡，無法檢查文件是否落後"
        )
    diff = run_git(root, ["diff", "--name-status", "-M", f"{base}..HEAD", "--", *anchor_rels])
    if diff.returncode != 0 or not diff.stdout.strip():
        return []
    changed = []
    for line in diff.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        if parts[0].startswith(("R100", "C100")):
            continue  # 純改名／複製、內容一字未改 → 文件不可能因此落後（D1 已負責指標）
        changed.append(parts[-1])
    if not changed:
        return []

    # 最後一次動到錨點檔案的 commit
    log_code = run_git(root, ["log", "-1", "--format=%H", f"{base}..HEAD", "--", *anchor_rels])
    code_commit = log_code.stdout.strip()
    if not code_commit:
        return []

    try:
        plan_rel = os.path.relpath(spec_path, root)
    except ValueError:
        return []
    status = run_git(root, ["status", "--porcelain", "--", plan_rel])
    if status.returncode == 0 and status.stdout.strip():
        return []  # plan.md 有未提交的修改 → 正在更新中，靜默
    log_plan = run_git(root, ["log", "-1", "--format=%H", "--", plan_rel])
    plan_commit = log_plan.stdout.strip()
    if not plan_commit:
        return []  # plan.md 未進 git（.spec/ 常被 gitignore）→ 無法判定，靜默
    if plan_commit == code_commit:
        return []  # 同一個 commit 同時改了碼與文件 → 靜默
    anc = run_git(root, ["merge-base", "--is-ancestor", plan_commit, code_commit])
    if anc.returncode != 0:
        return []  # plan.md 不早於程式碼變更（同時或更新）→ 靜默

    shown = ", ".join(changed[:5]) + (f" 等 {len(changed)} 個檔案" if len(changed) > 5 else "")
    return [
        make_finding(
            "D6", "WARN", spec_rel, None, "",
            f"錨點檔案自 {base[:8]} 之後有變更（{shown}），但 plan.md 未同步更新",
            FIX_HINTS["D6"],
        )
    ]


def check_spec(spec_path: Path, root: Path, do_fix: bool) -> tuple[list[dict], list[str], int, bool, bool]:
    """檢查單一 plan.md。回傳（findings, 環境問題訊息, 自動修筆數, 是否 strict）。"""
    try:
        spec_rel = os.path.relpath(spec_path, root)
    except ValueError:
        spec_rel = str(spec_path)

    text = read_text_safe(spec_path)
    if text is None:
        return [], [f"{spec_rel}: 檔案讀取失敗，無法檢查"], 0, False, False

    fm = parse_frontmatter(text)
    policy = (fm.get("drift_policy") or "normal").lower()
    if policy == "off":
        return [], [], 0, False, True
    strict = policy == "strict"

    spec_dir = spec_path.parent
    ignores = parse_ignores(text)
    anchors = scan_anchors(text)
    base = fm.get("verified_at_commit") or None
    findings: list[dict] = []
    envs: list[str] = []
    anchor_rels: list[str] = []

    for anchor in anchors:
        target, rel = resolve_anchor_path(anchor, root, spec_dir)
        if target.exists() and not target.is_dir() and not rel.startswith(".."):
            anchor_rels.append(rel)
        if anchor["kind"] == "sql":
            findings += check_sql_anchor(anchor, target, rel, spec_rel, root)
        else:
            findings += check_code_anchor(anchor, target, rel, spec_rel, root, base)

    if base and anchors:
        try:
            findings += check_lag(root, base, sorted(set(anchor_rels)), spec_path, spec_rel)
        except EnvProblem as exc:
            envs.append(str(exc))

    # D7：過渡期舊文件，每份只報一次
    missing = []
    if not base:
        missing.append("缺 frontmatter verified_at_commit")
    if not anchors:
        missing.append("沒有任何 @code:／@sql: 錨點")
    if missing:
        findings.append(
            make_finding(
                "D7", "WARN", spec_rel, None, "",
                "、".join(missing) + "（過渡期舊文件，本份只提醒一次）",
                FIX_HINTS["D7"],
            )
        )

    findings = [f for f in findings if not is_ignored(ignores, f["code"], f["line"])]

    fixed = 0
    if do_fix:
        edits = [f["_edit"] for f in findings if f["autofixable"] and f["_edit"]]
        if edits:
            new_text = text
            for start, end, replacement in sorted(edits, key=lambda e: e[0], reverse=True):
                new_text = new_text[:start] + replacement + new_text[end:]
            spec_path.write_text(new_text, encoding="utf-8")
            fixed = len(edits)
            findings = [f for f in findings if not (f["autofixable"] and f["_edit"])]

    findings.sort(key=lambda f: (f["line"] or 0, f["code"]))
    return findings, envs, fixed, strict, False


# ---------------------------------------------------------------- 輸入與輸出


def collect_specs(root: Path, args: argparse.Namespace) -> list[Path]:
    if args.spec:
        return [Path(s).resolve() for s in args.spec]
    found = sorted(root.glob(".spec/*/plan.md")) + sorted(root.glob("*/.spec/*/plan.md"))
    return sorted({p.resolve() for p in found})


def render_text(findings: list[dict], envs: list[str], specs: int, fixed: int, skipped: int = 0) -> None:
    for msg in envs:
        print(f"{LEVEL_ICON['ENV']} 無法檢查：{msg}")
        print("   修法：確認在 git 工作區內執行（或用 --root 指定 repo 根目錄），"
              "並確認 verified_at_commit 仍在歷史中")
    for f in findings:
        loc = f"{f['spec']}:{f['line']}" if f["line"] else f["spec"]
        head = f"{LEVEL_ICON[f['level']]} [{f['code']}] {loc}"
        if f["anchor"]:
            head += f" `{f['anchor']}`"
        print(head)
        print(f"   {f['detail']}")
        print(f"   修法：{f['fix']}")

    counts = {lv: sum(1 for f in findings if f["level"] == lv) for lv in ("FAIL", "WARN", "INFO")}
    if fixed:
        print(f"🔧 已自動修復 {fixed} 筆機械型問題（D1 改名／D3 行號），請 git diff 確認後提交")
    # drift_policy: off 的檔案是「沒檢查」，不是「檢查過沒問題」——
    # 若在總結裡混為一談，等於給出假保證，正是這支工具要消滅的東西。
    skipped_note = f"（另有 {skipped} 份 drift_policy: off，未檢查）" if skipped else ""
    checked = specs - skipped
    if findings or envs:
        print(
            f"\n檢查 {checked} 份 plan.md："
            f"FAIL {counts['FAIL']}／WARN {counts['WARN']}／INFO {counts['INFO']}"
            + (f"／環境問題 {len(envs)}" if envs else "")
            + skipped_note
        )
    elif checked == 0:
        print(f"⏭️  {specs} 份 plan.md 全部設為 drift_policy: off，未做任何檢查")
        print("   修法：確認這是刻意的；要恢復檢查請把 frontmatter 改回 normal")
    else:
        print(f"✅ 檢查 {checked} 份 plan.md，所有錨點有效{skipped_note}")


def render_json(findings: list[dict], envs: list[str]) -> None:
    out = [
        {
            "code": "E1",
            "level": "ENV",
            "spec": None,
            "line": None,
            "anchor": "",
            "detail": f"無法檢查：{msg}",
            "fix": "確認在 git 工作區內執行（或用 --root 指定 repo 根目錄），"
                   "並確認 verified_at_commit 仍在歷史中",
            "autofixable": False,
        }
        for msg in envs
    ]
    out += [{k: f[k] for k in JSON_FIELDS} for f in findings]
    print(json.dumps(out, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="check-spec-drift.py",
        description="偵測 .spec/{slug}/plan.md 的程式碼錨點是否失效（文件漂移）",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec", action="append", metavar="PATH", help="要檢查的 plan.md（可重複）")
    g.add_argument("--all", action="store_true", help="檢查 <root>/.spec/*/plan.md 全部")
    p.add_argument("--root", default=".", metavar="DIR", help="專案根目錄（預設 .）")
    p.add_argument("--format", choices=("text", "json"), default="text", help="輸出格式")
    p.add_argument("--strict", action="store_true", help="WARN 也視為失敗（exit 1）")
    p.add_argument("--fix", action="store_true", help="自動修機械型問題（D1 改名、D3 行號）")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()

    try:
        git_toplevel(root)
    except EnvProblem as exc:
        if args.format == "json":
            render_json([], [str(exc)])
        else:
            print(f"{LEVEL_ICON['ENV']} 無法檢查：{exc}")
            print("   修法：改到 git 工作區內執行，或用 --root 指定 repo 根目錄")
        return 3

    specs = collect_specs(root, args)
    if not specs:
        if args.format == "json":
            render_json([], [])
        else:
            print("✅ 找不到任何 .spec/*/plan.md，無錨點可檢查")
        return 0

    findings: list[dict] = []
    envs: list[str] = []
    fixed_total = 0
    strict_specs: set[str] = set()
    skipped_total = 0

    for spec in specs:
        if not spec.exists():
            try:
                rel = os.path.relpath(spec, root)
            except ValueError:
                rel = str(spec)
            envs.append(f"{rel}: 檔案不存在，無法檢查")
            continue
        f, e, fixed, strict, skipped = check_spec(spec, root, args.fix)
        findings += f
        envs += e
        fixed_total += fixed
        if skipped:
            skipped_total += 1
        if strict and f:
            strict_specs.add(f[0]["spec"])

    findings.sort(key=lambda x: (x["spec"], x["line"] or 0, x["code"]))

    if args.format == "json":
        render_json(findings, envs)
    else:
        render_text(findings, envs, len(specs), fixed_total, skipped_total)

    if any(f["level"] == "FAIL" for f in findings):
        return 1
    if envs:
        return 3
    warns = [f for f in findings if f["level"] == "WARN"]
    if warns:
        escalated = [f for f in warns if f["spec"] in strict_specs]
        if args.strict or escalated:
            if args.format == "text":
                why = "--strict" if args.strict else "drift_policy: strict"
                print(f"（{why}：WARN 視為失敗，exit 1）")
            return 1
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
