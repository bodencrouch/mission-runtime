# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mission-runtime** is a Claude Code plugin that implements an intent-first autonomous engineering runtime. It lets Claude take ownership of outcome-shaped missions ("make this reliable", "improve performance") rather than bounded tasks, keeping persistent state on disk across sessions and delegating bounded work to specialist agents.

Core mechanism: recover the need behind the user's words, write an operating contract, run a persistent control loop (interpret → inspect → model → queue → execute → verify → update memory → generate follow-ups → replan), verify with evidence, and stop only on a substantive condition — including an honest declaration of failure when no route remains.

Product grounding (problem, approach, metrics, tracks) lives in `STRATEGY.md`. A telemetry layer records what each run did to `~/.missionruntime/` on local disk; see Telemetry Subsystem below.

## The prompt surfaces are the product

Almost everything in this repo is instructions: skills, reference docs, agent definitions, and this file. `docs/prompt-style.md` is the standard for writing and editing any of them — instruction framing, altitude, register, structure, layering, and the per-change verification checklist. Read it before editing any `.md` file under `skills/` or `agents/`, and hold changes to its rules.

## Architecture

### Skills (`skills/` directory)

Four skills, each `skills/<name>/SKILL.md` with frontmatter `name`, `description` (the trigger surface — concrete quoted phrases, third person), and `metadata.version` (kept equal to the plugin version):

- **mission** — the orchestrator: intake (need-behind-the-ask diagnosis, message normalization, contract, readback), the control loop, delegation, verification, the question gate, communication rules, stopping. Its eight reference docs live in `skills/mission/references/` and are each linked once from the SKILL.md body:
  - `intent-contract.md` — need diagnosis, message-normalization repair table, evidence hierarchy, confidence tiers, contract template, readback, the canonical question gate (question packets with silence-defaults).
  - `control-loop.md` — loop stages with consequence-proportional ceremony, prioritization, parallelism and conflict control, stall detection, context management, budgets.
  - `amendment.md` — mid-mission directives: ledger-first landing, four-verdict triage, blast-radius sweep, effect boundary.
  - `delegation.md` — roster, the work packet (context-first ordering, deliverable type, scope fence, progress-grounding), dispatch rules, the falsifiable integration protocol.
  - `memory.md` — `.mission/` ledger schemas and the resumption protocol (capsule freshness, orphan demotion, HEAD-anchor reconciliation).
  - `verification.md` — tiered verification depth, the evidence standard, independent review routing, the problem-id circuit breaker (three attempts, then stop-and-choose).
  - `stopping.md` — continuation review, stopping conditions, stop-as-decision, failure reports, the final report template.
  - `telemetry.md` — the two capture paths, the fallback record shape, privacy controls, the recorder's three rules.
- **mission-resume** — reload `.mission/`, reconcile against repo reality, re-enter the loop without re-asking anything.
- **mission-status** — declarative progress or final report from the ledgers, anchored on the capsule's Reported-through timestamp; never a permission request.
- **mission-telemetry** — report recorded run data, check that recording works (doctor first, always), change telemetry settings.

### Agents (`agents/` directory)

Nine specialists, one `.md` each, frontmatter `name`, `description` (plain prose: capability, trigger scenarios, when-not-to — no example transcripts), `model: inherit`, `color` (from the documented set: red, blue, green, yellow, purple, orange, pink, cyan), and `tools` — **always declared, least privilege, no `Agent`** (specialists must not sub-delegate). Bodies are second person: role → "When to invoke" → method → discipline → required report format.

- Read-only by charter (report returned as final message; orchestrator saves it to `.mission/notes/`): **repo-cartographer**, **research-analyst**, **security-reviewer**, **code-quality-reviewer**, **regression-investigator**, **adversarial-critic**. Four of these hold Bash for read-only inspection; the charter and tools list together are the enforcement.
- Writers (save their own note file, return a terse summary): **implementation-engineer**, **test-engineer** (both: Read, Grep, Glob, Bash, Write, Edit), **docs-writer** (docs files only).

