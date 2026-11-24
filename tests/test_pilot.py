"""Verify the fixed ACS pilot fixture and fresh installation, not a live host."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs/evaluation/pilot"
INSTALL = ROOT / "scripts/install.py"


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def fixture(self, name):
        target = self.base / name
        shutil.copytree(PILOT / "fixture", target)
        return target

    def external_check(self, target, case, expected):
        result = subprocess.run([sys.executable, str(PILOT / "check.py"), case, str(target)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, expected, result.stderr or result.stdout)

    def test_fixed_cases_reject_incomplete_seed_and_accept_reference_changes(self):
        for case in ("simple", "normal", "complex"):
            with self.subTest(case=case):
                target = self.fixture(case)
                self.external_check(target, case, 1)
                if case == "simple":
                    path = target / "README.md"
                    path.write_text(path.read_text().replace("summmary", "summary"))
                elif case == "normal":
                    path = target / "report.py"
                    path.write_text(path.read_text().replace(
                        "def total(rows):\n    return sum(row[\"amount\"] for row in rows)",
                        "def total(rows, category=None):\n"
                        "    return sum(row['amount'] for row in rows\n"
                        "               if category is None or row['category'] == category)"))
                else:
                    path = target / "report.py"
                    path.write_text(path.read_text().replace(
                        '    return row.get("public") or row.get("owner") == viewer',
                        "    owner = row.get('owner')\n"
                        "    return row.get('public') is True or (\n"
                        "        isinstance(viewer, str) and isinstance(owner, str)\n"
                        "        and bool(viewer) and viewer == owner)"))
                self.external_check(target, case, 0)

    def test_fresh_balanced_setup_for_each_host_with_and_without_hooks(self):
        for host in ("codex", "claude-code"):
            for enabled in (False, True):
                with self.subTest(host=host, hooks=enabled):
                    target = self.fixture(f"{host}-{enabled}")
                    subprocess.run(["git", "init", "--template=", "-q", str(target)], check=True)
                    def cli(command, *opts):
                        result = subprocess.run(
                            [sys.executable, str(INSTALL), command, "--target", str(target), *opts],
                            capture_output=True, text=True, timeout=30)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        return json.loads(result.stdout)
                    selection = ("--modules", "acs", "--providers", host)
                    if enabled:
                        selection += ("--guard-providers", host, "--telemetry-providers", host)
                    preview = cli("preview", *selection)
                    self.assertEqual(preview["requested"]["profile"], "balanced")
                    self.assertEqual(preview["selection"]["skills"], [])
                    self.assertEqual(preview["requested"]["guard_providers"], [host] if enabled else [])
                    self.assertTrue(cli("apply", *selection, "--approve", preview["approval"])["applied"])
                    self.assertTrue(cli("status")["installed"])
                    self.assertEqual(cli("preview")["changes"], [])
                    for file in ("README.md", "report.py"):
                        self.assertEqual((target / file).read_bytes(),
                                         (PILOT / "fixture" / file).read_bytes())
                    profile = json.loads((target / f".agents/setup/profile-{host}.json").read_text())
                    self.assertEqual(profile["profile"], "balanced")
                    self.assertEqual(profile["evidence"], "configured")
                    self.assertEqual(len(profile["roles"]), 10)
                    native = ".codex/agents" if host == "codex" else ".claude/agents"
                    self.assertEqual(len(list((target / native).glob("acs-*"))), 9)
                    other = ".claude" if host == "codex" else ".codex"
                    self.assertFalse((target / other).exists())
                    settings = target / (".codex/hooks.json" if host == "codex" else ".claude/settings.json")
                    self.assertEqual(settings.exists(), enabled)
                    self.assertEqual((target / ".agents/hooks/runtime.py").exists(), enabled)
                    if enabled:
                        home = self.base / f"home-{host}"
                        home.mkdir()
                        hooks = json.loads(settings.read_text())["hooks"]
                        command = hooks["SessionStart"][0]["hooks"][0]["command"]
                        result = subprocess.run(command, shell=True, cwd=target,
                                                input='{"hook_event_name":"SessionStart"}',
                                                capture_output=True, text=True, timeout=3,
                                                env={**os.environ, "HOME": str(home),
                                                     "CLAUDE_PROJECT_DIR": str(target)})
                        self.assertEqual(result.returncode, 0, result.stderr)
                        self.assertEqual((result.stdout, result.stderr), ("", ""))
                        logs = list(home.glob(".local/state/agent-setup-hooks/*/*.jsonl"))
                        self.assertEqual(len(logs), 1)
                        record = json.loads(logs[0].read_text())
                        self.assertEqual(record["provider"], host)
                        self.assertEqual(record["event"], "SessionStart")
                        self.assertFalse(record["runtime_verified"])
                        self.assertIsNone(record["usage"])
                    else:
                        self.assertFalse((target / ".agents/hooks").exists())


if __name__ == "__main__":
    unittest.main()
