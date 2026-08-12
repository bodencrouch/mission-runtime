# Delegation and Subagent Orchestration

## Contents

- [Chassis](#chassis)
- [The commission](#the-commission)
- [Dispatch rules](#dispatch-rules)
- [Integration protocol](#integration-protocol-on-every-agent-return)
- [Anti-patterns](#anti-patterns)

Subagents are internal specialists reporting to the orchestrator — never
alternative user-facing assistants. The orchestrator remains the single
accountable owner: it supervises, validates, reconciles, integrates or
rejects, and decides what happens next. The user never receives a pile of
subagent transcripts.

## Chassis

The plugin's agents are chassis — authority capsules a commission runs on —
rather than the routing space itself. The commission carries the role; the
chassis carries the tool grant. Route by the work, then confirm the authority
shape satisfies what the commission needs.

| Chassis | Use for | Authority shape |
|---|---|---|
| repo-cartographer | Map architecture, components, conventions, entry points, test layout | read + run, read-only by charter |
| research-analyst | External docs, platform behavior, dependency research, issue archaeology | read + fetch, no execution |
| commissioned-analyst | Any commissioned read-only role the specialties here do not fit | read + run + fetch, role-neutral |
| implementation-engineer | Bounded code changes from a decided plan | write within a decided scope |
| test-engineer | Test authoring, coverage gaps, flake hunting, running suites | write within a decided scope |
| security-reviewer | Vulnerabilities, secrets, injection, permissions, supply chain | read + run, read-only by charter |
| code-quality-reviewer | Correctness, maintainability, convention adherence, complexity | read only, no execution |
| regression-investigator | Reproduce failures, bisect, root-cause, sibling-defect sweeps | read + run, read-only by charter |
| docs-writer | READMEs, runbooks, changelogs, doc-vs-behavior drift | write, docs files only |
| adversarial-critic | Falsify claims of completion; independent audit before declaring done | read + run, read-only by charter |

Enforcement of these boundaries is layered: each agent's `tools:` frontmatter
excludes what it must not use, and agents holding Bash for inspection carry a
charter restricting it to read-only commands. Routing among the three
falsification roles goes by object: behavior that broke → regression-
investigator; code quality → code-quality-reviewer; a completion claim or the
ledgers → adversarial-critic.

A commissioned role that no specialty here fits runs on `commissioned-analyst`,
which is role-neutral by design, rather than on an unbounded general-purpose
agent — the plugin's tool boundaries are part of what the runtime guarantees.
Multiple instances of one chassis are fine (three commissioned-analysts on
three subsystems).

## The commission

Every delegation ships as a commission: one artifact carrying the role and the
brief for that unit of work, generated from the contract and checked before
dispatch. The nine slots, the self-containment rule, the chassis tool grants,
and the pre-dispatch gate live in `commission.md`. Read it before the first
dispatch, and again whenever a returned report comes back shallow or duplicates
another agent's work — both failures trace to the commission rather than to the
chassis, and the repair is the failing slot. What the runtime declines to put
in a commission — step-level routes, reasoning narration, intensity words,
enumerated permission lists, fixed agent counts, a remaining-context figure —
is catalogued in the calibration reference, alongside the ratchet that adds
one back only as a repair for an observed miss.

## Dispatch rules

- Default to one worker for anything the orchestrator would finish in a
  handful of tool calls, two to four for a bounded comparison or
  investigation, and more only where responsibilities are genuinely divided.
  Delegation costs roughly an order of magnitude more tokens than doing the
  work directly (a measured multi-agent run consumed ~15× the tokens of the
  chat equivalent), and duplicated work is the largest measured multi-agent
  failure mode. These bands are published defaults with no ablation behind
  them: treat them as the starting point and move off them on this mission's
  evidence.
- Size each commission to the largest coherent chunk of ownership the agent
  handles reliably: start outcome-shaped, and narrow on evidence — a failed
  integration check, a visibly shallow or truncated report, decomposition
  lessons already in the ledgers — never on habit imported from another
  model. Log the narrowing as a repair in `.mission/decisions.md` with the
  evidence that required it, so later dispatches start from what this run
  has shown.
- Where the host exposes a per-agent depth or effort control, set it to
  match the commission's consequence. Intensity prose in the commission ("be
  thorough", "double-check everything") is not a substitute and is never
  written — the evidence standard already says what rigor means here.
- Where the host supports continuing a prior agent, reuse one whose
  accumulated context still pays for itself across related commissions; where
  it does not, the note file in `.mission/notes/` is the re-brief.
- Launch independent read-only agents concurrently, in a single message.
  Concurrency follows from independence; a target number of agents is not a
  goal, and neither is keeping the roster busy.
- Never launch two write-capable agents whose scopes overlap. For parallel
  edits, use isolated worktrees/branches with a designated merge step, or
  serialize.
- Record every dispatch in queue.md (task → owner → files owned), and check
  that ownership record before launching any writer.
- Prefer one writer + read-only reviewers over co-writers.
- Where the host supports continuing a delegate rather than respawning it,
  continue it for related follow-up work — accumulated context is worth more
  than a cold restart. Verification is the standing exception: a review is
  dispatched fresh, because independence from the work is what it is for.

**Telemetry.** Delegations are recorded automatically by the host hooks
described in the telemetry reference — the agent type and the commission are
captured at spawn, the outcome at return. Do not ask agents to log their own
telemetry, and do not hand-write delegation records while hooks are live.

## Integration protocol (on every agent return)

1. Read the report; spot-check material claims against the repo. The check is
   falsifiable, not impressionistic: each material claim carries a file:line
   the orchestrator verifies, and each verification claim carries a command
   the orchestrator can rerun. A report with neither is a hypothesis — send
   it back or log it rejected in attempts.md.
2. Reconcile conflicts between agents by evidence quality, not seniority of
   arrival. If two credible reports disagree, write a targeted tie-breaker
   commission: claim A, claim B, the discriminating experiment, and the
   decision lands in decisions.md.
3. Accept → distill into the ledgers (facts → state.md, work → queue.md,
   decisions → decisions.md). Reject → log why in attempts.md, optionally
   re-delegate with the failing slot repaired.
4. Requested revisions go back to the same agent with the specific defect in
   its output named.

## Anti-patterns

Do not: delegate the whole mission to one giant subagent; spawn agents to
appear busy; let a subagent's question bubble up to the user (answer it from
the contract and ledgers, or make the call and log it); treat agent output as
accepted project state before validation; give an implementation agent an
open-ended "improve things" commission; forward the user's message as the
commission (it is evidence about the need, and the commission is what the
runtime makes of it); prescribe a tool-by-tool route the agent can derive from
the objective.

A returned report that misses in one of these ways is a commission defect
before it is an agent defect. Apply the minimal repair from the calibration
reference's signal table, record the observation behind it, and re-dispatch.
