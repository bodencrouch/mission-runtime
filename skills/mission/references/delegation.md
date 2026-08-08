# Delegation and Subagent Orchestration

## Contents

- [Roster](#roster)
- [Work packet](#work-packet-every-delegation-includes-all-of-this)
- [Dispatch rules](#dispatch-rules)
- [Integration protocol](#integration-protocol-on-every-agent-return)
- [Anti-patterns](#anti-patterns)

Subagents are internal specialists reporting to the orchestrator — never
alternative user-facing assistants. The orchestrator remains the single
accountable owner: it supervises, validates, reconciles, integrates or
rejects, and decides what happens next. The user never receives a pile of
subagent transcripts.

## Roster

| Agent | Use for | Access |
|---|---|---|
| repo-cartographer | Map architecture, components, conventions, entry points, test layout | read + run (read-only by charter) |
| research-analyst | External docs, platform behavior, dependency research, issue archaeology | read + web |
| implementation-engineer | Bounded code changes from an approved plan | full |
| test-engineer | Test authoring, coverage gaps, flake hunting, running suites | full |
| security-reviewer | Vulnerabilities, secrets, injection, permissions, supply chain | read + run (read-only by charter) |
| code-quality-reviewer | Correctness, maintainability, convention adherence, complexity | read-only |
| regression-investigator | Reproduce failures, bisect, root-cause, sibling-defect sweeps | read + run |
| docs-writer | READMEs, runbooks, changelogs, doc-vs-behavior drift | read + write docs |
| adversarial-critic | Falsify claims of completion; independent audit before declaring done | read + run |

Enforcement of these boundaries is layered: each agent's `tools:` frontmatter
excludes what it must not use, and agents holding Bash for inspection carry a
charter restricting it to read-only commands. Routing among the three
falsification roles goes by object: behavior that broke → regression-
investigator; code quality → code-quality-reviewer; a completion claim or the
ledgers → adversarial-critic.

Missing specialty → use the closest general-purpose agent with a
role-defining work packet. Multiple instances of the same role are fine
(e.g., three research-analysts on three subsystems).

## Work packet (every delegation includes all of this)

The packet is the runtime's own product, never the user's message forwarded.
Order it context-first: binding constraints, then evidence and state, then the
ask — instructions at the end of a long prompt are followed best. Keep it
lean: point into `.mission/notes/` for long material instead of inlining it.

```markdown
OBJECTIVE: one sentence, outcome-shaped.
WHY: the governing principle behind the objective, in one line, so the cases
  this packet failed to enumerate still resolve the right way.
MISSION CONTEXT: the mission line + only the state the agent needs (pointers
  over pastes) + do-not-repeat notes from attempts.md where they apply.
SCOPE: files/systems in bounds; everything else out of bounds. No changes the
  objective does not require: no drive-by refactors, no unrequested cleanup,
  no abstractions for hypothetical future needs.
CONSTRAINTS: conventions, quality bar, do-not-touch list.
AUTHORITY: read-only | may edit <files> | may run <commands>. Reversible
  actions inside that boundary proceed without asking; anything outside it is
  a finding to report, not a decision to make.
DELIVERABLE TYPE: assessment | change | both — every packet says which.
EVIDENCE STANDARD: what makes a claim acceptable (repro steps, line refs,
  measurements — not opinions). For long-running packets: audit each progress
  claim against a tool result from this run; report unverified as unverified.
DELIVERABLE: sections required in the report — Findings (each with evidence +
  confidence), Proposed actions, Uncertainties, Artifacts touched. Where the
  report goes depends on the agent's authority (see below). Final message =
  data for the orchestrator, not prose for the user.
BUDGET: rough effort bound. Depth is set at dispatch (calibration reference),
  not requested in prose.
```

**Route freedom.** The packet states what must be true when the agent returns,
not the sequence of commands that gets there. Step-level instruction enters a
packet only as a repair for an observed miss, scoped to the role or task class
that produced it — the ratchet in the calibration reference. Everything the
runtime declines to put in a packet is listed there too: reasoning narration,
intensity words, enumerated permission lists, fixed agent counts, and any
figure describing how much context remains.

**Discovery versus reporting.** A packet that limits what an agent reports
also limits what it looks for; an obedient agent narrows its search to match
the threshold. State the two separately: search the whole scope, then report
ranked by severity, nits labeled as nits. A real correctness defect is never
dropped for being merely moderate, and a thin report is never padded to look
thorough.

**Who writes the note file.** The six inspection and review agents
(repo-cartographer, research-analyst, security-reviewer,
code-quality-reviewer, regression-investigator, adversarial-critic) work
read-only by charter: they return the full report as their final message and
the **orchestrator** saves it to `.mission/notes/<seq>-<agent>-<slug>.md`.
Write-capable agents (implementation-engineer, test-engineer, docs-writer)
save their own note file and return a terse summary. Instruct read-only
agents to return the report whole; asking one to write a file wastes a cycle
against its charter.

**Telemetry.** Delegations are recorded automatically by the host hooks
described in the telemetry reference — the agent type and the work packet are
captured at spawn, the outcome at return. Do not ask agents to log their own
telemetry, and do not hand-write delegation records while hooks are live.

## Dispatch rules

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

## Integration protocol (on every agent return)

1. Read the report; spot-check material claims against the repo. The check is
   falsifiable, not impressionistic: each material claim carries a file:line
   the orchestrator verifies, and each verification claim carries a command
   the orchestrator can rerun. A report with neither is a hypothesis — send
   it back or log it rejected in attempts.md.
2. Reconcile conflicts between agents by evidence quality, not seniority of
   arrival. If two credible reports disagree, commission a targeted
   tie-breaker packet: claim A, claim B, the discriminating experiment, and
   the decision lands in decisions.md.
3. Accept → distill into the ledgers (facts → state.md, work → queue.md,
   decisions → decisions.md). Reject → log why in attempts.md, optionally
   re-delegate with a sharpened packet.
4. Requested revisions go back to the same agent with the specific defect in
   its output named.

## Anti-patterns

Do not: delegate the whole mission to one giant subagent; spawn agents to
appear busy; let a subagent's question bubble up to the user (answer it from
the contract and ledgers, or make the call and log it); treat agent output as
accepted project state before validation; give an implementation agent an
open-ended "improve things" packet; forward the user's message as the packet
(it is evidence about the need, and the packet is what the runtime makes of
it); prescribe a tool-by-tool route the agent can derive from the objective.

A returned report that misses in one of these ways is a packet defect before
it is an agent defect. Apply the minimal repair from the calibration
reference's signal table, record the observation behind it, and re-dispatch.
