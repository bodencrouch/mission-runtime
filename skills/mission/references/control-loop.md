# The Persistent Control Loop

Run this closed loop until the stopping policy fires. It is a control system,
not a linear prompt chain: every cycle can reorder, add, or retire work.

## Stages

1. **Interpret** — load `.mission/mission.md` (or create it via the
   intent-contract reference on the first cycle). The contract is the fixed
   point; plans change, the mission does not. Mid-mission user directives
   enter through the amendment protocol.
2. **Inspect** — gather evidence: repo layout, docs, tests, config, issues,
   history, runtime behavior, logs, dependencies, packaging, conventions.
   Delegate broad sweeps (repo-cartographer, research-analyst) and run
   independent inspections concurrently. Close an inspection branch once
   further evidence is unlikely to change the next decision — investigation
   depth is bounded by decision-relevance, not by capability or remaining
   budget.
3. **Model** — update the project model in `.mission/state.md`: known facts,
   assumptions, unknowns, risks, relevant components, observed failures,
   candidate improvements, verification obligations.
4. **Queue** — turn mission + evidence into tasks in `.mission/queue.md`.
   Each task records: traceability (one line linking it to the mission or to
   discovered evidence), expected value, cost, risk, reversibility,
   dependencies, required expertise, evidence needed for completion, and
   whether it can run in parallel. Mirror to the session task list where
   the host provides one; queue.md stays authoritative.
5. **Commission** — for the highest-value unblocked task the orchestrator
   will not do directly, write the commission per the commission reference
   and run its pre-dispatch gate before anyone acts on it. A commission that
   fails the gate is repaired at the failing slot, not dispatched anyway.
6. **Execute** — do the task directly, or dispatch the gated commission to
   its bound chassis.
7. **Verify** — apply the verification reference. Unverified work does not
   count as done.
8. **Update memory** — record results, new facts, rejected approaches, new
   risks, new tasks, changed priorities in the ledgers. Ceremony scales with
   consequence: a low-consequence task earns a one-line Done entry; a
   consequential change earns the full verification record — uniform maximum
   bookkeeping starves the work it accounts for.
9. **Generate follow-ups** — run the continuation review from the stopping
   reference against what was just learned (full review after consequential
   completions and the first deliverable; a quick scan otherwise).
10. **Replan** — check the current plan is still the best route; detect stalls
    (see below).
11. **Continue or stop** — next task, or the stopping policy.

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
baseline collection — commission and launch those agents in a single message.
Keep dependent work ordered: implementation does not begin from three
incompatible proposals unless the orchestrator has chosen one or set up
isolated experiments. How many commissions a task deserves, and the reason,
is a dispatch rule in the delegation reference — read it before scaling a
single task into several.

Track in `.mission/queue.md`: file ownership, task dependencies, active agent
assignments, overlapping change surfaces. Two agents never edit the same
files concurrently without an explicit strategy: isolated worktrees/branches
(use the host's worktree isolation where it exists), alternative prototypes
with a designated merger, one writer plus read-only reviewers, or a
controlled comparison. Parallelism must reduce elapsed time, not increase
integration entropy.

## Stall detection

Declare a stall when: the same action repeats without new information; the
same failure recurs after materially identical attempts; evidence has not
changed across cycles; or the plan no longer reduces uncertainty. The attempt
history makes this mechanical: retries cite the logged attempts they differ
from, and the third same-class failure on one problem forces the recovery
protocol's stop-and-choose. On stall: gather different evidence; delegate an
independent investigation; simplify or isolate the problem; revert to
known-good; replan at mission level; defer the branch; or escalate only the
irreducible human dependency. Log every stall and response in
`.mission/attempts.md`.

## Context management

Do not solve context pressure by hoarding transcript. The ledgers in
`.mission/` are the authoritative state; the conversation is disposable.
Continuously distinguish durable facts, decisions, and unresolved risks
(→ ledgers) from redundant narration, repeated tool output, and superseded
plans (→ drop). Before any compaction, forced turn end, or long pause,
refresh the resume capsule in `.mission/state.md` (schema in the memory
reference) so a cold read of `.mission/` alone allows coherent continuation.
Prefer a fresh session over compaction when the choice exists — the capsule
carries state better than a compacted transcript. Window pressure is host
machinery, not mission strategy: never shrink scope or wind work down
because the window feels short. Refresh the capsule at natural checkpoints —
after each verify stage, before anything long — so a boundary, signaled or
not, lands after a fresh capsule; then keep working. Continuity of intent,
not continuity of text.

## Budgets

If the user or platform sets a time/token/cost budget, record it in the
contract and treat it as a hard stopping condition. Spend it by expected
value: verification of consequential changes outranks breadth of speculative
improvement. A budget bounds when work stops, never how large the mission
reads — do not quietly shrink the outcome model to fit it. When the budget
plainly cannot cover the outcome, surface the tension in the next update,
log the triage in `.mission/decisions.md`, and spend what exists on the
highest-value slice.
