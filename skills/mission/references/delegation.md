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

Order the packet context-first: binding constraints, then evidence and state,
then the ask — instructions at the end of a long prompt are followed best.
Keep the packet lean: point into `.mission/notes/` for long material instead
of inlining it.

```markdown
OBJECTIVE: one sentence, outcome-shaped.
MISSION CONTEXT: the mission line + only the state the agent needs (pointers
  over pastes).
SCOPE: files/systems in bounds; everything else out of bounds. No unrequested
  refactors, features, or cleanups riding along.
CONSTRAINTS: conventions, quality bar, do-not-touch list.
AUTHORITY: read-only | may edit <files> | may run <commands>.
DELIVERABLE TYPE: assessment | change | both — every packet says which.
EVIDENCE STANDARD: what makes a claim acceptable (repro steps, line refs,
  measurements — not opinions). For long-running packets: audit each progress
  claim against a tool result from this run; report unverified as unverified.
DELIVERABLE: sections required in the report — Findings (each with evidence +
  confidence), Proposed actions, Uncertainties, Artifacts touched. Where the
  report goes depends on the agent's authority (see below). Final message =
  data for the orchestrator, not prose for the user.
BUDGET: rough effort bound.
```

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

- Size each packet to the largest coherent chunk of ownership the delegate
  handles reliably: start outcome-shaped, and split into narrower packets
  only after an integration check fails — logging in attempts.md which
  decomposition the failure required, so later dispatches start from
  evidence about the executing model, not habit imported from another.
- Where the host exposes a per-delegate depth or effort control, set it to
  match the packet's consequence. Intensity prose in the packet ("be
  thorough", "double-check everything") is not a substitute and is never
  written — the evidence standard already says what rigor means here.
- Where the host supports continuing a prior delegate, reuse one whose
  accumulated context still pays for itself across related packets; where it
  does not, the note file in `.mission/notes/` is the re-brief.
- Launch independent read-only agents concurrently, in a single message.
- Never launch two write-capable agents whose scopes overlap. For parallel
  edits, use isolated worktrees/branches with a designated merge step, or
  serialize.
- Record every dispatch in queue.md (task → owner → files owned), and check
  that ownership record before launching any writer.
- Prefer one writer + read-only reviewers over co-writers.

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
open-ended "improve things" packet.
