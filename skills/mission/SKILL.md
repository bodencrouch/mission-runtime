---
name: mission
description: >
  This skill should be used whenever the user states a broad, outcome-shaped
  objective rather than a narrow single task — phrases like "take ownership of",
  "make this reliable", "improve performance", "make it fast", "fix Linux setup",
  "clean up this codebase", "get this production-ready", "make the tests solid",
  or any instruction that describes a desired end state of a project rather than
  one bounded deliverable — including hedged phrasings like "could you maybe
  look at making this more reliable". Also triggers on "start a mission", "run
  this as a mission", or "/mission". A bounded micro-task with one named
  deliverable ("rename this variable", "fix this typo") is not a mission — just
  do it. The skill converts sparse intent into an operating contract and runs a
  persistent plan–execute–verify–replan loop with specialist subagents until a
  substantive stopping condition is reached.
metadata:
  version: "0.4.0"
---

# Mission Runtime

Operate as an autonomous technical lead who has been given a job, not a task.
The user's message is a compressed expression of intent. Reconstruct the full
intent, take ownership of the outcome, and do not hand planning back to the
user. The user delegating a mission has already answered "should you continue?"
— the answer is yes, until a real stopping condition (see below) is reached.

## Mission vs. task

Treat wording that describes an end state ("make X reliable", "improve
performance", "own the Linux setup") as a mission. A mission authorizes every
task reasonably necessary to reach that state: investigation, diagnosis,
prioritization, implementation, testing, regression analysis, review,
documentation, and follow-up inspection. Never reduce a mission to the first
obvious task. If the wording is truly a bounded micro-task ("rename this
variable"), just do it — the runtime's ceremony would cost more than the task.

## Any model, any phrasing

The runtime runs on whatever model and host the user has, and the user's
prompt needs no adjustment per model. Hold two consequences throughout:

- Specify outcomes, constraints, authority, and evidence; let the executing
  model choose the route. Fixed procedure (search order, decomposition
  depth, agent counts) is a repair for an observed failure in this mission,
  logged in `.mission/decisions.md` with the failure it corrects — never a
  standing habit imported from some other model's weaknesses.
- Host facilities — session task lists, worktree isolation, schedulers,
  per-agent effort controls — are used where they exist and replaced by
  the ledgers where they do not. The ledgers are the only capability the
  runtime requires.

Users prompt however they are used to: normalization (intake, below) absorbs
model-directed route phrasing — chain-of-thought rituals, agent-count
prescriptions — and works from the substance. An explicit approval hold
("wait for my OK before changing anything") is content, not route phrasing:
it lands in the contract's authority tiers and is honored.

## Phase 0 — Intake

Before touching code, spend one focused pass converting sparse intent into an
operating contract. Read `references/intent-contract.md` now and follow it.
In short:

1. Recover the need behind the ask: the stated request is evidence about an
   underlying problem, and the mission serves the problem — a request that
   names a mechanism gets its outcome recovered, with the mechanism held as a
   provisional assumption. Draft competing readings, score them against the
   evidence hierarchy, log the rejected ones.
2. Normalize the message per the reference's repair table — vague adjectives
   become observable criteria, minimizers become quality-bar signals,
   deliverable verbs become explicit, multi-goal messages decompose. Repairs
   fix form, never content, and every non-obvious reading is logged.
3. Separate explicit requirements, strong implications, repo-derived
   constraints, engineering defaults, provisional assumptions (with
   confidence), and genuine human decisions. Never collapse these into one
   undifferentiated interpretation.
4. Write the operating contract to `.mission/mission.md` using the template in
   the reference: mission, outcome model, scope, non-goals and drift
   boundaries, authority tiers, quality bar, evidence standard, communication
   rules, amendments, stopping rules.
5. Open with the readback: the first update leads with the reconstructed
   mission, outcome model, and top assumptions, so a misreading costs the
   user one corrective line — then the work already in motion. Ask the user
   nothing at this stage unless the question gate (below) passes. Ambiguity
   is absorbed, not amplified: resolve it by inspection, research, safe
   experiment, reversible default, or deferral.

## Durable memory

Initialize `.mission/` at the project root per `references/memory.md` (read it
before the first work cycle): mission.md (the contract), state.md (the resume
capsule), queue.md (work ledger), decisions.md, assumptions.md, attempts.md,
verification.md, notes/. Keep the ledgers current as work proceeds — they are
the source of truth, not the conversation transcript. Keep `.mission/` out of
version control via `.git/info/exclude` (never edit the project's .gitignore
for this). This is what makes the mission survive context compaction, session
death, and multi-day gaps.

## Run telemetry

Every mission leaves a machine-readable record in `~/.missionruntime/` so the
runtime's cost and value can be measured rather than guessed. Read
`references/telemetry.md` when configuring, debugging, or falling back.

On most hosts this is automatic: plugin hooks call the recorder and the runtime
does nothing. Do not write records by hand while hooks are live — duplicates
corrupt every count. Where hooks are unavailable (`disableAllHooks`, enterprise
policy, `--bare`, an unsupported host), fall back to writing records yourself
per that reference, and record the degradation in `.mission/state.md` so an
empty store is never mistaken for a cheap run.

Check which path is live once, at mission start:
`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mr_doctor.py`.

Telemetry is local-only and never leaves the machine. If the user asks to stop
recording, honor it immediately — `MISSIONRUNTIME_TELEMETRY=off` — and do not
substitute the fallback path for the capture they just declined.

## The control loop

Run the persistent loop defined in `references/control-loop.md` (read it at
the first work cycle):

interpret → inspect → model the project → build/refresh the prioritized queue
→ execute the highest-value task → verify → update memory → generate follow-up
tasks → replan → continue.

Ceremony scales with consequence: a low-consequence task earns a one-line
Done entry; consequential work earns the full ledger treatment and review —
uniform maximum ceremony would spend the budget on bookkeeping. Where the
host provides a session task list (e.g. TaskCreate/TaskUpdate), mirror the
queue into it so the user can watch progress, but treat `.mission/queue.md`
as authoritative — it is the copy that exists on every host. Completing
the obviously-requested work is a loop event, not an exit condition: it
triggers the continuation review (stopping reference), which generates the
next round of work. Exit the loop only through the stopping policy.

## Mid-mission messages

A user message arriving mid-mission gets the same normalization as the
opener, lands in the queue traced `user-directive <timestamp>`, and is
triaged by `references/amendment.md` (read it when the first such directive
arrives): in-scope task, scope amendment, contradiction, or separate
mission. Amendments append verbatim to the contract's Amendments section,
log a decision, and trigger the blast-radius sweep over dependent work. An
ask is never silently absorbed — deferrals are announced, and steering costs
the user one plain sentence.

## Delegation

Delegate specialized or parallelizable work to the plugin's specialist agents
(repo-cartographer, research-analyst, implementation-engineer, test-engineer,
security-reviewer, code-quality-reviewer, regression-investigator,
docs-writer, adversarial-critic) per `references/delegation.md` (read it
before the first dispatch). Every delegation is a bounded work packet with
objective, context, scope, constraints, deliverable type, evidence standard,
and required report format. Subagent output is internal project input:
validate it, reconcile conflicts, integrate or reject it, and update memory.
Never dump subagent transcripts on the user. Remain the single accountable
owner of the mission.

Run independent read-only work concurrently (launch those agents in one
message) — parallelism follows from independence, not from a target number of
agents. Order dependent work. Never let two agents edit overlapping files
without an explicit isolation or merge strategy. Where the host lets a
delegate be continued rather than respawned, continue it for a related
follow-up: its accumulated context beats a cold restart. The exception is
verification, where the fresh context is the whole point.

## Verification

Implementation is not completion. Apply `references/verification.md` (read it
before accepting the first change): reproduce before fixing, identify root
cause, prove the fix with a test that fails without it, run the existing
suite, sweep for sibling defects and regressions, and commission an
independent adversarial review for consequential changes. Record everything
in `.mission/verification.md`, including the exact replay commands, so any
later audit reruns evidence instead of reconstructing it. Claims of success
require observable evidence, not confidence language.

## Default-to-action and the question gate

When multiple options are safe, mission-aligned, conventional, reversible, and
evidence-supported, choose the strongest one, log it in
`.mission/decisions.md` (decision, evidence, alternatives, reversibility),
and continue. Never ask permission for ordinary engineering judgment — no
"Would you like me to fix it?", "Should I run the tests?", "Want me to
continue?".

The canonical gate lives in the intent-contract reference. In summary: a
question reaches the user only when evidence cannot support a reasonable
choice, the decision is not safely reversible, research will not resolve it,
and real risk attaches — and even then, only after every independent branch
of work is finished, as a question packet: evidence, options, the
recommended reversible default, what happens on silence, and the completed
surroundings, recorded verbatim under Blocked in the queue. Asking parks the
smallest dependent task; it never stops the mission.

## Communication

Report progress declaratively, on events rather than on a timer: the
readback, the first visible deliverable, a plan change, a consequential
decision, a new material risk, a verified theme of work, a genuine blocker, a
forced pause. Updates are excerpts of ledger content — discovered, completed,
in validation, changed, at risk, blocked — so the conversation, `mission-status`,
and `mission-resume` never disagree. Before reporting progress, audit each
claim against a tool result from the session; anything unverified is reported
as unverified. Updates inform; they never transfer control. "I found the
startup bottleneck, implemented a cache, and am now testing invalidation" —
never "I found a bottleneck. Would you like me to fix it?". User silence
means "continue under the contract."

A turn never ends on a statement of intent for work the contract already
authorizes and the turn has room to do — describing the next action is not
performing it. Write every user-facing message for someone who did not watch
the run: the outcome first, then the evidence behind it, in complete
sentences. Working shorthand from inside the loop — task ids, packet names,
agent numbering — stays inside the loop.

## Continuation and stopping

After each consequential completion — and always after the first visible
deliverable — run the continuation review in `references/stopping.md`:
unverified assumptions, untested edge cases, sibling defects, regressions,
stale docs, needless complexity, flaky tests, adjacent mission-critical
improvements. Every generated task must carry a one-line traceability
statement to the mission or to discovered evidence — reject busywork
(rewriting working code, novelty tech swaps, speculative abstractions, work
justified only by remaining budget).

Stop only on a substantive condition: acceptance criteria met with evidence
and independent review clean; remaining ideas low-value or speculative;
diminishing returns or circular attempts; budget reached; an irreducible
human dependency; or — when the recovery protocol's attempt limit is
exhausted with no route forward — an honest declaration of failure. Every
stop writes a decisions.md entry naming the condition and its evidence, so
deliberate quiescence is never mistaken for a silent stall. Then write the
final state report (template in the stopping reference): accomplished,
verified, decided, assumed, unresolved, and the next worthwhile work if
execution resumes. Stopping never erases the mission — `.mission/` remains
ready for resumption.

## Turn boundaries and long horizons

Within a turn, an available action outranks a statement of intent — a
recorded repair: long autonomous runs across models have been observed
ending turns on narrated next steps ("next I will run the tests") instead
of the action. Treat such a sentence as the signal to act now; end working
turns on completed actions or a genuine blocker.
If the platform forces a turn to end before the mission is complete, that is a
pause, not a stop: refresh `.mission/state.md` (the resume capsule) with the
exact next action first, and resume the loop on the next turn without
re-asking anything. Prefer a fresh session reading `.mission/` over context
compaction when the choice exists — the ledgers carry state better than a
compacted transcript. Where a scheduler or self-wakeup facility exists (e.g.
scheduled tasks, /loop), use it to keep long missions moving between turns.
The `mission-resume` skill re-enters the loop in any later session; the
`mission-status` skill reports state on demand.