Falsification routing: broken behavior → regression-investigator; code quality → code-quality-reviewer; a completion claim or the ledgers → adversarial-critic.

## Telemetry Subsystem

This is where the plugin's executable code lives; the rest of the repo is markdown and JSON. Records live in `~/.missionruntime/` — outside any repo, shared across hosts and projects — and are never transmitted. Design rationale: `skills/mission/references/telemetry.md`.

### Scripts (`scripts/` directory)

- **mr_record.py** — the recorder. Reads one host hook payload from stdin, derives a normalized view (session id, cwd, tool name, agent type, durations, status) using per-field candidate name lists, retains the whole raw payload so a host renaming a field does not destroy old data, and appends one NDJSON line to `~/.missionruntime/sessions/<YYYY-MM-DD>/<session-id>.jsonl`. It marks a record `mission_active` when the event's cwd contains a `.mission/` directory — the flag the benchmark comparison is built on. It exits 0 on every path and swallows its own errors to `~/.missionruntime/recorder.err`, because hosts treat a non-zero exit on several events as "block this action".
- **mr_report.py** — aggregates the NDJSON into per-session rows, then compares mission sessions against non-mission ones. Flags: `--days N`, `--sessions`, `--json`. Reports cost only (wall-clock, tool calls, prompts, subagent counts) and explicitly declines to score value.
- **mr_doctor.py** — checks whether recording is actually happening: interpreter, recorder runs, config and env switches, `hooks/hooks.json` parses, which hosts are wired, store size and freshness, recorder error log. Exits 1 when it finds a problem.
- **mr_install_hooks.py** — renders a host hook template with an absolute recorder path and writes it to that host's config location. `--host cursor|copilot|codex`, `--scope user|project`, `--apply`. Dry run by default; backs up an existing target. Claude Code never needs this.

### Hook configs (`hooks/` directory)

- **hooks.json** — Claude Code; loaded from the plugin automatically. Wires SessionStart, UserPromptSubmit, PreToolUse (matchers `Agent|Task` → SubagentSpawn and `Skill` → SkillInvoke), SubagentStart, SubagentStop, PostToolUse, Stop, SessionEnd. Every hook sets `suppressOutput: true`; all are `async: true` except SessionEnd (`timeout: 5`), because an async hook is not guaranteed to finish during teardown. A test enforces that split; changing it needs a reason.
- **cursor.json**, **copilot.json**, **codex.json** — templates for other hosts with `__MR_CMD__` as the recorder placeholder. Written from vendor documentation and untested against live hosts; treat as unproven.

### Configuration

Environment variables beat the config file. Defaults live in `DEFAULT_CONFIG` in `mr_record.py`.

- `MISSIONRUNTIME_TELEMETRY=off` — record nothing.
- `MISSIONRUNTIME_REDACT=1` — replace text with a length plus a short digest, and drop the raw payload whole rather than filtering it.
- `MISSIONRUNTIME_HOME=<path>` — relocate the store. `mr_record.py`, `mr_report.py`, and `mr_doctor.py` honor it (this is how the tests stay out of a real store). `mr_install_hooks.py` does not read it.
- `~/.missionruntime/config.json` — optional: `enabled`, `redact_text`, `max_text_chars`, `capture_tool_io`, `max_payload_bytes`. A malformed file falls back to defaults.

Prompts and tool inputs are captured in full by default — a deliberate trade-off documented in `skills/mission/references/telemetry.md`, and why the off switch and redaction switch must keep working.

### Tests (`tests/` directory)

Two suites, run together. Run exactly:

```
python3 -m unittest discover -s tests
```

- `tests/test_telemetry.py` covers the properties the telemetry subsystem may not lose: recorder exits 0 on hostile input, unwritable store, path-traversal session ids; host dialects normalize to the same fields; config/env switches take effect and env wins; the report survives corrupt lines and empty stores; hook configs parse, reference the recorder, and stay async; the installer renders valid JSON and backs up what it replaces. Tests point `MISSIONRUNTIME_HOME` at a temp directory.
- `tests/test_runtime_conformance.py` mechanically enforces the style guide on the markdown runtime: skill/agent frontmatter shape, description length and person, `metadata.version` == plugin version, SKILL.md line ceiling, every reference linked from the mission SKILL.md exactly once, agent `tools` declared least-privilege (read-only set excludes write tools; no `Agent` anywhere), prose descriptions, valid colors, delegation roster completeness, the four hazard-pattern greps, and manifest description/version parity.

