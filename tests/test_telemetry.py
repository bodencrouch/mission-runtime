#!/usr/bin/env python3
"""Tests for the mission-runtime telemetry scripts. Standard library only.

    python3 -m unittest discover -s tests -v

The load-bearing property under test is that the recorder exits 0 no matter
what it is fed. Several host hook events treat a non-zero exit as "block this
action", so a recorder that can crash is a recorder that can freeze a user's
session.
"""

from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RECORDER = os.path.join(ROOT, "scripts", "mr_record.py")
REPORT = os.path.join(ROOT, "scripts", "mr_report.py")
DOCTOR = os.path.join(ROOT, "scripts", "mr_doctor.py")
INSTALL = os.path.join(ROOT, "scripts", "mr_install_hooks.py")


def run_recorder(stdin_text, store, *args, env_extra=None):
    env = dict(os.environ)
    env["MISSIONRUNTIME_HOME"] = store
    env.pop("MISSIONRUNTIME_TELEMETRY", None)
    env.pop("MISSIONRUNTIME_REDACT", None)
    if env_extra:
        env.update(env_extra)
    return subprocess.run([sys.executable, RECORDER, *args],
                          input=stdin_text, text=True, capture_output=True,
                          timeout=30, env=env)


def read_records(store):
    out = []
    for path in sorted(glob.glob(os.path.join(store, "sessions", "*", "*.jsonl"))):
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    out.append(json.loads(line))
    return out


class RecorderNeverBlocks(unittest.TestCase):
    """Every one of these must exit 0. Non-zero can block a host session."""

    HOSTILE = [
        ("empty", ""),
        ("whitespace", "   \n  "),
        ("not json", "this is not json at all"),
        ("truncated json", '{"session_id": "abc"'),
        ("json array", '[1,2,3]'),
        ("json string", '"just a string"'),
        ("json null", 'null'),
        ("json number", '42'),
        ("nul bytes", '{"session_id":"a\u0000b"}'),
        ("raw control chars", '{"session_id":"a\x01\x02b"}'),
        ("deep nesting", json.dumps({"session_id": "deep", "d": {"a": {"b": {"c": {"d": {"e": 1}}}}}})),
        ("huge string", json.dumps({"session_id": "huge", "prompt": "x" * 500000})),
        ("weird session id", json.dumps({"session_id": "../../etc/passwd"})),
        ("absolute path session id", json.dumps({"session_id": "/etc/shadow"})),
        ("non-string session id", json.dumps({"session_id": {"nested": True}})),
        ("unicode", json.dumps({"session_id": "u1", "prompt": "héllo 🌍 ‮"})),
    ]

    def test_hostile_inputs_all_exit_zero(self):
        for label, payload in self.HOSTILE:
            with self.subTest(case=label):
                with tempfile.TemporaryDirectory() as store:
                    proc = run_recorder(payload, store, "--event", "T",
                                        "--host", "test")
                    self.assertEqual(proc.returncode, 0,
                                     f"{label}: stderr={proc.stderr}")

    def test_path_traversal_session_id_stays_inside_store(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({"session_id": "../../../escape"}),
                         store, "--event", "T", "--host", "test")
            escaped = os.path.join(os.path.dirname(store), "escape.jsonl")
            self.assertFalse(os.path.exists(escaped))
            files = glob.glob(os.path.join(store, "sessions", "*", "*.jsonl"))
            self.assertEqual(len(files), 1)
            self.assertNotIn("..", os.path.basename(files[0]))

    def test_unwritable_store_does_not_crash(self):
        with tempfile.TemporaryDirectory() as parent:
            store = os.path.join(parent, "ro")
            os.makedirs(store)
            os.chmod(store, 0o500)
            try:
                proc = run_recorder(json.dumps({"session_id": "x"}), store,
                                    "--event", "T", "--host", "test")
                self.assertEqual(proc.returncode, 0)
            finally:
                os.chmod(store, 0o700)

    def test_missing_args_ok(self):
        with tempfile.TemporaryDirectory() as store:
            proc = run_recorder(json.dumps({"session_id": "x"}), store)
            self.assertEqual(proc.returncode, 0)


