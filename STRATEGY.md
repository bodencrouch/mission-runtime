---
name: mission-runtime
last_updated: 2026-08-07
---

# mission-runtime Strategy

## Target problem

A developer who delegates work to an AI assistant still does the hardest part
themselves: turning a rough goal into precise instructions, catching early
stops, and re-explaining everything when the session ends. Assistants act on
what was literally said rather than what was actually needed, and their memory
dies with the conversation.

## Our approach

Treat the user's message as evidence of intent, not as the task list: the
runtime reconstructs the outcome the user actually needs, writes it down as a
contract, and runs a persistent plan–execute–verify loop against that contract
until an evidence-backed stopping condition is met. All mission state lives in
files on disk, so the work outlives any one session.

## Who it's for

**Primary:** A developer delegating outcome-shaped work — "make this
reliable", "clean this up", "get it production-ready". They're hiring
mission-runtime to turn a one-sentence goal into finished, verified
engineering work without supervising each step.

## Key metrics

- **User prompts per completed mission** — how much steering a mission needs
  after the opening message; measured from `~/.missionruntime/` via
  `mr_report.py`.
- **Verified-completion rate** — share of missions that end with evidence in
  `.mission/verification.md` rather than silently stalling; read from the
  mission ledgers.
- **Resume survival** — whether a mission continued in a later session picks
  up without the user re-explaining anything; observed from session records
  and `.mission/state.md` freshness.
- **Cost per mission** — wall-clock, tool calls, and subagent spend for
  mission sessions against the non-mission baseline; `mr_report.py`'s
  comparison view.

## Tracks

### Intent and instruction quality

The prompt surfaces — skills, agents, reference docs — that turn sparse input
into the right mission and the right behavior.

_Why it serves the approach:_ reconstruction of intent is the product; it is
only as good as the instructions that define it.

### Durable memory and resumption

The `.mission/` ledger system, resume flow, and state discipline.

_Why it serves the approach:_ the contract-and-loop model only works if the
mission survives session death and context loss.

### Verification and delegation

Evidence-gated completion: specialist agents for bounded work, reproduction
before fixes, tests as proof, adversarial review as the final gate.

_Why it serves the approach:_ unsupervised work is only acceptable when
completion claims carry evidence.

### Measurement

Local telemetry that records what each run did and what it cost.

_Why it serves the approach:_ an autonomous runtime that can't be benchmarked
can't be trusted or improved.

## Not working on

- Porting the whole plugin to other hosts — only the telemetry surface is
  cross-host today.
- Any telemetry that leaves the machine. Records stay on local disk, always.
- Runtime dependencies beyond Python 3's standard library.

## Marketing

**One-liner:** State an outcome. The runtime owns the engineering work until
that outcome is real and verified.
