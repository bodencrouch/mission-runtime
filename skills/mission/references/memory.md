# Durable Project Memory (`.mission/`)

Create `.mission/` at the project root on mission start. It is the runtime's
persistent brain: mission memory, work ledger, decision log, assumption
register, attempt history, verification ledger, and resume capsule. The
conversation window is a cache; these files are the database.

Keep it out of version control without touching the project: append
`.mission/` to `.git/info/exclude` (create the file if absent). Never commit
`.mission/`, and never edit the project's `.gitignore` for this purpose. If
there is no git repo, just use the directory.

Update ledgers as events happen, not in batches at the end. Append-only files
get new entries at the top. Rewritten files (state.md) are replaced wholesale.

## Files

### mission.md — the operating contract (write once, amend rarely)
Template in intent-contract.md. Amend only when the user redirects the
mission or a contract-level assumption is disproven; log the amendment in
decisions.md.

### state.md — resume capsule (rewrite frequently; this is the file a cold
session reads first)

```markdown
# State — <ISO timestamp>
## Mission (one line)
## Current interpretation / plan (short)
## Project model
Facts, components, conventions, environments, risks — compact bullets.
## Completed (with evidence pointers into verification.md)
## Active
Task, owner (self/agent), current hypothesis, files in play.
## Assumptions in force (top items; full register in assumptions.md)
## Blockers (smallest dependent task each, and what was finished around it)
## Risks
## Next action (exact, executable — "run X", "delegate Y to test-engineer")
```

### queue.md — work ledger

```markdown
## Pending   (priority-ordered)
- [P1] <task> — trace: <mission link or evidence> — value/cost/risk —
  deps: ... — parallel-safe: y/n — expertise: <agent or self>
## Active    (task — owner — files owned — started)
## Blocked   (task — exact dependency — what proceeds anyway)
## Deferred  (task — why: speculative/low-value/awaiting-upstream)
## Done      (task — evidence pointer — completed)
## Canceled  (task — why)
```

### decisions.md — append-only decision log

```markdown
## <timestamp> <decision title>
Decided: ... | Why: ... | Evidence: ... | Alternatives rejected: ... |
Reversibility: ... | Follow-up verification: ...
```

### assumptions.md — assumption register

```markdown
## <id> <statement>
Source: inferred/repo/default | Confidence: high/med/low |
Impact if wrong: ... | Verification method: ... |
Status: unverified/confirmed/refuted (+ where)
```

Refuted assumptions trigger queue review: retire or rework dependent tasks.

### attempts.md — append-only attempt history (anti-circling)

```markdown
## <timestamp> <approach>
Hypothesis: ... | What was tried (commands, patches): ... |
Result: ... | Failure class: hypothesis/context/tool/env/flaky/dependency/
implementation/permission | Why abandoned: ... | Do-not-repeat notes: ...
```

Consult before retrying anything. A retry must be materially different from
every logged attempt.

### verification.md — verification ledger

```markdown
## <timestamp> <change or claim>
Reproduced original failure: y/n/how | Root cause: ... |
Tests run (and which fail without the fix): ... | Environments: ... |
Baseline vs. result: ... | Regression sweep: ... | Independent review:
agent + verdict | Evidence still missing: ...
```

### notes/ — raw subagent reports and long evidence
One file per delegation (`notes/<seq>-<agent>-<slug>.md`). The orchestrator
distills these into the ledgers; they are retrievable raw material, never
user-facing output.

## Resumption protocol

On `mission-resume` (or any cold start where `.mission/` exists): read
state.md, then mission.md, then queue.md; skim recent decisions, assumptions,
attempts. Reconcile the ledger against reality — `git status`/`git log` since
the capsule timestamp, quick test run if cheap — because the repo may have
changed while the runtime was away. Fold discrepancies into the queue as new
evidence. Then execute state.md's "Next action" and re-enter the loop. Never
ask the user to restate anything already in `.mission/`.