## Working With This Codebase

### Editing skills, agents, or references

1. Read `docs/prompt-style.md` first; it carries the rules and the sources behind them.
2. Skill descriptions keep their concrete trigger phrases — they are what makes discovery work. Agent `tools` stay least-privilege. Names never change casually: skill directory names and agent file names are the discovery surface.
3. Run the checklist in the style guide's "Checking a prompt change" section: the unittest suite, hazard greps, cross-reference resolution, terminology.
4. Loop semantics changes go to `skills/mission/SKILL.md` and `skills/mission/references/control-loop.md` together, then get exercised with a full mission cycle.

### Changing the recorder or a hook config

1. Field names are added to the candidate lists in `FIELD_ALIASES`, `TEXT_ALIASES`, `TOOL_RESULT_ALIASES`, or `TOOL_INPUT_ALIASES` — never swapped for a single "correct" name, because host schemas change between releases.
2. Run the test suite, then `python3 scripts/mr_doctor.py`; the recorder must still exit 0 and the hook configs must still parse.
3. If the record shape changed, update `skills/mission/references/telemetry.md` — it tells the fallback path what to write, and the two capture paths must aggregate together.

## Key Design Decisions

- **Model-agnostic surfaces**: the runtime must produce good results on whatever model and host the user has, from whatever phrasing the user writes. Prompt surfaces specify outcomes, invariants, authority, and evidence — never a fixed route, and never a particular model's compensations as standing rules; host capabilities are referenced conditionally, with the `.mission/` ledgers as the universal fallback. The rules live in `docs/prompt-style.md` ("Model portability").
- **Persistent control loop, not one-shot**: stopping is explicit and evidence-based; every stop writes a decision naming its condition.
- **The need governs, the words inform**: intake recovers the problem behind the request; normalization repairs a message's form, never its content; every non-obvious reading is logged and surfaced in the readback.
- **Durable memory on disk**: the conversation is a cache; the `.mission/` ledgers are the database. Mid-mission directives always land in the ledger before triage.
- **Orchestrator is single owner**: subagent reports are validated against a falsifiable bar (file:line spot-checks, rerunnable commands), then integrated or rejected.
- **Default to action, questions as packets**: reversible evidence-backed choices are made and logged; a rare surviving question ships with options, a recommended default, and its silence behavior.
- **Verification as gate, scaled to consequence**: tests for everything; sibling sweeps and independent review for consequential changes; adversarial audit at completion; three materially different attempts per problem, then stop-and-choose.
- **Telemetry never blocks and never leaves the machine**: the recorder exits 0 on every path; records go to local disk only. Full-text capture by default makes the off and redaction switches load-bearing.

## Plugin Installation and Metadata

- Plugin definition: `.claude-plugin/plugin.json` (name, version, description, author, license, keywords, repository).
- Marketplace definition: `.claude-plugin/marketplace.json` — repeats the plugin description and adds `source: "./"`, `category`, `tags`. The two files duplicate the description on purpose; change it in both. Version lives only in plugin.json.
- Skill `metadata.version` fields track the plugin version; bump them together.
- Skills register by directory name under `skills/`; agents by file name under `agents/`; hooks load from `hooks/hooks.json` with no user configuration.

## Dependencies

No npm packages, no build step, no external APIs, no network calls. The plugin is markdown, JSON manifests, and Python 3 scripts importing only the standard library. Python 3 was chosen over bash+jq because jq is absent by default on macOS and minimal Linux images, and a missing jq would make the recorder silently record nothing — the worst failure mode for telemetry. Adding a third-party dependency to these scripts is a contract change, not a refactor.
