---
name: mission-runtime
last_updated: 2026-08-12
---

# mission-runtime Strategy

## Target problem

A developer who wants an AI to own an outcome has to do the prompt engineering
first: decompose the goal, define who does what, state acceptance criteria, and
say what evidence counts. Skip that work and the assistant executes the literal
words; do it properly and the developer has already done the hard part
themselves.

## Our approach

The runtime does the prompt engineering the user skipped. It reconstructs the
need behind the message, writes it down as a contract, and synthesizes the
specialist roles and briefs that this particular mission demands — every
generated line traceable to the request or to gathered evidence, and checked
for drift before anyone acts on it. The bet is on generated specification,
rather than on a fixed agent roster or on asking the user more questions.

## Who it's for

**Primary:** A developer delegating outcome-shaped work — "make this reliable",
"clean this up", "get it production-ready". They're hiring mission-runtime to
turn a one-sentence goal into finished, verified engineering work without
writing the brief and without supervising each step.

## Key metrics

- **Readback correction rate** — share of missions whose first user reply after
  the readback corrects the reconstructed mission or outcome model; read from
  `.mission/` amendments against session records. Rises when intent recovery
  drifts.
- **Steering prompts per completed mission** — user messages after the opener,
  including anything the user has to re-explain after a resume; measured from
  `~/.missionruntime/` via `mr_report.py`.
- **Packet rejection rate** — share of delegations whose report is rejected at
  integration or re-dispatched with a sharpened brief; counted from
  `.mission/attempts.md`. Rises when generated briefs are underspecified.
- **Verified-completion rate** — share of missions ending with evidence in
  `.mission/verification.md` rather than silently stalling; read from the
  mission ledgers.
- **Cost per mission** — wall-clock, tool calls, and subagent spend for mission
  sessions against the non-mission baseline; `mr_report.py`'s comparison view.

## Tracks

### Intent reconstruction

Recovering the need behind a sparse message and fixing it as a contract: the
diagnosis, the confidence tiers, the readback, and the non-blocking questions
the user can answer or ignore.

_Why it serves the approach:_ every generated brief inherits the errors of the
reconstruction it came from, so this is where drift is cheapest to catch.

### Role synthesis and briefing

Deriving the role set a specific mission demands, writing each brief to a
checkable standard, and validating it before dispatch.

_Why it serves the approach:_ this is the prompt engineering the user was
skipping, and it is where a generated prompt either holds or drifts.

### Durable evidence

The `.mission/` ledgers, the resume protocol, verification gates, and
adversarial audit before any completion claim.

_Why it serves the approach:_ unsupervised work is only acceptable when
completion carries evidence, and only if the mission survives session death.

### Measurement

Local telemetry that records what each run did and what it cost.

_Why it serves the approach:_ a runtime that writes its own instructions has to
be benchmarked, or nobody can tell good generation from confident generation.

## Not working on

- Teaching users to write better prompts. Improving the input is the runtime's
  job; a user who has to learn the phrasing has been handed the work back.
- Porting the whole plugin to other hosts — only the telemetry surface is
  cross-host today.
- Any telemetry that leaves the machine. Records stay on local disk, always.
- Runtime dependencies beyond Python 3's standard library.

## Marketing

**One-liner:** Give it one line. The runtime writes the full brief, assembles
the specialists, and works until the outcome is verified.

**Key message:** You describe the outcome you want. The runtime works out what
you actually need, writes the specification, and builds the team of specialists
to deliver it. It shows you its reading first, so one sentence corrects it.
