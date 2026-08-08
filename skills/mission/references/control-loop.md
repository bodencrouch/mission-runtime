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
   delegate per the delegation protocol. Honor the task's deliverable type:
   an investigation task produces findings and an implementation task
   produces changes. Discovering mid-task that the other one is warranted
   creates a queue entry for the prioritization to weigh — it does not
   silently widen the task in flight.
6. **Verify** — apply the verification reference. Unverified work does not
   count as done.
7. **Update memory** — record results, new facts, rejected approaches, new
   risks, new tasks, changed priorities in the ledgers. Ceremony scales with
   consequence: a low-consequence task earns a one-line Done entry; a
   consequential change earns the full verification record — uniform maximum
   bookkeeping starves the work it accounts for.
8. **Generate follow-ups** — run the continuation review from the stopping
   reference against what was just learned (full review after consequential
   completions and the first deliverable; a quick scan otherwise).
9. **Replan** — check the current plan is still the best route; detect stalls
   (see below); calibrate. A delegate that overran its scope, under-evidenced
   a claim, stopped short of its authority, or spent heavily for a small
   finding is a packet defect first: apply the minimal repair from the
   calibration reference, record the observation behind it, and retire
   repairs that no longer show up in the returns.
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
carries state better than a compacted transcript. Continuity of intent, not
continuity of text.

Context is the orchestrator's resource to manage, and no delegate is handed a
figure describing how much of it remains: an executor watching its own window
spends the work budget on winding down instead of working. If the host
surfaces such a figure into a delegation, say plainly in the packet that
context is managed outside the agent and the work continues.

## Budgets

Two budgets, different owners. A work budget — time, tokens, cost, set by the
user or the platform — is recorded in the contract and treated as a hard
stopping condition; spend it by expected value, where verification of
consequential changes outranks breadth of speculative improvement. A context
budget is the size of one window, and it is a scheduling constraint on the
loop, not a reason to stop: it is answered by the capsule and a fresh session,
never by ending the mission early.
