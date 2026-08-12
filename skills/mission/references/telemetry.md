# Telemetry: Recording What the Runtime Did

## Contents

- [Two capture paths](#two-capture-paths)
- [Detecting which path is live](#detecting-which-path-is-live)
- [The fallback record](#the-fallback-record)
- [Reading the data](#reading-the-data)
- [Scoring a run](#scoring-a-run)
- [Privacy](#privacy)
- [Rules the recorder must keep](#rules-the-recorder-must-keep)

The runtime is expensive to run and hard to judge. Telemetry exists to answer
one question with data instead of impression: **what did a mission cost, and
what did it produce?**

Records go to `~/.missionruntime/` — outside any repo, shared across every host
and project, so runs can be compared. Nothing is ever transmitted anywhere.

## Two capture paths

**Hooks (primary).** The host calls `scripts/mr_record.py` on lifecycle events
and it appends a record. This is automatic and does not depend on the model
remembering anything — which matters most on the runs that go badly, exactly
the runs worth studying. Claude Code loads `hooks/hooks.json` from the plugin
with no setup. Cursor, Copilot, and Codex need
`scripts/mr_install_hooks.py --host <name> --apply` once.

**Skill-driven (fallback).** When hooks are unavailable — `disableAllHooks`,
enterprise policy, `--bare` mode, or an unsupported host — the runtime writes
its own records. This path is lossy: it has no tool-level data and only fires
when the model remembers. Treat it as degraded, never as equivalent.

## Detecting which path is live

Do not assume. At mission start, run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_doctor.py
```

If it reports the store is receiving records, hooks are working and the runtime
should write nothing extra — duplicate records corrupt the counts. If it reports
no recent records, switch to the fallback below and note the degradation in
`.mission/state.md`, so nobody later reads an empty store as "cheap run".

## The fallback record

When hooks are not recording, append one JSON object per line to
`~/.missionruntime/sessions/<YYYY-MM-DD>/<session-or-mission-id>.jsonl`. Use the
same field names the recorder emits, so both paths aggregate together:

```json
{"schema":1,"ts":"<ISO8601 UTC>","event":"SubagentSpawn","host":"<host>",
 "session_id":"<id>","mission_active":true,"agent_type":"test-engineer",
 "delegated_prompt":"<the commission>","cwd":"<project root>"}
```

Write at minimum: one `UserPromptSubmit` with the mission prompt, one
`SubagentSpawn` per delegation with `agent_type` and the commission, one
`SubagentStop` per return with the distilled outcome, and one `Stop` carrying
the stopping condition in `status`. Writing these is cheap; reconstructing them
later is impossible.

The runtime may call the recorder directly rather than hand-writing JSON:

```
echo '<json>' | python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_record.py \
  --event SubagentSpawn --host fallback
```

## Reading the data

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_report.py            # summary
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_report.py --sessions # per session
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_report.py --json     # for analysis
```

The report separates mission sessions from ordinary ones — that comparison is
the benchmark. A mission session is detected by a `.mission/` directory in the
working directory at the time of the event.

## Scoring a run

The report gives cost honestly: wall-clock, tool calls, subagent count. It does
not claim a verdict, because value is not measurable from event counts. A
six-agent mission that found a real production bug and a six-agent mission that
produced a tidy summary of nothing look identical in the data.

To make runs comparable, record the outcome yourself at mission end. Append to
`~/.missionruntime/outcomes.jsonl`:

```json
{"session_id":"<id>","ts":"<ISO8601>","verdict":"worth-it|marginal|wasteful",
 "found":"<what the run actually produced>","would_have_caught_manually":true}
```

Cost data plus a one-line honest verdict per run is enough to answer "is this
worth it" after ten or twenty missions. Cost data alone never will be.

## Privacy

Prompts and tool inputs are captured in full by default, because they are the
most useful part of the record and the store is local-only. That is a real
trade-off: prompts routinely contain file contents, paths, and command lines.

Controls, in precedence order (environment beats file):

| Control | Effect |
|---|---|
| `MISSIONRUNTIME_TELEMETRY=off` | Records nothing at all |
| `MISSIONRUNTIME_REDACT=1` | Text becomes a length plus a short digest |
| `MISSIONRUNTIME_HOME=<path>` | Moves the store |
| `~/.missionruntime/config.json` | `enabled`, `redact_text`, `max_text_chars`, `capture_tool_io`, `max_payload_bytes` |

Under redaction the raw payload is dropped entirely rather than filtered — there
is no reliable list of nested keys that can hold user text across four hosts.

## Rules the recorder must keep

1. **Never block.** It exits 0 on every path. Several hook events treat a
   non-zero exit as "block this action", so a recorder that can crash is a
   recorder that can freeze a session.
2. **Never guess a schema.** Host field names differ and change between
   releases. The whole payload is retained; the normalized view is derived from
   candidate name lists.
3. **Never phone home.** Local disk only.

Changing any of these is a contract change, not a refactor.
