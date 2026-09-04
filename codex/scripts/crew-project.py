#!/usr/bin/env python3
"""Local setup, task creation, diagnostics and closure gates for CREW for Codex."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

SCRIPTS = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("crew_state", SCRIPTS / "crew-state.py")
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)


def run_state(*args):
    return state.main(list(args))


def config_path(root):
    path = root / ".crew" / "config.json"
    if not path.resolve().is_relative_to(root):
        raise ValueError(".crew/config.json must stay inside the project")
    return path


def read_config(root):
    path = config_path(root)
    if not path.exists():
        return {"schema_version": 1, "mode": "local", "notion": {}}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("Unsupported .crew/config.json schema")
    if value.get("mode") not in ("local", "notion"):
        raise ValueError("mode must be local or notion")
    if not isinstance(value.get("notion", {}), dict):
        raise ValueError("notion must be an object")
    return value


def write_config(root, value):
    path = config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".json.tmp")
    if temp.is_symlink():
        raise ValueError("Config temporary file cannot be a symlink")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def init(root):
    config = read_config(root)
    if not config_path(root).exists():
        write_config(root, config)
        print(f"Created {config_path(root)} (local mode)")
    else:
        print(f"Preserved {config_path(root)} ({config['mode']} mode)")
    # Intentionally do not modify AGENTS.md, gitignore, global config, or accounts.
    return 0


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=20)


def doctor(root):
    problems = 0
    print(f"Python: {sys.version.split()[0]} ({sys.executable})")
    print(f"Project: {root}")
    try:
        config = read_config(root)
        print(f"Config: {config['mode']} ({'saved' if config_path(root).exists() else 'default'})")
        if config["mode"] == "notion":
            print("Notion: connection/schema must be verified with the host's Notion tools")
    except (ValueError, OSError) as exc:
        print(f"FAIL config: {exc}")
        problems += 1
    if shutil.which("git"):
        result = git(root, "rev-parse", "--show-toplevel")
        print("Git: " + (result.stdout.strip() if result.returncode == 0 else "not a usable Git checkout; drift unavailable"))
    else:
        print("Git: unavailable; task state still works, drift/branches unavailable")
    for slug, _ in state.iter_states(root):
        if run_state("validate", "--slug", slug, "--project", str(root)):
            problems += 1
    # iter_states omits malformed JSON; count those explicitly.
    for path in sorted((root / ".spec").glob("*/state.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            print(f"FAIL {path}: {exc}")
            problems += 1
            continue
        if not isinstance(raw, dict):
            print(f"FAIL {path}: state must be an object")
            problems += 1
    print("Browser / Word / Excel: optional host capabilities; not checked by this local script")
    return 1 if problems else 0


def start(root, slug, name, task_type, demo=False):
    directory = state.spec_dir(root, slug)
    # Refuse even a partial existing task, rather than overwriting its plan.
    if directory.exists():
        raise ValueError(f"Task already exists: {directory}; use an existing task or a new slug")
    init(root)
    directory.mkdir(parents=True)
    title = name or slug
    plan = ("---\ndrift_policy: normal\n---\n\n# " + title + "\n\n"
            "## 目標與範圍\n\n" + title + "\n\n"
            "## 驗收條件\n\n- 待釐清可觀察的成功條件。\n\n"
            "## 決策紀錄\n\n尚未進行設計。\n\n"
            "## 已知取捨與風險\n\n尚未完成調查。\n\n"
            "## 指路\n\n實際閱讀程式碼後補上 @code 錨點。\n\n"
            "## 檢查報告摘要\n\n尚未實作或驗證。\n")
    if demo:
        plan = plan.replace("- 待釐清可觀察的成功條件。", "- 依專案條件輸入關鍵字，能找到符合條件的任務。\n- 沒有符合項目時顯示空狀態。")
        plan = plan.replace("尚未進行設計。", "示範決策：先沿用專案既有查詢方式；尚未實作。")
        plan = plan.replace("尚未完成調查。", "此為本機示範，未連接 Notion，未修改產品程式。")
    (directory / "plan.md").write_text(plan, encoding="utf-8")
    result = run_state("init", "--slug", slug, "--name", title, "--type", task_type,
                       "--project", str(root))
    if result:
        print(f"Task is incomplete; inspect {directory} before retrying", file=sys.stderr)
        return result
    print(f"Plan: {directory / 'plan.md'}")
    return 0


def close_check(root, slug, allow_warnings):
    if run_state("validate", "--slug", slug, "--project", str(root)):
        return 1
    current = state.read_state(root, slug)
    plan = state.spec_dir(root, slug) / "plan.md"
    failures, warnings = [], []
    if not plan.is_file():
        failures.append("plan.md is missing")
    else:
        text = plan.read_text(encoding="utf-8")
        import re
        if re.search(r"(?m)^drift_policy:\s*['\"]?off", text):
            failures.append("drift_policy off cannot satisfy closure")
    if current.get("inferred"):
        failures.append("State is inferred; verify it before closing")
    unit = current.get("work_unit", {})
    if unit.get("remaining") or unit.get("ambiguities") or state.as_int(unit.get("done")) < state.as_int(unit.get("total")):
        failures.append("Unfinished work units or unresolved ambiguities")
    for step in state.STEPS[:-1]:
        entry = current["steps"][step]
        if entry["status"] not in state.DONE_LIKE:
            failures.append(f"{step}: {entry['status']}")
        if entry["status"] == "skipped" and not entry.get("reason"):
            failures.append(f"{step}: skipped without a reason")
    for kind in ("security", "verify", "review"):
        report = current.get("results", {}).get(kind, {})
        status = str(report.get("status", "")).upper()
        if state.as_int(report.get("critical")) > 0 or status == "FAIL":
            failures.append(f"{kind}: unresolved failure")
        elif status == "WARN" or state.as_int(report.get("warnings")) > 0:
            warnings.append(f"{kind}: warnings require user acceptance")
        elif current["steps"][kind]["status"] == "done" and status != "PASS":
            failures.append(f"{kind}: missing fresh PASS result")
    if failures:
        print("\n".join("FAIL " + item for item in failures))
        return 1
    result = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPTS / "check-spec-drift.py"),
                             "--root", str(root), "--spec", str(plan)], timeout=60)
    if result.returncode not in (0, 2):
        return result.returncode
    if result.returncode == 2:
        warnings.append("Drift warnings require user acceptance")
    for item in warnings:
        print("WARN " + item)
    if warnings and not allow_warnings:
        return 2
    print("Closure checks passed; requested Git/Notion actions still need completion.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "doctor", "start", "demo", "mode", "close-check"):
        command = subs.add_parser(name)
        command.add_argument("--project", type=Path, default=Path.cwd())
        if name in ("start", "demo", "close-check"):
            command.add_argument("--slug", required=name in ("start", "close-check"))
        if name in ("start", "demo"):
            command.add_argument("--name", default="")
            command.add_argument("--type", choices=("bug", "feature"), default="feature")
        if name == "mode":
            command.add_argument("--value", choices=("local", "notion"), required=True)
        if name == "close-check":
            command.add_argument("--allow-warnings", action="store_true")
    args = parser.parse_args(argv)
    root = args.project.expanduser().resolve()
    try:
        if not root.is_dir():
            raise ValueError(f"Project does not exist: {root}")
        if args.command == "init":
            return init(root)
        if args.command == "doctor":
            return doctor(root)
        if args.command == "mode":
            config = read_config(root)
            config["mode"] = args.value
            write_config(root, config)
            print(f"Saved {args.value} mode; this does not authorize or test a connection")
            return 0
        if args.command == "close-check":
            return close_check(root, args.slug, args.allow_warnings)
        slug = args.slug or "demo-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        return start(root, slug, args.name or ("任務搜尋示範" if args.command == "demo" else slug),
                     args.type, args.command == "demo")
    except (ValueError, OSError, state.CrewError, subprocess.TimeoutExpired) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
