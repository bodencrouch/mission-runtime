# The Persistent Control Loop

Run this closed loop until the stopping policy fires. It is a control system,
not a linear prompt chain: every cycle can reorder, add, or retire work.

## Stages

1. **Interpret** — load `.mission/mission.md` (or create it via
   intent-contract.md on the first cycle). The contract is the fixed point;
   plans change, the mission does not.
2. **Inspect** — gather evidence: repo layout, docs, tests, config, issues,
   history, runtime behavior, logs, dependencies, packaging, conventions.
   Delegate broad sweeps (repo-cartographer, research-analyst) and run
   independent inspections concurrently.
3. **Model** — update the project model in `.mission/state.md`: known facts,
   assumptions, unknowns, risks, relevant components, observed failures,
   candidate improvements, verification obligations.
4. **Queue** — turn mission + evidence into tasks in `.mission/queue.md`.
   Each task records: traceability (one line linking it to the mission or to
   discovered evidence), expected value, cost, risk, reversibility,
   dependencies, required expertise, evidence needed for completion, and
   whether it can run in parallel. Mirror to the session task list.
5. **Execute** — take the highest-value unblocked task. Do it directly or
   delegate per delegation.md.
6. **Verify** — apply verification.md. Unverified work does not count as
   done.
7. **Update memory** — record results, new facts, rejected approaches, new
   risks, new tasks, changed priorities in the ledgers.
8. **Generate follow-ups** — run the continuation questions in stopping.md
   against what was just learned.
9. **Replan** — check the current plan is still the best route; detect stalls
   (see below).
10. **Continue or stop** — next task, or the stopping policy.

## Prioritization

The queue is never FIFO. Prefer work that is high-value, well-evidenced, and
mission-critical. Weigh: mission relevance, user impact, severity, diagnostic
confidence, expected improvement, evidence value (does it reduce
uncertainty?), risk reduction, reversibility, cost, dependency position
(does it unblock other work?), and parallelism opportunity. Defer work that is
speculative, cosmetic, weakly connected, high-risk with little evidence,
expensive relative to benefit, or likely to be invalidated by unresolved
upstream findings.

## Parallelism and conflict control

Run independent read-only work concurrently: architecture mapping, test-suite
analysis, documentation research, dependency research, issue-history review,
baseline collection — launch those agents in a single message. Keep dependent
work ordered: implementation does not begin from three incompatible proposals
unless the orchestrator has chosen one or set up isolated experiments.

Track in `.mission/queue.md`: file ownership, task dependencies, active agent
assignments, overlapping change surfaces. Two agents never edit the same
files concurrently without an explicit strategy: isolated worktrees/branches,
alternative prototypes with a designated merger, one writer plus read-only
reviewers, or a controlled comparison. Parallelism must reduce elapsed time,
not increase integration entropy.

## Stall detection

Declare a stall when: the same action repeats without new information; the
same failure recurs after materially identical attempts; evidence has not
changed across cycles; or the plan no longer reduces uncertainty. On stall:
gather different evidence; delegate an independent investigation; simplify or
isolate the problem; revert to known-good; replan at mission level; defer the
branch; or escalate only the irreducible human dependency. Log every stall
and response in `.mission/attempts.md`.

## Context management

Do not solve context pressure by hoarding transcript. The ledgers in
`.mission/` are the authoritative state; the conversation is disposable.
Continuously distinguish durable facts, decisions, and unresolved risks
(→ ledgers) from redundant narration, repeated tool output, and superseded
plans (→ drop). Before any compaction, forced turn end, or long pause,
refresh the resume capsule in `.mission/state.md` (schema in memory.md) so a
cold read of `.mission/` alone allows coherent continuation. Continuity of
intent, not continuity of text.

## Budgets

If the user or platform sets a time/token/cost budget, record it in the
contract and treat it as a hard stopping condition. Spend it by expected
value: verification of consequential changes outranks breadth of speculative
improvement.
