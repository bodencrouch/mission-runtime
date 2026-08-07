# mission-runtime

An intent-first autonomous engineering runtime for Claude. Give it a job, not
a task list: state a broad outcome ("make Linux setup solid", "improve this
app's performance", "take ownership of reliability") and the runtime
reconstructs your intent, writes its own operating contract, plans and
prioritizes the work, delegates to specialist subagents, verifies its own
output, and keeps generating mission-traceable follow-up work until a
substantive stopping condition is reached — not until the first plausible
answer.

## What it changes about Claude's behavior

- **Mission over task**: outcome-shaped requests are interpreted as
  delegation of responsibility, implicitly authorizing investigation,
  prioritization, implementation, testing, review, docs, and follow-up.
- **Default to action**: safe, reversible, evidence-supported choices are
  made and logged, never bounced back as questions. Questions pass a strict
  gate (irreversible, credential, legal/security authority, or materially
  conflicting requirements — and only after all independent work is done).
- **Persistent control loop**: interpret → inspect → model → queue → execute
  → verify → learn → replan, until the stopping policy fires.
- **Durable memory**: a `.mission/` directory at the project root holds the
  contract, resume capsule, work ledger, decision log, assumption register,
  attempt history, and verification ledger. Missions survive context
  compaction, session death, and multi-day gaps. (Kept out of your VCS via
  `.git/info/exclude`; your `.gitignore` is never touched.)
- **Supervised specialists**: subagents report evidence to the orchestrator,
  which validates, reconciles, and integrates — one accountable owner, no
  transcript dumps.
- **Verification as completion**: reproduce → root-cause → fix → regression
  test → suite → sibling sweep → independent adversarial audit for anything
  consequential.
- **Real stopping policy**: quiescence on evidence-backed completion,
  diminishing returns, budget, or an irreducible human dependency — always
  with a final state report (accomplished, verified, assumed, unresolved,
  next worthwhile work).

## Components

**Skills**

- `mission` — intake (the "introducer": sparse-intent reconstruction →
  operating contract) plus the persistent control loop. Reference docs cover
  the contract template and evidence hierarchy, the loop and prioritization,
  the memory schema, the delegation protocol, verification and failure
  recovery, continuation/stopping policy, and the telemetry design.
- `mission-resume` — reload `.mission/` in any later session, reconcile
  against repo reality, and re-enter the loop without re-asking anything.
- `mission-status` — declarative progress or final report from the ledgers;
  never a disguised permission request.
- `mission-telemetry` — report the recorded run data, check that recording is
  working, and change the telemetry settings.

**Agents**

repo-cartographer, research-analyst, implementation-engineer, test-engineer,
security-reviewer, code-quality-reviewer, regression-investigator,
docs-writer, adversarial-critic. Reviewers and investigators are
read-only/diagnose-only by design; writers carry bounded file scopes.

## Usage

Say what you want to be true:

- "Take ownership of this repository and make its Linux installation and
  startup experience reliable."
- "Make it fast."
- "Get this service production-ready."

Then let it run. Check in anytime with "mission status"; continue a previous
session with "resume the mission". Redirect at will — your messages amend the
contract; silence means "continue".

## Telemetry

Every run leaves a record on disk, so the runtime's cost can be measured
instead of guessed at.

**Read this first.** Your prompts and tool inputs are recorded in full by
default. Records are written to `~/.missionruntime/` on your own machine.
Nothing is transmitted anywhere. `MISSIONRUNTIME_TELEMETRY=off` stops
recording. Redaction and a config file are described below.

**How it records.** Claude Code loads `hooks/hooks.json` from the plugin, so
recording starts with no setup. On each hook event the host runs
`scripts/mr_record.py`, which reads the payload on stdin, derives a normalized
view of the fields that matter for benchmarking, and appends one JSON line to
`~/.missionruntime/sessions/<date>/<session-id>.jsonl`. The recorder exits 0 on
every path — including malformed input and write failures — because several
hook events treat a non-zero exit as "block this action". Errors go to
`~/.missionruntime/recorder.err` instead.

**When hooks cannot run.** If the host has hooks disabled — `disableAllHooks`,
enterprise policy, `--bare` mode, an unsupported host — the runtime writes its
own records instead. That path carries no tool-level data and depends on the
model remembering to write, so read those sessions as incomplete, not as cheap.

**Reading the data.** Ask for it in plain words — "show mission stats", "how
much did that mission cost" — and the `mission-telemetry` skill runs the
commands. Or run them yourself from the plugin directory:

```
python3 scripts/mr_report.py             # summary
python3 scripts/mr_report.py --sessions  # one row per session
python3 scripts/mr_report.py --json      # machine-readable
python3 scripts/mr_report.py --days 7    # last 7 days only
```

The report separates mission sessions from ordinary ones, and that comparison
is the benchmark. A session counts as a mission when a `.mission/` directory
exists in the working directory at the time of the event. The numbers are cost
only — wall-clock, tool calls, prompts, subagent counts — and the report says
so rather than claiming a verdict.

With no store on disk yet, the report prints where it looked and points you at
the doctor.

**Checking that it works.** An empty store and a broken recorder look the same
from the outside, so ask:

```
python3 scripts/mr_doctor.py
```

It reports the interpreter, whether the recorder runs, which config and
switches are in force, which hosts are wired, and how old the newest record is.
It exits non-zero when it finds a problem.

**Turning it down or off.** Environment variables win over the config file.

- `MISSIONRUNTIME_TELEMETRY=off` — record nothing.
- `MISSIONRUNTIME_REDACT=1` — store a length and a short digest instead of the
  text. The raw payload is dropped whole rather than filtered.
- `MISSIONRUNTIME_HOME=<path>` — move the store.
- `~/.missionruntime/config.json` — optional file with the keys `enabled`,
  `redact_text`, `max_text_chars`, `capture_tool_io`, and `max_payload_bytes`.
  A malformed file falls back to defaults rather than failing.

To delete history, remove `~/.missionruntime/sessions/`.

**Other hosts.** Claude Code is the host this was built and exercised against.
Hook configs for Cursor, Copilot, and Codex ship in `hooks/`, written from each
vendor's documentation but not yet tested against a live host — treat them as
unproven. Install one with:

```
python3 scripts/mr_install_hooks.py --host cursor --apply
```

Without `--apply` the script prints its plan and writes nothing. It backs up
any file already at the target before replacing it.

## Setup

Installing the plugin requires no setup for Claude Code: no MCP servers, no
build step, no packages to install. State a mission and it runs.

Telemetry also works out of the box on its defaults, and records to
`~/.missionruntime/`. Nothing below is required:

- `MISSIONRUNTIME_TELEMETRY`, `MISSIONRUNTIME_REDACT`, and
  `MISSIONRUNTIME_HOME` change what is recorded and where.
- `~/.missionruntime/config.json` sets the same options in a file.

See Telemetry above for what each one does.

The telemetry scripts need Python 3 and import only the standard library.
