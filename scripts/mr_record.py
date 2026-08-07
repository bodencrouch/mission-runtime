#!/usr/bin/env python3
"""mission-runtime telemetry recorder.

Reads one JSON object from stdin (a host hook payload), normalizes the fields
that matter for benchmarking, and appends one NDJSON line to the local store.

Design rules, in priority order:

1. Never break the session. Every failure path is swallowed and the process
   exits 0. Hosts treat exit code 2 as "block this action" on several events,
   so an unhandled exception here could hard-stop a user's work.
2. Never phone home. This writes to local disk and nothing else.
3. Never guess a schema. Host payload field names differ between hosts and
   change between releases, so the entire raw payload is retained and the
   normalized view is derived from candidate name lists.

Usage (from a hook config):
    mr_record.py --event SubagentStop --host claude
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import sys

SCHEMA_VERSION = 1

DEFAULT_CONFIG = {
    # Master switch. Env MISSIONRUNTIME_TELEMETRY=off wins over this.
    "enabled": True,
    # When true, prompt and message text is replaced by a length + digest.
    # The digest still lets you tell repeated prompts apart without storing
    # the words.
    "redact_text": False,
    # Longest text field retained before truncation.
    "max_text_chars": 8000,
    # Whether tool inputs/results are captured at all. Tool inputs can contain
    # file contents and command lines.
    "capture_tool_io": True,
    # Longest raw payload retained, in bytes. Beyond this the payload is
    # dropped and only the normalized view is kept.
    "max_payload_bytes": 262144,
}

# Candidate source keys per normalized field, in preference order. Hosts
# disagree: Claude Code uses snake_case, Copilot uses camelCase, Cursor calls a
# subagent `subagent_id`, Codex calls it `agent_id`.
FIELD_ALIASES = {
    "session_id": ("session_id", "sessionId", "conversation_id",
                   "conversationId", "thread-id", "threadId"),
    "turn_id": ("prompt_id", "promptId", "turn_id", "turnId",
                "generation_id", "generationId"),
    "host_event": ("hook_event_name", "hookEventName"),
    "cwd": ("cwd", "workspace_root", "workspaceRoot"),
    "model": ("model", "model_id", "modelId"),
    "tool_name": ("tool_name", "toolName"),
    "tool_use_id": ("tool_use_id", "toolUseId", "tool_call_id", "toolCallId"),
    "agent_id": ("agent_id", "agentId", "subagent_id", "subagentId"),
    "agent_type": ("agent_type", "agentType", "subagent_type", "subagentType"),
    "transcript_path": ("transcript_path", "transcriptPath",
                        "agent_transcript_path", "agentTranscriptPath"),
    "duration_ms": ("duration_ms", "durationMs"),
    "tool_call_count": ("tool_call_count", "toolCallCount"),
    "status": ("status", "final_status", "finalStatus", "stopReason",
               "stop_reason", "end_reason", "endReason", "reason"),
    "source": ("source", "trigger", "composer_mode"),
}

# Text-bearing fields, split out because they are the privacy-sensitive ones.
TEXT_ALIASES = {
    "prompt": ("prompt", "user_prompt", "userPrompt", "task", "description"),
    "last_message": ("last_assistant_message", "lastAssistantMessage",
                     "summary"),
}

# The result of a tool call. Three different names are documented across
# Anthropic's own sources; treat all of them as candidates rather than betting
# on one.
TOOL_RESULT_ALIASES = ("tool_output", "tool_result", "tool_response",
                       "toolResult")
TOOL_INPUT_ALIASES = ("tool_input", "toolInput", "toolArgs", "tool_args")


def store_root() -> str:
    """Where records live. Explicitly overridable so CI and tests can redirect."""
    override = os.environ.get("MISSIONRUNTIME_HOME")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    home = os.path.expanduser("~")
    if not home or home == "~":
        home = os.environ.get("TMPDIR") or "/tmp"
    return os.path.join(home, ".missionruntime")


def load_config(root: str) -> dict:
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(os.path.join(root, "config.json"), encoding="utf-8") as fh:
            user = json.load(fh)
        if isinstance(user, dict):
            for key in DEFAULT_CONFIG:
                if key in user:
                    cfg[key] = user[key]
    except FileNotFoundError:
        pass
    except Exception:
        # A malformed config must not disable recording silently AND must not
        # crash. Fall back to defaults.
        pass

    flag = (os.environ.get("MISSIONRUNTIME_TELEMETRY") or "").strip().lower()
    if flag in ("0", "off", "false", "no", "disabled"):
        cfg["enabled"] = False
    elif flag in ("1", "on", "true", "yes", "enabled"):
        cfg["enabled"] = True

    redact = (os.environ.get("MISSIONRUNTIME_REDACT") or "").strip().lower()
    if redact in ("1", "on", "true", "yes"):
        cfg["redact_text"] = True
    elif redact in ("0", "off", "false", "no"):
        cfg["redact_text"] = False
    return cfg


def first_present(payload: dict, names) -> object:
    for name in names:
        if name in payload and payload[name] is not None:
            return payload[name]
    return None


def scrub_text(value: object, cfg: dict) -> object:
    """Apply the redaction and truncation policy to one text value."""
    if value is None:
        return None
    if not isinstance(value, str):
        try:
            value = json.dumps(value, ensure_ascii=False)
        except Exception:
            value = str(value)
    if cfg["redact_text"]:
        digest = hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()
        return {"redacted": True, "chars": len(value), "sha256": digest[:16]}
    limit = int(cfg["max_text_chars"])
    if len(value) > limit:
        return value[:limit] + f"…[truncated {len(value) - limit} chars]"
    return value


def detect_mission(cwd: str) -> dict:
    """Is a mission-runtime mission active in this working directory?

    This is the flag that makes benchmarking possible: it separates sessions
    where the runtime was driving from sessions where it was not.
    """
    info = {"mission_active": False, "mission_dir": None}
    if not cwd:
        return info
    try:
        candidate = os.path.join(cwd, ".mission")
        if os.path.isdir(candidate):
            info["mission_active"] = True
            info["mission_dir"] = candidate
    except Exception:
        pass
    return info


def build_record(payload: dict, event: str, host: str, cfg: dict) -> dict:
    norm = {}
    for field, names in FIELD_ALIASES.items():
        value = first_present(payload, names)
        if value is not None:
            norm[field] = value

    for field, names in TEXT_ALIASES.items():
        value = first_present(payload, names)
        if value is not None:
            norm[field] = scrub_text(value, cfg)

    if cfg["capture_tool_io"]:
        tool_input = first_present(payload, TOOL_INPUT_ALIASES)
        if tool_input is not None:
            norm["tool_input"] = scrub_text(tool_input, cfg)
            # The subagent's own prompt rides inside the spawn tool's input.
            # It is the single most valuable field for attributing work to a
            # delegation, so lift it to the top level when present.
            if isinstance(tool_input, dict):
                for key in ("subagent_type", "description"):
                    if tool_input.get(key) is not None:
                        norm.setdefault(key, tool_input[key])
                if tool_input.get("prompt") is not None:
                    norm["delegated_prompt"] = scrub_text(
                        tool_input["prompt"], cfg)
        tool_result = first_present(payload, TOOL_RESULT_ALIASES)
        if tool_result is not None:
            norm["tool_result"] = scrub_text(tool_result, cfg)

    record = {
        "schema": SCHEMA_VERSION,
        "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(
            timespec="milliseconds").replace("+00:00", "Z"),
        "event": event or norm.get("host_event") or "unknown",
        "host": host,
        "pid": os.getpid(),
    }
    record.update(norm)
    record.update(detect_mission(str(norm.get("cwd") or "")))

    if cfg["redact_text"]:
        # The raw payload is dropped wholesale under redaction. Scrubbing it
        # selectively would mean knowing every nested key that can hold user
        # text, across four hosts and future releases — a guess that fails
        # silently and leaks. Losing schema-durability is the cheaper mistake.
        record["payload_omitted"] = "redacted"
        return record

    try:
        raw = json.dumps(payload, ensure_ascii=False, default=str)
        if len(raw.encode("utf-8", "replace")) <= int(cfg["max_payload_bytes"]):
            # Retained verbatim so that a host renaming a field does not
            # destroy already-collected data.
            record["payload"] = payload
        else:
            record["payload_dropped_bytes"] = len(raw)
    except Exception:
        record["payload_unserializable"] = True
    return record


def log_error(root: str, message: str) -> None:
    """Best-effort error breadcrumb. Never raises, never grows without bound."""
    try:
        path = os.path.join(root, "recorder.err")
        try:
            if os.path.getsize(path) > 1_048_576:
                os.replace(path, path + ".1")
        except OSError:
            pass
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{_dt.datetime.now(_dt.timezone.utc).isoformat()} "
                     f"{message}\n")
    except Exception:
        pass


def main() -> int:
    root = store_root()
    try:
        args = sys.argv[1:]
        event = ""
        host = "unknown"
        i = 0
        while i < len(args):
            if args[i] == "--event" and i + 1 < len(args):
                event = args[i + 1]
                i += 2
            elif args[i] == "--host" and i + 1 < len(args):
                host = args[i + 1]
                i += 2
            else:
                i += 1

        cfg = load_config(root)
        if not cfg["enabled"]:
            return 0

        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception:
            # Not JSON. Keep the bytes rather than discarding the event.
            payload = {"_unparsed_stdin": raw[:4096]}
        if not isinstance(payload, dict):
            payload = {"_non_object_stdin": payload}

        record = build_record(payload, event, host, cfg)

        session = str(record.get("session_id") or "unknown")
        safe = "".join(c if (c.isalnum() or c in "-_") else "-"
                       for c in session)[:120] or "unknown"
        day = record["ts"][:10]
        out_dir = os.path.join(root, "sessions", day)
        os.makedirs(out_dir, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, default=str)
        with open(os.path.join(out_dir, safe + ".jsonl"), "a",
                  encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception as exc:  # noqa: BLE001 - deliberate catch-all
        log_error(root, f"{type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    # Exit status is hardcoded: a recorder must never be able to block a host.
    sys.exit(main())
