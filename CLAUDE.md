# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**mission-runtime** is a Claude plugin that implements an intent-first autonomous engineering runtime. It enables Claude to take ownership of outcome-shaped missions (e.g., "make this reliable", "improve performance") rather than bounded tasks, maintaining persistent state across sessions and delegating work to specialist agents.

The system's core philosophy: reconstruct user intent from sparse input, write an operating contract that states assumptions and constraints, execute a persistent control loop (interpret → inspect → model → queue → execute → verify → learn → replan), delegate to specialists, and stop only on evidence-backed substantive conditions.

A telemetry layer records what each run did to `~/.missionruntime/` on local disk, so the runtime's cost can be measured rather than guessed at. See Telemetry Subsystem below.

## Architecture

### Skills (`skills/` directory)

Four skills implement the runtime:

- **mission** (`skills/mission/SKILL.md`) — The orchestrator. Handles intake (intent reconstruction → operating contract), persistent control loop management, delegation to agents, memory updates, and stopping policy. Runs the cycle: interpret → inspect → model → build queue → execute → verify → update memory → generate follow-ups → replan. Reference docs in `skills/mission/references/` cover the contract template, memory schema, loop mechanics, delegation protocol, verification strategy, stopping conditions, and telemetry.

- **mission-resume** (`skills/mission-resume/SKILL.md`) — Reload `.mission/` state in new sessions, reconcile against repo reality, and re-enter the loop without re-asking anything. Used when continuing a previous mission.

- **mission-status** (`skills/mission-status/SKILL.md`) — Declarative progress or final report from the ledgers, never a permission request. Shows what's done, active, blocked, and what's next.

- **mission-telemetry** (`skills/mission-telemetry/SKILL.md`) — Reports the recorded run data, checks that recording is working, and changes the telemetry settings. Runs `scripts/mr_doctor.py` before quoting numbers, because an empty store and a broken recorder look identical.

### Agents (`agents/` directory)

Specialist agents handle bounded work packets dispatched by the orchestrator:

- **repo-cartographer** — Maps repo layout, dependencies, test structure, deployment config, and conventions. Read-only inspection work run early in a mission.

- **implementation-engineer** — Executes a decided plan within explicit file scope. Implements changes, adds regression tests, verifies locally. Bounded by architecture decision already made.

- **test-engineer** — Builds regression tests, verifies fixes, runs test suite, checks coverage. Gets a decided fix or hypothesis and proves it.

- **security-reviewer** — Audits code for auth, permission checks, input validation, secrets leakage, and injection vectors. Read-only diagnosis.

- **code-quality-reviewer** — Reviews for maintainability, complexity, naming, duplication, type safety, dead code. Read-only.

- **regression-investigator** — Reproduces failures, identifies root cause, traces through relevant code. Diagnoses before fix is attempted.

- **docs-writer** — Drafts or updates documentation and README sections. Scoped to specific doc files.

- **research-analyst** — Researches external libraries, best practices, design patterns, and prior art. Gathers external grounding for architectural decisions.

- **adversarial-critic** — Challenges assumptions and decisions, tries to break implementations, surfaces edge cases and risks. Final independent audit gate.

## Persistent Memory System

`.mission/` directory at project root holds the runtime's persistent state (kept out of VCS via `.git/info/exclude`). This survives session death and context compaction.

### Key Files

- **mission.md** — Operating contract (write once, amend rarely). States: mission outcome, scope, constraints, authority tiers, quality bar, evidence standard, communication rules, stopping policy.

- **state.md** — Resume capsule (rewrite frequently). Compact snapshot of project model, completed work, active task, assumptions in force, blockers, risks, next action. Read first on session reload.

- **queue.md** — Work ledger (append-only log of work). Sections: Pending (priority-ordered with trace to mission), Active, Blocked, Deferred, Done. Each entry links to why it matters.

- **decisions.md** — Decision log. Records what was chosen, evidence considered, alternatives, reversibility. Build institutional memory.

- **assumptions.md** — Register of provisional assumptions with confidence levels. Separate from facts so they don't calcify.

- **attempts.md** — Attempt history. What was tried, why it failed, what that teaches. Prevents circular retry.

- **verification.md** — Verification ledger. Test commands run, results, evidence of fixes, regression tests added, suite runs. Claims of success require observable data.

