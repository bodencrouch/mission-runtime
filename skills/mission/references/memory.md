# Durable Project Memory (`.mission/`)

## Contents

- [Ground rules](#ground-rules)
- [Files](#files)
- [Not in `.mission/`: run telemetry](#not-in-mission-run-telemetry)
- [Resumption protocol](#resumption-protocol)

## Ground rules

Create `.mission/` at the project root on mission start. It is the runtime's
persistent brain: mission memory, work ledger, decision log, assumption
ledger, attempt history, verification ledger, and resume capsule. The
conversation window is a cache; these files are the database.

Keep it out of version control without touching the project: append
`.mission/` to `.git/info/exclude` (create the file if absent). Never commit
`.mission/`, and never edit the project's `.gitignore` for this purpose. If
there is no git repo, just use the directory.

Update ledgers as events happen, not in batches at the end — a session can
die between batches. Append-only files get new entries at the top. Rewritten
files (state.md) are replaced wholesale.

## Files

### mission.md — the operating contract (write once, amend via protocol)
Template in the intent-contract reference. Amend when the user redirects the
mission or a contract-level assumption is disproven: the directive lands
verbatim in the contract's Amendments section and the amendment is logged in
decisions.md, per the amendment reference.

### state.md — resume capsule (rewrite frequently; this is the file a cold
session reads first)

```markdown
# State — <ISO timestamp> — repo at <git HEAD sha, branch>
## Mission (one line)
## Current interpretation / plan (short)
## Project model
Facts, components, conventions, environments, risks — compact bullets.
## Completed (with evidence pointers into verification.md)
## Active
Task, owner (self/agent), current hypothesis, files in play.
## Assumptions in force (top items; full ledger in assumptions.md)
## Blockers (smallest dependent task each, and what was finished around it)
## Risks
## Reported-through (timestamp of the last user-facing update, so the next
   update states deltas from a recorded anchor, not from memory)
## Next action (exact, executable — "run X", "delegate Y to test-engineer")
```

The git HEAD anchor makes reconciliation on resume exact: `git log
<sha>..HEAD` shows precisely what changed while the runtime was away.

### queue.md — work ledger

```markdown
## Pending   (priority-ordered)
- [P1] <task> — trace: <mission link | evidence | user-directive <ts>> —
  value/cost/risk — deps: ... — parallel-safe: y/n — expertise: <agent|self>
## Active    (task — owner — files owned — started)
## Blocked   (task — exact dependency — what proceeds anyway)
   A question-gate blocker carries the question packet verbatim — evidence,
   options, recommended default, what fires on silence — so status and
   resume re-present it without re-derivation.
## Deferred  (task — why: speculative/low-value/awaiting-upstream — revisit
   when: <condition>)
## Done      (task — evidence pointer — completed)
## Canceled  (task — why)
```

### decisions.md — append-only decision log

```markdown
## <timestamp> <decision title>
Decided: ... | Why: ... | Evidence: ... | Alternatives rejected: ... |
Reversibility: ... | Follow-up verification: ...
```

Contract amendments and non-obvious message readings ("read X as Y because
Z") are decision entries too.

### assumptions.md — assumption ledger

```markdown
## <id> <statement>
Source: inferred/repo/default | Confidence: high/med/low |
Impact if wrong: ... | Verification method: ... |
Status: unverified/confirmed/refuted (+ where)
```

Refuted assumptions trigger queue review: retire or rework dependent tasks.

### attempts.md — append-only attempt history (anti-circling)

```markdown
## <timestamp> <approach> — problem: <problem-id> — attempt <N> of 3
Hypothesis: ... | What was tried (commands, patches): ... |
Checkpoint before: <ref/stash/copy, so revert is concrete> |
Result: ... | Failure class: hypothesis/context/tool/env/flaky/dependency/
implementation/permission | Why abandoned: ... | Do-not-repeat notes: ...
```

Consult before retrying anything. A retry must cite the logged attempts it
materially differs from; the third same-class failure on one problem-id
forces the recovery protocol's stop-and-choose — never a fourth retry.

### verification.md — verification ledger

```markdown
## <timestamp> <change or claim>
Reproduced original failure: y/n/how | Root cause: ... |
Tests run (and which fail without the fix): ... | Environments: ... |
Replay commands (exact, so an audit reruns evidence instead of
reconstructing it): ... |
Baseline vs. result: ... | Regression sweep: ... | Independent review:
agent + verdict | Evidence still missing: ...
```

### notes/ — raw subagent reports and long evidence
One file per delegation (`notes/<seq>-<agent>-<slug>.md`). The orchestrator
distills these into the ledgers; they are retrievable raw material, never
user-facing output.

## Not in `.mission/`: run telemetry

`.mission/` is per-project and describes *this* mission. Run telemetry —
timings, subagent spawns, tool counts, outcomes — goes to `~/.missionruntime/`
instead, because comparing runs across projects and hosts is the whole point
of collecting it. See the telemetry reference. Keep the two separate: ledgers
are for reasoning, telemetry is for measurement.

## Resumption protocol

On `mission-resume` (or any cold start where `.mission/` exists): read
state.md, then mission.md (including Amendments), then queue.md; skim recent
decisions, assumptions, attempts. Check capsule freshness: a ledger entry
newer than the capsule means the last session died before its refresh —
rebuild the capsule from the ledgers before trusting it. Demote every Active
queue entry to Pending with an orphan note: no agent survived the session,
so "Active" on a cold start is always stale. Reconcile against reality —
`git log <capsule sha>..HEAD`, `git status`, a cheap test run if the suite
is fast — because the repo may have changed while the runtime was away. Fold
discrepancies into the queue as new evidence, and re-verify any Done items
whose files changed externally. Then execute state.md's "Next action" and
re-enter the loop. Never ask the user to restate anything already in
`.mission/`.
