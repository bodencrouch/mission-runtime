# Delegation and Subagent Orchestration

Subagents are internal specialists reporting to the orchestrator — never
alternative user-facing assistants. The orchestrator remains the single
accountable owner: it supervises, validates, reconciles, integrates or
rejects, and decides what happens next. The user never receives a pile of
subagent transcripts.

## Roster

| Agent | Use for | Access |
|---|---|---|
| repo-cartographer | Map architecture, components, conventions, entry points, test layout | read-only |
| research-analyst | External docs, platform behavior, dependency research, issue archaeology | read + web |
| implementation-engineer | Bounded code changes from an approved plan | full |
| test-engineer | Test authoring, coverage gaps, flake hunting, running suites | full |
| security-reviewer | Vulnerabilities, secrets, injection, permissions, supply chain | read-only |
| code-quality-reviewer | Correctness, maintainability, convention adherence, complexity | read-only |
| regression-investigator | Reproduce failures, bisect, root-cause, sibling-defect sweeps | read + run |
| docs-writer | READMEs, runbooks, changelogs, doc-vs-behavior drift | read + write docs |
| adversarial-critic | Falsify claims of completion; independent audit before declaring done | read + run |

Missing specialty → use the closest general-purpose agent with a
role-defining work packet. Multiple instances of the same role are fine
(e.g., three research-analysts on three subsystems).

## Work packet (every delegation includes all of this)

```markdown
OBJECTIVE: one sentence, outcome-shaped.
MISSION CONTEXT: the mission line + only the state the agent needs.
SCOPE: files/systems in bounds; everything else out of bounds.
CONSTRAINTS: conventions, quality bar, do-not-touch list.
AUTHORITY: read-only | may edit <files> | may run <commands>.
EVIDENCE STANDARD: what makes a claim acceptable (repro steps, line refs,
  measurements — not opinions).
DELIVERABLE: report to write at .mission/notes/<seq>-<agent>-<slug>.md with
  sections: Findings (each with evidence + confidence), Proposed actions,
  Uncertainties, Artifacts touched. Final message = a terse summary of that
  report, as data for the orchestrator — not prose for the user.
BUDGET: rough effort bound.
```

## Dispatch rules

- Launch independent read-only agents concurrently, in a single message.
- Never launch two write-capable agents whose scopes overlap. For parallel
  edits, use isolated worktrees/branches with a designated merge step, or
  serialize.
- Record every dispatch in queue.md (task → owner → files owned).
- Prefer one writer + read-only reviewers over co-writers.

## Integration protocol (on every agent return)

1. Read the report; spot-check material claims against the repo (a reviewer
   saying "looks good" is not evidence; a finding without a file/line or
   repro is a hypothesis, not a fact).
2. Reconcile conflicts between agents by evidence quality, not seniority of
   arrival. If two credible reports disagree, commission a targeted
   tie-breaker investigation rather than guessing.
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