- **notes/** — Agent reports and technical details. Implementation notes, test results, findings outside scope, risks.

## Telemetry Subsystem

This is where the plugin's executable code lives; the rest of the repo is markdown and JSON. It records what each run did so the runtime can be benchmarked. Records live in `~/.missionruntime/` — outside any repo, shared across hosts and projects — and are never transmitted. Design rationale is in `skills/mission/references/telemetry.md`.

### Scripts (`scripts/` directory)

- **mr_record.py** — The recorder. Reads one host hook payload from stdin, derives a normalized view (session id, cwd, tool name, agent type, durations, status) using per-field candidate name lists, retains the whole raw payload so a host renaming a field does not destroy old data, and appends one NDJSON line to `~/.missionruntime/sessions/<YYYY-MM-DD>/<session-id>.jsonl`. It marks a record `mission_active` when the event's cwd contains a `.mission/` directory — the flag the benchmark comparison is built on. It exits 0 on every path and swallows its own errors to `~/.missionruntime/recorder.err`, because hosts treat a non-zero exit on several events as "block this action".

- **mr_report.py** — Aggregates the NDJSON into per-session rows, then compares mission sessions against non-mission ones. Flags: `--days N`, `--sessions` (per-session table), `--json`. Reports cost only (wall-clock, tool calls, prompts, subagent counts) and explicitly declines to score value.

- **mr_doctor.py** — Checks whether recording is actually happening: interpreter, recorder runs, config and env switches in force, `hooks/hooks.json` parses, which other hosts are wired, store size and freshness, recorder error log. Exits 1 when it finds a problem.

- **mr_install_hooks.py** — Renders a host hook template with an absolute path to the recorder and writes it to that host's config location. `--host cursor|copilot|codex`, `--scope user|project`, `--apply`. Dry run by default; backs up an existing target before replacing it. Claude Code never needs this.

### Hook configs (`hooks/` directory)

- **hooks.json** — Claude Code. Loaded from the plugin automatically, no install step. Wires SessionStart, UserPromptSubmit, PreToolUse (matchers `Agent|Task` → SubagentSpawn and `Skill` → SkillInvoke), SubagentStart, SubagentStop, PostToolUse, Stop, SessionEnd. Every hook sets `suppressOutput: true`, and all of them are `async: true` except SessionEnd, which uses `timeout: 5` because an async hook is not guaranteed to finish as the session tears down. A test enforces that split; changing it needs a reason.

- **cursor.json**, **copilot.json**, **codex.json** — Templates for the other hosts, with `__MR_CMD__` as the recorder placeholder that `mr_install_hooks.py` substitutes. Written from vendor documentation and not yet tested against a live host; treat them as unproven.

### Configuration

Environment variables beat the config file. Defaults live in `DEFAULT_CONFIG` in `mr_record.py`.

- `MISSIONRUNTIME_TELEMETRY=off` — record nothing.
- `MISSIONRUNTIME_REDACT=1` — replace text with a length plus a short digest, and drop the raw payload whole rather than filtering it.
- `MISSIONRUNTIME_HOME=<path>` — relocate the store. `mr_record.py`, `mr_report.py`, and `mr_doctor.py` honor it, which is how the tests stay out of a real store. `mr_install_hooks.py` does not read it; it only writes host configs.
- `~/.missionruntime/config.json` — optional: `enabled`, `redact_text`, `max_text_chars`, `capture_tool_io`, `max_payload_bytes`. A malformed file falls back to defaults instead of failing.

Prompts and tool inputs are captured in full by default. That is a deliberate trade-off, documented in `references/telemetry.md`, and it is why the off switch and the redaction switch have to keep working.

### Tests (`tests/` directory)

`tests/test_telemetry.py` covers the properties the subsystem is not allowed to lose: the recorder exits 0 on hostile input, an unwritable store, and a path-traversal session id; host dialects (Claude, Cursor, Copilot) normalize to the same fields; the config and env switches take effect and env wins; the report survives a corrupt line and an empty store; the shipped hook configs parse, reference the recorder, and stay async; and the installer renders valid JSON and backs up what it replaces. Tests that write records point `MISSIONRUNTIME_HOME` at a temporary directory, so running them does not touch a real store. Run:

```
python3 -m unittest discover -s tests
```

## Control Loop and Task Execution

### One Cycle Looks Like

1. Load `.mission/mission.md` (the contract is the fixed point)
2. Gather evidence via inspection (delegate repo scan, analysis work concurrently)
3. Update project model in `.mission/state.md` (facts, unknowns, risks, components)
4. Turn mission + evidence into prioritized tasks in `.mission/queue.md` with traceability
5. Execute highest-value unblocked task (do directly or delegate per scope and expertise)
6. Verify work (reproduce → root cause → test → regression sweep → if consequential, adversarial audit)
7. Update ledgers with results, new facts, new tasks, changed priorities
8. Generate follow-up work from continuation questions in `references/stopping.md`
9. Replan: is the current plan still best? Any stalls?
10. Continue loop or fire stopping policy

### Prioritization

Never FIFO. Weigh: mission relevance, user impact, severity, diagnostic confidence, expected improvement, evidence value (uncertainty reduction?), risk, reversibility, cost, dependency position (blocks other work?), and parallelism.

### Delegation Pattern

Each agent packet includes: objective, context, scope, constraints, evidence standard, required report format. Examples:

- "Map the codebase" → repo-cartographer
- "Diagnose why startup is slow" → regression-investigator (read-only trace through code + timing)
- "Implement the agreed fix to X" → implementation-engineer (bounded scope, one file or disjoint set)
- "Build a regression test for Y" → test-engineer

Read-only work (inspect, diagnose, research, review) runs in parallel. Writers get non-overlapping file scopes or explicit merge strategy.

## Reference Documentation

Key design documents in `skills/mission/references/`:

- **intent-contract.md** — Contract template. Reconstructing intent from evidence hierarchy (explicit words → prior conversation → docs → repo structure → conventions → safe defaults). Separating explicit requirements, implications, constraints, assumptions, decisions.

- **control-loop.md** — Loop mechanics, prioritization heuristics, parallelism rules, conflict avoidance for concurrent writers, stall detection.

- **delegation.md** — Bounding work packets, reporting structure, orchestrator's validation gate for subagent findings, reconciliation of conflicts.

- **verification.md** — Verification as completion gate. Reproduce → root cause → prove fix with test → run suite → regression sweep → for high-consequence changes, adversarial audit. Evidence standards.

- **stopping.md** — Continuation review questions after each deliverable (unverified assumptions?, untested edges?, regressions?, docs stale?, unnecessary complexity?, flaky tests?). Stopping conditions: acceptance criteria met + clean review, remaining work low-value, diminishing returns, budget, irreducible human dependency.

- **memory.md** — Ledger schema and append-only practices. When to create, update, and read `.mission/` files.

- **telemetry.md** — What the runtime records and why. The two capture paths (host hooks primary, skill-written records as a degraded fallback), how to tell which one is live, the record shape the fallback must match, the privacy trade-off and its controls, and the three rules the recorder may not break (never block, never guess a schema, never phone home).

## Working With This Codebase

### For New Skill or Agent Development

1. Create a new `.md` file with frontmatter. Skills go in `skills/<skill-name>/SKILL.md` and carry `name`, `description`, and `metadata` (which holds `version`). Agents go in `agents/<agent-name>.md` and carry `name`, `description`, `model`, `color`, and `tools`. Seven of the nine agents declare `tools` explicitly; `implementation-engineer` and `test-engineer` leave it out. Declare it — a read-only reviewer that can write is a reviewer that can break its own contract.
2. Frontmatter triggers: when should this skill/agent be used? The name determines when Claude Code recognizes and invokes it.
3. Agent body: system prompt that defines behavior, constraints, reporting format.
4. Skills include reference docs (in `skills/skill-name/references/`) when architecture is complex (state machines, ledgers, delegation protocols).
5. Keep instructions focused and actionable: hard rules, deliverable format, scope boundaries.

### Testing a Skill or Agent

1. Create a test mission or task that exercises the skill/agent.
2. Verify the contract is written correctly if it's a skill.
3. Check that delegation packets are well-formed.
4. Verify agent reports follow the expected format and answer the objective.
5. Read the ledgers to confirm memory updates are correct and traceability is intact.

### Editing the Runtime Control Loop

The control loop lives in `skills/mission/SKILL.md` (phases: Intake, Control Loop stages, Delegation, Verification, Default-to-Action, Communication, Stopping). Changes here are high-impact:

- Update the loop stages in the SKILL.md body
- Update supporting docs in `references/` if loop semantics change
- Test with a full mission cycle to verify no infinite loops or stalls
- Check that ledger updates still make sense with new loop stages

### Common Scenarios

**Adding a new specialist agent:**

1. Write `agents/new-agent-name.md` with frontmatter and system prompt.
2. In `skills/mission/references/delegation.md`, add an example work packet for this agent.
3. In `skills/mission/SKILL.md`, reference the new agent in the Delegation section.
4. Test by delegating to it in a real mission cycle.

**Changing the stopping policy:**

1. Edit `skills/mission/references/stopping.md` (continuation questions, stopping conditions).
2. Update the loop in `skills/mission/SKILL.md` to call the new stopping logic.
3. Test by running a mission to completion and verifying it stops at the right point.

**Fixing memory corruption or ledger bugs:**

1. Check `.mission/queue.md` and `.mission/state.md` format in `references/memory.md`.
2. Update the ledger schema if format changes.
3. Add a migration step in `mission-resume` skill if old `.mission/` directories need updating.

**Changing the recorder or a hook config:**

1. Edit `scripts/mr_record.py` or the config in `hooks/`. Field names are added to the candidate lists in `FIELD_ALIASES`, `TEXT_ALIASES`, `TOOL_RESULT_ALIASES`, or `TOOL_INPUT_ALIASES` — never swapped for a single "correct" name, because host schemas change between releases.
2. Run `python3 -m unittest discover -s tests`.
3. Run `python3 scripts/mr_doctor.py` and confirm the recorder still exits 0 and the hook configs still parse.
4. If the record shape changed, update `skills/mission/references/telemetry.md`, which tells the fallback path what to write. The two must stay in sync or the two capture paths stop aggregating together.

## Key Design Decisions

- **Persistent control loop, not one-shot**: Stopping is explicit and evidence-based, not "first plausible answer".
- **Durable memory on disk**: Survives session death, context compaction, multi-day gaps. Conversation is a cache; ledgers are the database.
- **Orchestrator is single owner**: Subagent reports are validated and reconciled, not dumped. One accountable entity.
- **Default to action**: Safe, reversible, evidence-supported choices are made; questions pass a strict gate and only after independent work is done.
- **Verification as gate**: Unverified work doesn't count. Reproduce, root-cause, test, regression sweep, (if high-consequence) adversarial audit.
- **Delegation by scope**: Each agent touches only its packet's files. Discovering out-of-scope findings is reported, not acted on silently.
- **Telemetry never blocks**: The recorder exits 0 on every path, and every Claude Code recording hook but SessionEnd is `async`. A broken recorder loses data; it must not stall or block a session.
- **Telemetry never leaves the machine**: Records are written to local disk and nothing else. Prompts are captured in full by default, so the off switch and the redaction switch are load-bearing, not optional extras.

## Plugin Installation and Metadata

- Plugin definition: `.claude-plugin/plugin.json` (name, version, description, author, license, keywords).
- Marketplace definition: `.claude-plugin/marketplace.json` — the manifest a marketplace reads. It repeats the name, description, and author, and adds `source` (`"./"`, this repo), `category`, and `tags`. The two files duplicate the description, so a wording change has to be made in both.
- Skills are registered by directory name under `skills/`, each holding a `SKILL.md`.
- Agents are registered by `.md` file name in the `agents/` directory.
- Hooks come from `hooks/hooks.json`, which Claude Code loads from the plugin without any user configuration.
- Claude Code discovers and invokes skills and agents based on the frontmatter `name:` and trigger conditions in the description.

## Dependencies

No npm packages, no build step, no external APIs, no network calls. The plugin is markdown, JSON manifests, and Python 3 scripts.

The one runtime requirement is Python 3 for the telemetry scripts in `scripts/`, which import only the standard library — no pip install. Python 3 was chosen over bash plus jq because jq is absent by default on macOS and on minimal Linux images, and a missing jq would make the recorder silently record nothing — the worst failure mode for a telemetry component. Adding a third-party dependency to these scripts is a contract change, not a refactor.
