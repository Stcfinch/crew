"""Behavioral smoke tests for the Codex port; no live services or accounts."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "codex/scripts/crew-state.py"
PROJECT = ROOT / "codex/scripts/crew-project.py"
INSTALL = ROOT / "scripts/install-codex.py"


class CodexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="crew-test-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, script, *args, code=0):
        result = subprocess.run([sys.executable, "-X", "utf8", str(script), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return result.stdout

    def state(self, command, *args, code=0):
        return self.run_script(STATE, command, "--project", self.root, "--slug", "sample", *args, code=code)

    def start(self, task_type="feature"):
        return self.run_script(PROJECT, "start", "--project", self.root, "--slug", "sample",
                               "--name", "中文測試", "--type", task_type)

    def test_local_start_preserves_config_and_refuses_overwrite(self):
        self.run_script(PROJECT, "init", "--project", self.root)
        config = self.root / ".crew/config.json"
        value = json.loads(config.read_text(encoding="utf-8"))
        value["custom"] = {"keep": True}
        config.write_text(json.dumps(value), encoding="utf-8")
        self.start()
        self.assertEqual(json.loads(config.read_text(encoding="utf-8")), value)
        plan = self.root / ".spec/sample/plan.md"
        before = plan.read_bytes()
        self.run_script(PROJECT, "start", "--project", self.root, "--slug", "sample", code=1)
        self.assertEqual(plan.read_bytes(), before)
        self.state("validate")

    def test_bug_next_resume_and_failures(self):
        self.start("bug")
        self.assertEqual(json.loads(self.state("next"))["command"], "$bug-investigate sample")
        self.state("set", "--step", "spec", "--status", "done")
        self.assertEqual(json.loads(self.state("next"))["command"], "$bug-fix sample")
        self.state("unit", "--skill", "$bug-fix", "--done", "1", "--total", "3", "--remaining", "case-two")
        self.assertEqual(json.loads(self.state("next"))["command"], "$bug-fix --resume sample")
        self.state("unit", "--clear")
        self.state("set", "--step", "build", "--status", "done")
        self.state("result", "--kind", "security", "--status", "FAIL", "--set", "critical=1")
        self.assertEqual(json.loads(self.state("next"))["command"], "$bug-fix sample")
        brief = self.run_script(STATE, "session-brief", "--project", self.root)
        self.assertIn("$plan-next sample", brief)

    def test_traversal_and_absolute_slugs_rejected_without_writes(self):
        for slug in ("../outside", "a/b", "a\\b", str(self.root / "absolute"), "CON."):
            self.run_script(STATE, "init", "--project", self.root, "--slug", slug, code=1)
        self.assertFalse((self.root / ".spec").exists())

    def test_lock_contention_and_release(self):
        self.start()
        code = ("import importlib.util, pathlib, time; "
                "s=importlib.util.spec_from_file_location('crew', " + repr(str(STATE)) + "); "
                "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                "ctx=m.state_lock(pathlib.Path(" + repr(str(self.root / ".spec/sample")) + ")); "
                "ctx.__enter__(); print('ready', flush=True); time.sleep(10)")
        owner = subprocess.Popen([sys.executable, "-X", "utf8", "-c", code],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        try:
            self.assertEqual(owner.stdout.readline().strip(), "ready")
            self.state("set", "--name", "contended", code=3)
        finally:
            owner.terminate()
            owner.communicate(timeout=10)
        self.state("set", "--name", "after-release")
        self.state("validate")

    def test_demo_does_not_claim_implementation(self):
        self.run_script(PROJECT, "demo", "--project", self.root, "--slug", "sample")
        value = json.loads((self.root / ".spec/sample/state.json").read_text(encoding="utf-8"))
        self.assertEqual(value["steps"]["build"]["status"], "pending")
        self.assertIsNone(value["notion"]["page_id"])
        self.run_script(PROJECT, "close-check", "--project", self.root, "--slug", "sample", code=1)

    def test_doctor_detects_corrupt_state(self):
        self.start()
        (self.root / ".spec/sample/state.json").write_text("broken", encoding="utf-8")
        self.run_script(PROJECT, "doctor", "--project", self.root, code=1)

    def init_git(self):
        for args in (("init",), ("config", "user.email", "test@example.invalid"),
                     ("config", "user.name", "CREW test")):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        (self.root / "app.py").write_text("def target():\n    return 1\n", encoding="utf-8")
        for args in (("add", "app.py"), ("commit", "-m", "fixture")):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)
        return subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()

    def test_closure_requires_real_results_and_valid_anchors(self):
        commit = self.init_git()
        self.start()
        plan = self.root / ".spec/sample/plan.md"
        plan.write_text(f"---\nverified_at_commit: {commit}\n---\n\n@code:app.py#target\n", encoding="utf-8")
        for step in ("spec", "db", "arch", "build", "security", "verify", "review"):
            self.state("set", "--step", step, "--status", "done")
        self.run_script(PROJECT, "close-check", "--project", self.root, "--slug", "sample", code=1)
        for kind in ("security", "verify", "review"):
            self.state("result", "--kind", kind, "--status", "PASS", "--set", "critical=0")
        self.run_script(PROJECT, "close-check", "--project", self.root, "--slug", "sample")
        self.state("result", "--kind", "verify", "--status", "STALE")
        self.run_script(PROJECT, "close-check", "--project", self.root, "--slug", "sample", code=1)
        self.state("result", "--kind", "verify", "--status", "PASS")
        plan.write_text(f"---\nverified_at_commit: {commit}\n---\n\n@code:app.py#missing\n", encoding="utf-8")
        self.run_script(PROJECT, "close-check", "--project", self.root, "--slug", "sample", code=1)

    def test_personal_install_isolated_and_update_preserves_marketplace(self):
        home = self.root / "home"
        market = home / ".agents/plugins/marketplace.json"
        market.parent.mkdir(parents=True)
        unrelated = {"name": "existing", "source": {"source": "local", "path": "./plugins/existing"}}
        market.write_text(json.dumps({"name": "personal", "interface": {"displayName": "My Tools"},
                                     "plugins": [unrelated]}), encoding="utf-8")
        self.run_script(INSTALL, "--home", home, "--no-enable", "--dry-run")
        self.assertFalse((home / "plugins").exists())
        self.run_script(INSTALL, "--home", home, "--no-enable")
        target = home / "plugins/crew"
        self.assertEqual(len(list((target / "skills").glob("*/SKILL.md"))), 27)
        self.assertFalse((target / "plugins").exists())
        self.assertFalse((target / ".git").exists())
        self.assertFalse((target / "hooks").exists())
        self.assertFalse((target / ".claude-plugin").exists())
        first_version = json.loads((target / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.run_script(INSTALL, "--home", home, "--no-enable", code=1)
        self.run_script(INSTALL, "--home", home, "--no-enable", "--update")
        catalog = json.loads(market.read_text(encoding="utf-8"))
        self.assertEqual(catalog["plugins"][0], unrelated)
        self.assertEqual(catalog["interface"]["displayName"], "My Tools")
        self.assertEqual(len(catalog["plugins"]), 2)
        self.assertTrue(list((home / "plugins").glob("crew.backup-*")))
        version = json.loads((target / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        self.assertNotEqual(version, first_version)
        self.run_script(target / "codex/scripts/crew-project.py", "demo", "--project", self.root, "--slug", "installed-demo")


if __name__ == "__main__":
    unittest.main()
