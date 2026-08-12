---
name: mission-telemetry
description: >
  This skill should be used when the user asks about mission-runtime telemetry,
  benchmarking, or measurement — phrases like "is mission-runtime worth it",
  "how much did that mission cost", "benchmark the runtime", "show mission
  stats", "what did the agents do", "turn telemetry off", "stop recording my
  prompts", "where is the telemetry stored", or "/mission-telemetry". It reports
  recorded run data, checks that recording is actually working, and changes the
  telemetry configuration.
metadata:
  version: "0.4.0"
---

# Mission Telemetry

Report and configure the run records the runtime writes to `~/.missionruntime/`.
Full design in `${CLAUDE_PLUGIN_ROOT}/skills/mission/references/telemetry.md`.

## 1. Establish what is actually being recorded

Answer from the doctor, never from assumption — an empty store and a broken
recorder look the same to the user. Run:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_doctor.py
```

Report plainly whether recording is on, which hosts are wired, and how fresh the
newest record is. If the doctor reports problems, fix those before showing any
numbers, and say the numbers are incomplete.

## 2. Answer the question that was asked

For "how much did this cost" or "is it worth it":

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_report.py
```

Lead with the mission vs non-mission comparison — that contrast is the whole
point. Give the ratios in plain words. Then state the limit honestly: these are
cost numbers, and cost alone cannot say whether a run was worth it.

If the store holds only mission sessions, say so and explain that a baseline
needs ordinary sessions recorded with the plugin installed.

For per-run detail use `--sessions`; for analysis use `--json`.

## 3. Offer the outcome log when cost data is not enough

If the user is trying to decide whether the runtime pays for itself, point them
at `~/.missionruntime/outcomes.jsonl` and offer to append one line per mission:
verdict, what the run actually produced, and whether they would have caught it
themselves. Ten honest lines beat a thousand event records for this question.

## 4. Configuration changes

| Ask | Do |
|---|---|
| Turn recording off | Set `enabled: false` in `~/.missionruntime/config.json`, or export `MISSIONRUNTIME_TELEMETRY=off` |
| Stop storing prompt text | Set `redact_text: true`, or export `MISSIONRUNTIME_REDACT=1` |
| Stop storing tool inputs | Set `capture_tool_io: false` |
| Move the store | Export `MISSIONRUNTIME_HOME=<path>` |
| Delete history | Remove `~/.missionruntime/sessions/` — confirm the path with the user first, then delete |
| Wire another host | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_install_hooks.py --host cursor\|copilot\|codex --apply` |

Environment variables beat the config file. After changing the config, re-run
the doctor and show the result rather than asserting it took effect.

Deleting records is irreversible. Name the exact path and wait for confirmation.

## 5. Boundaries

Three rules hold because the data is only trustworthy while they do. Never
write telemetry records by hand while hooks are recording — duplicates corrupt
every count. Never read `~/.missionruntime/` to reconstruct past conversations
for the user — it exists to measure the runtime, not to serve as a searchable
history. Never send any of it anywhere — the store is local by contract.