class RecorderCaptures(unittest.TestCase):

    def test_normalizes_claude_subagent_stop(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({
                "session_id": "s1", "hook_event_name": "SubagentStop",
                "agent_id": "a1", "agent_type": "test-engineer",
                "last_assistant_message": "done", "cwd": store,
            }), store, "--event", "SubagentStop", "--host", "claude")
            rec = read_records(store)[0]
            self.assertEqual(rec["agent_type"], "test-engineer")
            self.assertEqual(rec["agent_id"], "a1")
            self.assertEqual(rec["last_message"], "done")

    def test_normalizes_cursor_dialect(self):
        """Cursor uses subagent_id/subagent_type and conversation_id."""
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({
                "conversation_id": "c1", "subagent_id": "sa1",
                "subagent_type": "reviewer", "duration_ms": 1234,
                "tool_call_count": 7,
            }), store, "--event", "SubagentStop", "--host", "cursor")
            rec = read_records(store)[0]
            self.assertEqual(rec["session_id"], "c1")
            self.assertEqual(rec["agent_id"], "sa1")
            self.assertEqual(rec["agent_type"], "reviewer")
            self.assertEqual(rec["duration_ms"], 1234)

    def test_normalizes_copilot_camelcase(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({
                "sessionId": "cp1", "toolName": "shell",
                "toolArgs": {"cmd": "ls"},
            }), store, "--event", "PostToolUse", "--host", "copilot")
            rec = read_records(store)[0]
            self.assertEqual(rec["session_id"], "cp1")
            self.assertEqual(rec["tool_name"], "shell")

    def test_lifts_delegated_prompt_from_spawn(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({
                "session_id": "s2", "tool_name": "Agent",
                "tool_input": {"subagent_type": "research-analyst",
                               "prompt": "Go research X"},
            }), store, "--event", "SubagentSpawn", "--host", "claude")
            rec = read_records(store)[0]
            self.assertEqual(rec["subagent_type"], "research-analyst")
            self.assertEqual(rec["delegated_prompt"], "Go research X")

    def test_all_three_tool_result_field_names_captured(self):
        """Hosts disagree on this field name; all candidates must work."""
        for name in ("tool_output", "tool_result", "tool_response"):
            with self.subTest(field=name):
                with tempfile.TemporaryDirectory() as store:
                    run_recorder(json.dumps({"session_id": "s", name: "RESULT"}),
                                 store, "--event", "PostToolUse", "--host", "x")
                    self.assertEqual(read_records(store)[0]["tool_result"],
                                     "RESULT")

    def test_raw_payload_retained(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({"session_id": "s", "future_field": "v"}),
                         store, "--event", "T", "--host", "x")
            self.assertEqual(read_records(store)[0]["payload"]["future_field"],
                             "v")

    def test_mission_active_detected(self):
        with tempfile.TemporaryDirectory() as store:
            proj = os.path.join(store, "proj")
            os.makedirs(os.path.join(proj, ".mission"))
            run_recorder(json.dumps({"session_id": "s", "cwd": proj}),
                         store, "--event", "T", "--host", "x")
            self.assertTrue(read_records(store)[0]["mission_active"])

    def test_mission_inactive_when_no_mission_dir(self):
        with tempfile.TemporaryDirectory() as store:
            proj = os.path.join(store, "plain")
            os.makedirs(proj)
            run_recorder(json.dumps({"session_id": "s", "cwd": proj}),
                         store, "--event", "T", "--host", "x")
            self.assertFalse(read_records(store)[0]["mission_active"])


