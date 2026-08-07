# Intent Reconstruction and the Operating Contract

## Contents

- [The need behind the ask](#the-need-behind-the-ask)
- [Sparse-intent reconstruction](#sparse-intent-reconstruction)
- [Message normalization](#message-normalization)
- [Evidence hierarchy](#evidence-hierarchy)
- [Confidence tiers](#confidence-tiers)
- [Operating contract template](#operating-contract-template)
- [The readback](#the-readback)
- [The question gate](#the-question-gate)

## The need behind the ask

A request usually names a mechanism; the mission serves the need. Before
scoping anything, recover the situation that made the user write the message:
what hurts, what they would recognize as "this is what I wanted", and what
would make the complaint stop coming back. The stated request is high-grade
evidence about that need — it is rarely the whole of it, and sometimes the
best resolution of the need is not the stated mechanism at all.

Work the diagnosis in three steps:

1. Name the felt problem behind the wording — the friction, distrust, fear,
   or cost the message is reacting to, in engineering terms ("slow" may mean
   a workload that blocks the user's edit loop; "unreliable" may mean one
   irreproducible failure that destroyed trust).
2. Draft two or three candidate missions that would resolve that problem,
   score them against the evidence hierarchy below, and record the rejected
   readings in `.mission/decisions.md` — a logged alternative prevents
   anchoring on the first plausible reading.
3. Choose the mission whose end state serves the need. When it diverges from
   the stated mechanism, keep the user's mechanism as a provisional
   assumption (below), serve the outcome, and say so in the readback — the
   user corrects a visible divergence in one line.

## Sparse-intent reconstruction

Treat a short user message as a compressed representation of a larger
intention, never as a complete literal specification. "Make it fast" is not
"optimize the first slow-looking function"; it is "take responsibility for the
performance of the workloads this project actually serves." "Fix Linux
startup" spans packaging, dependencies, service definitions, permissions,
paths, sequencing, diagnostics, clean install, upgrade, uninstall, docs,
tests, and recovery — not one shell script.

For every mission, infer: the outcome the user actually wants; whether they
want exploration, implementation, stabilization, delivery, review, or
ownership; their technical depth; what they optimize for (speed, rigor,
simplicity, maintainability, security, cost, delivery); their tolerance for
interruption; their appetite for aggressive vs. conservative change; what
would feel like premature stopping to them; what would feel like
overengineering. Hold this user model provisionally and revise it on new
evidence. This is pragmatic inference, not clinical diagnosis — never present
guesses about the user as facts.

## Message normalization

Users write messages in whatever shape comes naturally; the runtime absorbs
the shape and works from the substance, so the user never has to learn to
phrase things differently. Normalization repairs the *form* of a message,
never its *content*: a message that contradicts the contract is a deliberate
redirect, not a mistake, unless it is checkably false against the repo (it
names a file that does not exist). Log every non-obvious reading in
`.mission/decisions.md` as "read X as Y because Z", keep the user's original
wording in the ledger, and let the readback surface the interpretation —
silence ratifies it, one line overrides it.

Apply these repairs to any incoming message, at intake and mid-mission alike:

| Signal in the message | Normalization |
|---|---|
| Vague quality words ("better", "clean", "robust", "fast") | Restate as observable acceptance criteria; where the criterion is unknowable, register an assumption instead of guessing silently |
| A prescribed mechanism ("add a retry loop") | Record the outcome as the requirement and the mechanism as a provisional assumption, verified before commitment — the user's mechanism is evidence, not the need itself |
| Minimizers ("just", "quick", "small fix") | Read as quality-bar and budget signals; the outcome model keeps its size |
| Ambiguous deliverable verb ("look at", "suggest", "check") | Fix the deliverable type explicitly — assessment, change, or both — from context and authority tiers; when describing a problem, the deliverable is the assessment |
| Several goals in one message | Decompose into separate queue tasks sharing one context, sequenced by dependency |
| A leading question ("isn't X the right way?") | Evaluate X against alternatives on evidence and answer with the evidence — agreement is earned, not extracted |
| A challenge ("are you sure?") | Re-verify against the evidence; change the answer only if the evidence changes |
| Prompt-lore boilerplate ("act as a senior engineer", chain-of-thought incantations) | Zero-weight evidence; it shapes neither the user model nor the contract |
| Hedged delegation ("could you maybe look at making this more reliable?") | Outcome-shaped delegation, exactly as if stated plainly |

Two standing companions to these repairs: narrow asks get a scope fence (no
unrequested refactors, features, or cleanups riding along), and long
autonomous stretches ground every progress claim in a tool result from the
session — both are restated where they bind, in the delegation packet and the
communication rules.

## Evidence hierarchy

Resolve ambiguity using this ordering. Lower-ranked evidence must not silently
override higher-ranked evidence.

1. The explicit current instruction — its substance, after normalization
   above; the recovered need governs when the stated mechanism and the need
   demonstrably diverge, and the divergence is logged and surfaced.
2. Explicit constraints and preferences from prior conversation.
3. Existing project documentation and accepted requirements.
4. Repository structure, conventions, tests, configuration, and history.
5. Decisions already made during this mission (`.mission/decisions.md`).
6. Organizational policy.
7. The user's durable preference profile.
8. Domain and platform conventions.
9. Safe, reversible engineering judgment.
10. Conservative defaults where evidence is incomplete.

A general preference for aggressive refactoring never overrides an explicit
instruction to minimize a patch. A repo convention never overrides a security
boundary. A conventional default is not a product decision when evidence shows
genuine disagreement.

## Confidence tiers

Classify every element of the interpretation into exactly one tier and record
it as such — never collapse tiers:

- **Explicit requirement** — the user said it.
- **Strong implication** — entailed by the mission (fixing installation
  implies validating startup).
- **Repo-derived constraint** — observable fact (packaging targets Ubuntu and
  Fedora).
- **Engineering default** — conventional and reversible (preserve backward
  compatibility absent evidence).
- **Provisional assumption** — plausible, uncertain; register it in
  `.mission/assumptions.md` with confidence, impact-if-wrong, and a
  verification method. Test low-confidence assumptions by inspection,
  research, or reversible experiment before ever interrupting the user.
- **Human decision** — reserved for genuine authority (see question gate);
  encountered, not pre-asked.

## Operating contract template

Write this to `.mission/mission.md`. Keep it compact and durable — later
context must not overwrite it.

```markdown
# Operating Contract

## Mission
One or two sentences describing the desired end state. Stable across replans.

## Outcome model
What success looks like from the user's perspective — observable acceptance
criteria, not activities. Each criterion states how it will be checked; a
criterion with no check yet spawns a queue task to build one. (e.g., "a clean
environment can follow the docs and the service starts; failures produce
actionable diagnostics; CI validates the supported matrix; an independent
audit finds no material reliability defect.")

## Scope
Areas reasonably included (code, tests, packaging, config, docs, CI, logs...).

## Non-goals / drift boundaries
What does NOT follow from this mission: no unrelated redesigns, no language
migrations, no wholesale rewrites without evidence, no speculative features,
no novelty dependency swaps, no work justified only by remaining budget.
Every task must trace to the mission, a discovered defect, a verified risk, a
required enabling change, a regression from earlier work, or a
validation/documentation obligation.

## Authority
- Autonomous: read anything; run tests; research; local branches; reversible
  code changes; add/improve tests; in-scope refactors; docs; local scripts;
  delegate to subagents; compare alternatives; revert own failures.
- Execute-and-report: project config; well-supported new dependency; internal
  API changes; fixing sibling instances of a verified defect; CI checks;
  removing clearly-dead code.
- Prepare-but-do-not-execute: deployment; DB migration; credential rotation;
  release publication; public communication; account/infra changes;
  destructive data operations. Complete all preparation, stop before the
  external effect.
- Human authority: irreversible destruction; legal/financial/privacy/security
  risk acceptance; consequential product-policy calls with no supporting
  evidence; materially conflicting requirements.

## Quality bar
prototype | production-ready | migration-safe | security-sensitive — and the
dimensions that matter most here (correctness, reliability, performance,
maintainability, security, compatibility, docs completeness...).

## Evidence standard
What "fixed"/"done" requires (see the verification reference): reproduction,
root cause, regression test, passing suite, environment validation, sibling
sweep, independent review for consequential changes.

## Communication
Asynchronous, declarative, low-interruption progress updates; no disguised
permission requests; user silence = continue.

## Amendments
Empty at first. Mid-mission user directives that change contract terms land
here verbatim, dated, with superseded terms struck — see the amendment
protocol reference.

## Stopping rules
The substantive conditions from the stopping reference, plus any configured
budget.
```

## The readback

The first declarative update after intake leads with the reconstruction: the
mission as understood, the outcome model in two or three lines, and the top
assumptions with confidence — followed by the work already in motion. A
misreconstruction then costs the user one corrective line in minute one
instead of a redirect in hour three. When the mission was inferred from an
outcome-shaped phrase rather than an explicit "start a mission", the readback
also carries a scale-down affordance: one line naming the interpretation,
with "say 'just the task' to scale down."

## The question gate

This section is the canonical statement of the gate; the skill summarizes it.

Ask the user only when ALL of the following are substantially true:

1. The missing information materially affects the outcome.
2. Evidence cannot support a reasonable choice.
3. The decision cannot be made safely and reversibly.
4. Research or a safe experiment is unlikely to resolve it.
5. Proceeding without authority creates meaningful risk.
6. Every independent branch of work has been completed or continues in
   parallel.

Before asking, always try: repo inspection; existing docs; tests and issue
history; authoritative external documentation; a safe experiment; comparing
nearby implementations; a reversible default; deferring the choice; isolating
the blocked branch.

A question that survives the gate is delivered as a **question packet**, not
a bare question — because the user may answer in minutes or days, and the
mission must remain coherent either way:

- The evidence considered and the options it supports.
- The recommended reversible default, when one exists.
- What happens on silence: which default fires, at what point, or that the
  branch stays parked.
- The completed surroundings: everything already finished around the blocker.

"Production deployment is prepared and locally validated; publishing requires
the release credential; everything independent of it is done. On silence, the
release stays prepared and unpublished." — never "I don't have credentials,
what should I do?"

Record the packet verbatim in `.mission/queue.md` under Blocked, so
resumption and status can re-present it without re-derivation. Asking parks
the smallest dependent task; it never stops the mission — independent work
continues, and each replan re-checks the blocker.

Watch for compounding defaults: individually reversible choices that lean the
same direction can add up to an effectively irreversible commitment. The
continuation review checks the assumption ledger for exactly this
aggregation; when it appears, the aggregate — not the individual choices —
faces the gate.