class ConfigControls(unittest.TestCase):

    def test_env_switch_disables_recording(self):
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({"session_id": "s"}), store,
                         "--event", "T", "--host", "x",
                         env_extra={"MISSIONRUNTIME_TELEMETRY": "off"})
            self.assertEqual(read_records(store), [])

    def test_config_file_disables_recording(self):
        with tempfile.TemporaryDirectory() as store:
            with open(os.path.join(store, "config.json"), "w") as fh:
                json.dump({"enabled": False}, fh)
            run_recorder(json.dumps({"session_id": "s"}), store,
                         "--event", "T", "--host", "x")
            self.assertEqual(read_records(store), [])

    def test_env_beats_config_file(self):
        with tempfile.TemporaryDirectory() as store:
            with open(os.path.join(store, "config.json"), "w") as fh:
                json.dump({"enabled": False}, fh)
            run_recorder(json.dumps({"session_id": "s"}), store,
                         "--event", "T", "--host", "x",
                         env_extra={"MISSIONRUNTIME_TELEMETRY": "on"})
            self.assertEqual(len(read_records(store)), 1)

    def test_redaction_removes_prompt_text(self):
        secret = "my api key is sk-abcdef123456"
        with tempfile.TemporaryDirectory() as store:
            run_recorder(json.dumps({"session_id": "s", "prompt": secret}),
                         store, "--event", "UserPromptSubmit", "--host", "x",
                         env_extra={"MISSIONRUNTIME_REDACT": "1"})
            rec = read_records(store)[0]
            self.assertTrue(rec["prompt"]["redacted"])
            self.assertEqual(rec["prompt"]["chars"], len(secret))
            # The raw payload must not leak what the normalized view redacted.
            self.assertNotIn("payload", rec)
            self.assertEqual(rec["payload_omitted"], "redacted")
            self.assertNotIn("sk-abcdef123456", json.dumps(rec))

    def test_malformed_config_falls_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as store:
            with open(os.path.join(store, "config.json"), "w") as fh:
                fh.write("{ this is not json")
            proc = run_recorder(json.dumps({"session_id": "s"}), store,
                                "--event", "T", "--host", "x")
            self.assertEqual(proc.returncode, 0)
            self.assertEqual(len(read_records(store)), 1)

    def test_capture_tool_io_false_drops_tool_payload_fields(self):
        with tempfile.TemporaryDirectory() as store:
            with open(os.path.join(store, "config.json"), "w") as fh:
                json.dump({"capture_tool_io": False}, fh)
            run_recorder(json.dumps({"session_id": "s", "tool_name": "Bash",
                                     "tool_input": {"command": "rm -rf /"}}),
                         store, "--event", "PostToolUse", "--host", "x")
            rec = read_records(store)[0]
            self.assertNotIn("tool_input", rec)
            self.assertEqual(rec["tool_name"], "Bash")

    def test_truncation_bounds_long_text(self):
        with tempfile.TemporaryDirectory() as store:
            with open(os.path.join(store, "config.json"), "w") as fh:
                json.dump({"max_text_chars": 50}, fh)
            run_recorder(json.dumps({"session_id": "s", "prompt": "y" * 5000}),
                         store, "--event", "UserPromptSubmit", "--host", "x")
            rec = read_records(store)[0]
            self.assertIn("truncated", rec["prompt"])
            self.assertLess(len(rec["prompt"]), 200)


class ReportAndDoctor(unittest.TestCase):

    def _seed(self, store):
        events = [
            ({"session_id": "m1", "cwd": os.path.join(store, "proj")},
             "UserPromptSubmit"),
            ({"session_id": "m1", "tool_name": "Read"}, "PostToolUse"),
            ({"session_id": "m1", "tool_name": "Read"}, "PostToolUse"),
            ({"session_id": "m1", "agent_id": "a", "agent_type": "test-engineer"},
             "SubagentStart"),
            ({"session_id": "m1", "agent_id": "a", "agent_type": "test-engineer"},
             "SubagentStop"),
            ({"session_id": "p1", "cwd": os.path.join(store, "plain")},
             "UserPromptSubmit"),
            ({"session_id": "p1", "tool_name": "Read"}, "PostToolUse"),
        ]
        os.makedirs(os.path.join(store, "proj", ".mission"), exist_ok=True)
        os.makedirs(os.path.join(store, "plain"), exist_ok=True)
        for payload, event in events:
            run_recorder(json.dumps(payload), store, "--event", event,
                         "--host", "test")

    def test_report_json_shape(self):
        with tempfile.TemporaryDirectory() as store:
            self._seed(store)
            env = {**os.environ, "MISSIONRUNTIME_HOME": store}
            proc = subprocess.run([sys.executable, REPORT, "--json"],
                                  capture_output=True, text=True, timeout=60,
                                  env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["sessions"], 2)
            self.assertEqual(data["comparison"]["mission"]["sessions"], 1)
            self.assertEqual(data["comparison"]["non_mission"]["sessions"], 1)
            self.assertEqual(data["comparison"]["mission"]["total_subagents"], 1)
            self.assertIn("test-engineer",
                          [a["agent"] for a in data["agents"]])

    def test_report_on_empty_store_is_graceful(self):
        with tempfile.TemporaryDirectory() as store:
            env = {**os.environ, "MISSIONRUNTIME_HOME": store}
            proc = subprocess.run([sys.executable, REPORT],
                                  capture_output=True, text=True, timeout=60,
                                  env=env)
            self.assertEqual(proc.returncode, 0)
            self.assertIn("No telemetry found", proc.stdout)

    def test_report_survives_corrupt_line(self):
        with tempfile.TemporaryDirectory() as store:
            self._seed(store)
            target = glob.glob(os.path.join(store, "sessions", "*", "*.jsonl"))[0]
            with open(target, "a", encoding="utf-8") as fh:
                fh.write("{not json at all\n")
            env = {**os.environ, "MISSIONRUNTIME_HOME": store}
            proc = subprocess.run([sys.executable, REPORT, "--json"],
                                  capture_output=True, text=True, timeout=60,
                                  env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_doctor_runs(self):
        with tempfile.TemporaryDirectory() as store:
            env = {**os.environ, "MISSIONRUNTIME_HOME": store}
            proc = subprocess.run([sys.executable, DOCTOR],
                                  capture_output=True, text=True, timeout=60,
                                  env=env)
            self.assertIn("recorder", proc.stdout)
            self.assertIn("claude hooks", proc.stdout)


class HookConfigs(unittest.TestCase):

    def test_all_hook_configs_are_valid_json(self):
        for name in ("hooks.json", "cursor.json", "copilot.json", "codex.json"):
            with self.subTest(config=name):
                path = os.path.join(ROOT, "hooks", name)
                with open(path, encoding="utf-8") as fh:
                    json.load(fh)

    def test_claude_hooks_reference_the_recorder(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        for event, entries in data["hooks"].items():
            for entry in entries:
                for hook in entry["hooks"]:
                    self.assertIn("mr_record.py", hook["command"], event)

    def test_claude_recording_hooks_are_async_except_session_end(self):
        """A synchronous recorder can stall a turn; SessionEnd is the one
        exception because its async completion is not guaranteed."""
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        for event, entries in data["hooks"].items():
            for entry in entries:
                for hook in entry["hooks"]:
                    if event == "SessionEnd":
                        self.assertNotIn("async", hook)
                        self.assertIn("timeout", hook)
                    else:
                        self.assertTrue(hook.get("async"), event)

    def test_installer_dry_run_renders_valid_json(self):
        for host in ("cursor", "copilot", "codex"):
            with self.subTest(host=host):
                proc = subprocess.run(
                    [sys.executable, INSTALL, "--host", host],
                    capture_output=True, text=True, timeout=60)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertIn("Dry run", proc.stdout)

    def test_installer_writes_and_backs_up(self):
        with tempfile.TemporaryDirectory() as proj:
            target = os.path.join(proj, ".cursor", "hooks.json")
            os.makedirs(os.path.dirname(target))
            with open(target, "w") as fh:
                fh.write('{"version": 1, "hooks": {}}')
            proc = subprocess.run(
                [sys.executable, INSTALL, "--host", "cursor", "--scope",
                 "project", "--project", proj, "--apply"],
                capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            with open(target, encoding="utf-8") as fh:
                written = json.load(fh)
            self.assertIn("sessionStart", written["hooks"])
            self.assertNotIn("__MR_CMD__", json.dumps(written))
            backups = glob.glob(target + ".bak-*")
            self.assertEqual(len(backups), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class AgentCounting(unittest.TestCase):
    """Regression tests for the specialist counter.

    The count of delegations is the headline number in the benchmark, so both
    the missing-spawn and missing-stop cases must be exact.
    """

    def _emit(self, store, events):
        for payload, event in events:
            run_recorder(json.dumps(payload), store, "--event", event,
                         "--host", "test")

    def _report(self, store):
        env = {**os.environ, "MISSIONRUNTIME_HOME": store}
        proc = subprocess.run([sys.executable, REPORT, "--json"],
                              capture_output=True, text=True, timeout=60,
                              env=env)
        assert proc.returncode == 0, proc.stderr
        return json.loads(proc.stdout)

    def test_two_of_same_type_counted_twice_with_full_lifecycle(self):
        with tempfile.TemporaryDirectory() as store:
            self._emit(store, [
                ({"session_id": "s", "tool_name": "Agent",
                  "tool_input": {"subagent_type": "research-analyst"}},
                 "SubagentSpawn"),
                ({"session_id": "s", "agent_id": "a1",
                  "agent_type": "research-analyst"}, "SubagentStop"),
                ({"session_id": "s", "tool_name": "Agent",
                  "tool_input": {"subagent_type": "research-analyst"}},
                 "SubagentSpawn"),
                ({"session_id": "s", "agent_id": "a2",
                  "agent_type": "research-analyst"}, "SubagentStop"),
            ])
            agents = {a["agent"]: a["spawns"] for a in self._report(store)["agents"]}
            self.assertEqual(agents["research-analyst"], 2)

    def test_two_of_same_type_counted_twice_without_spawn_events(self):
        """The fallback path may record stops only — must not collapse to 1."""
        with tempfile.TemporaryDirectory() as store:
            self._emit(store, [
                ({"session_id": "s", "agent_id": "a1",
                  "agent_type": "research-analyst"}, "SubagentStop"),
                ({"session_id": "s", "agent_id": "a2",
                  "agent_type": "research-analyst"}, "SubagentStop"),
            ])
            agents = {a["agent"]: a["spawns"] for a in self._report(store)["agents"]}
            self.assertEqual(agents["research-analyst"], 2)

    def test_spawn_without_stop_still_counted(self):
        """A session killed mid-delegation still did the work."""
        with tempfile.TemporaryDirectory() as store:
            self._emit(store, [
                ({"session_id": "s", "tool_name": "Agent",
                  "tool_input": {"subagent_type": "test-engineer"}},
                 "SubagentSpawn"),
            ])
            report = self._report(store)
            agents = {a["agent"]: a["spawns"] for a in report["agents"]}
            self.assertEqual(agents["test-engineer"], 1)
            detail = report["comparison"]
            total = (detail["mission"]["total_subagents"]
                     + detail["non_mission"]["total_subagents"])
            self.assertEqual(total, 1)

    def test_mixed_types_not_conflated(self):
        with tempfile.TemporaryDirectory() as store:
            self._emit(store, [
                ({"session_id": "s", "tool_name": "Agent",
                  "tool_input": {"subagent_type": "security-reviewer"}},
                 "SubagentSpawn"),
                ({"session_id": "s", "agent_id": "a1",
                  "agent_type": "security-reviewer"}, "SubagentStop"),
                ({"session_id": "s", "agent_id": "a2",
                  "agent_type": "docs-writer"}, "SubagentStop"),
            ])
            agents = {a["agent"]: a["spawns"] for a in self._report(store)["agents"]}
            self.assertEqual(agents["security-reviewer"], 1)
            self.assertEqual(agents["docs-writer"], 1)


class HookCommandsExecute(unittest.TestCase):
    """Run every command string in hooks.json exactly as the host would.

    Reading the JSON only proves it parses. This proves the quoting survives a
    shell, python3 resolves, and a record actually lands on disk — the failure
    modes that would otherwise show up as a silently empty store.
    """

    def test_every_claude_hook_command_runs_and_records(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as fh:
            config = json.load(fh)
        commands = [(event, hook["command"])
                    for event, entries in config["hooks"].items()
                    for entry in entries for hook in entry["hooks"]]
        self.assertGreaterEqual(len(commands), 8)

        with tempfile.TemporaryDirectory() as store:
            env = dict(os.environ)
            env["CLAUDE_PLUGIN_ROOT"] = ROOT
            env["MISSIONRUNTIME_HOME"] = store
            env.pop("MISSIONRUNTIME_TELEMETRY", None)
            for event, command in commands:
                with self.subTest(event=event):
                    proc = subprocess.run(
                        command, shell=True, env=env, text=True,
                        capture_output=True, timeout=30,
                        input=json.dumps({"session_id": "hooksim",
                                          "hook_event_name": event}))
                    self.assertEqual(proc.returncode, 0,
                                     f"{event}: {proc.stderr}")
            self.assertEqual(len(read_records(store)), len(commands))

    def test_hook_commands_survive_a_plugin_path_with_spaces(self):
        """Plugin install paths are not guaranteed to be shell-safe."""
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, "plugin dir with spaces")
            os.makedirs(os.path.join(root, "scripts"))
            shutil.copy2(os.path.join(ROOT, "scripts", "mr_record.py"),
                         os.path.join(root, "scripts", "mr_record.py"))
            store = os.path.join(tmp, "store")
            env = dict(os.environ)
            env["CLAUDE_PLUGIN_ROOT"] = root
            env["MISSIONRUNTIME_HOME"] = store
            env.pop("MISSIONRUNTIME_TELEMETRY", None)
            with open(os.path.join(ROOT, "hooks", "hooks.json"),
                      encoding="utf-8") as fh:
                command = json.load(fh)["hooks"]["Stop"][0]["hooks"][0]["command"]
            proc = subprocess.run(command, shell=True, env=env, text=True,
                                  capture_output=True, timeout=30,
                                  input='{"session_id":"spaces"}')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(len(read_records(store)), 1)
