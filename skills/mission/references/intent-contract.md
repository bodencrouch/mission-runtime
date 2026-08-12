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
- [Non-blocking questions](#non-blocking-questions)

## The need behind the ask

A request usually names a mechanism; the mission serves the need. Before
scoping anything, recover the situation that made the user write: what hurts,
what they would recognize as "this is what I wanted", what would stop the
complaint recurring. The stated request is high-grade evidence about that need,
rarely the whole of it, sometimes not the best resolution of it.

Work the diagnosis in three steps:

1. Name the felt problem behind the wording — the friction, distrust, fear,
   or cost the message is reacting to, in engineering terms ("slow" may mean
   a workload that blocks the user's edit loop; "unreliable" may mean one
   irreproducible failure that destroyed trust).
2. Draft two or three candidate missions that would resolve that problem,
   score them against the evidence hierarchy below, and record the rejected
   readings in `.mission/decisions.md` — a logged alternative prevents
   anchoring on the first plausible reading.
3. Choose the mission whose end state serves the need. Divergence from the
   stated mechanism is normalized below and named in the readback, where the
   user corrects it in one line.

## Sparse-intent reconstruction

Treat a short user message as a compressed representation of a larger
intention, never as a complete literal specification. "Make it fast" is not
"optimize the first slow-looking function"; it is "take responsibility for the
performance of the workloads this project actually serves." "Fix Linux startup"
spans packaging, dependencies, service definitions, permissions, paths,
sequencing, diagnostics, install, upgrade, uninstall, docs, tests, and recovery
— not one shell script.

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
`.mission/decisions.md` as "read X as Y because Z" and let the readback surface
the interpretation — silence ratifies it, one line overrides it. The user's own
wording is preserved verbatim in the contract's Original request section.

Apply these repairs to any incoming message, at intake and mid-mission alike:

| Signal in the message | Normalization |
|---|---|
| Vague quality words ("better", "clean", "robust", "fast") | Restate as observable acceptance criteria; where the criterion is unknowable, register an assumption instead of guessing silently |
| A prescribed mechanism ("add a retry loop") | Record the outcome as the requirement and the mechanism as a provisional assumption, verified before commitment — the user's mechanism is evidence, not the need itself |
| A prescribed route ("spawn three agents", chain-of-thought rituals, demands to expose deliberation) | Treat as a prescribed mechanism for the *route*: record the outcome plus the signals the phrasing carries — desired rigor, visibility — and choose the route on evidence, because route habits are usually tuned to some other model's weaknesses; the substance ports, the choreography does not. Serve visibility asks with evidence and conclusions in the deliverable, never a transcript of deliberation. An explicit approval hold ("propose a plan and wait for my OK") is authority, not route: it is content, recorded in the contract's Authority tiers and honored. Surface either reading in the readback |
| Minimizers ("just", "quick", "small fix") | Read as quality-bar and budget signals; the outcome model keeps its size |
| Ambiguous deliverable verb ("look at", "suggest", "check") | Fix the deliverable type explicitly — assessment, change, or both — from context and authority tiers; when describing a problem, the deliverable is the assessment |
| Several goals in one message | Decompose into separate queue tasks sharing one context, sequenced by dependency |
| A leading question ("isn't X the right way?") | Evaluate X against alternatives on evidence and answer with the evidence — agreement is earned, not extracted |
| A challenge ("are you sure?") | Re-verify against the evidence; change the answer only if the evidence changes |
| Persona and prompt-lore boilerplate ("act as a senior engineer", "you are an expert", chain-of-thought incantations) | Zero-weight evidence; it shapes neither the user model nor the contract |
| Intensity language ("be thorough", "really dig into this", "do it properly") | A depth signal, not content: raise the dispatch depth and the verification tier for the affected work. It does not travel into a commission as prose |
| A prescription about the runtime's own method ("spawn five agents", "plan before you touch anything", "use a specific model") | A method preference: honor it where the host supports it and it costs nothing, otherwise hold it as a provisional assumption and let the outcome govern — logged like any other reading |
| Hedged delegation ("could you maybe look at making this more reliable?") | Outcome-shaped delegation, exactly as if stated plainly |

Three repairs bind at dispatch rather than here: the scope fence on a narrow
ask; grounding progress claims in tool results; and the normalized substance,
never the original wording, that travels into a commission — the runtime
absorbs the phrasing so the user never has to supply a well-formed prompt.
The commission reference states them where they bind.

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

The first four tiers are the contract's provenance tags — `[stated]`,
`[entailed]`, `[repo: <file>]`, `[default]` — one per acceptance criterion and
non-goal. An untagged constraint is removed rather than debated: a constraint
nobody can source is a hallucinated requirement, the failure the agent-error
taxonomy names sub-intention redundancy (task-irrelevant sub-goals). Checks on
a tag run one way — a failed faithfulness or entailment check demotes its
constraint to "needs a provenance tag or removal", a passed one certifies
nothing, because factuality metrics are biased against heavy paraphrase over
distant context (the shape of an expanded contract) and the best detectors
reach about 84% balanced accuracy. Agreement across independently generated
readings is not evidence either: models run 67–82% self-consistent even on
genuinely under-specified input.

## Operating contract template

Write this to `.mission/mission.md`. Two budgets keep it durable against later
context: at most seven acceptance criteria, and 120 lines for the whole file.
Past the cap, a new criterion displaces an existing one instead of appending.
Instruction-following degrades monotonically with instruction count (a
regression on count alone predicts performance within about 10% error), and
long context loses recall at every length increment, not only near the limit.
Seven and 120 are starting values set by analogy, unmeasured for this runtime,
open to recalibration from its own data. The Original request slot is the one
section no replan rewrites: committing to an early reading with no path back to
the source is the dominant long-conversation failure — a 39% average drop
across 200,000+ conversations, nearly all of it added unreliability rather than
lost capability.

```markdown
# Operating Contract

## Original request
The user's message, verbatim. No replan rewrites this section.

## Mission
One or two sentences describing the desired end state. Stable across replans.

## Outcome model
Observable acceptance criteria, not activities — at most seven, each with one
provenance tag and a stated check. A criterion with no check yet spawns a queue
task to build one. (e.g., "a clean environment follows the docs and the service
starts [stated]; failures produce actionable diagnostics [entailed]; CI
validates the supported matrix [repo: .github/workflows/ci.yml]; no material
reliability defect survives an independent audit [default]")

## Scope
Areas reasonably included (code, tests, packaging, config, docs, CI, logs...).

## Non-goals / drift boundaries
What does not follow from this mission, each tagged like the criteria: no
unrelated redesigns, no language migrations, no rewrites without evidence, no
speculative features, no novelty dependency swaps, no work justified only by
remaining budget. Every task traces to the mission, a discovered defect, a
verified risk, a required enabling change, a regression from earlier work, or a
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
- Action boundary: an informational request is answered with findings, an
  implementation request with changes. Turning the first into the second is
  an amendment, not initiative.

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

The first declarative update after intake leads with the reconstruction, in
full rather than summarized: the mission, every outcome-model criterion with
its provenance tag, scope and non-goals, and every assumption with its
confidence — followed by the work already in motion. Full restatement is the
one that recovers what partial restatement does not: the multi-turn study
above found a 39% average drop from splitting a single instruction across
turns, and restating the complete accumulated instruction closed most of the
gap where restating only part of it closed little. The constraint budget
above is what makes "full" cheap enough to say once — a capped contract fits
a readback. A misreconstruction then costs one corrective line in minute one
instead of a redirect in hour three. When the mission was inferred from an
outcome-shaped phrase rather than an explicit "start a mission", the readback
also carries a scale-down affordance: one line naming the interpretation,
with "say 'just the task' to scale down."

Before it goes out, run the round-trip check: from the finished contract alone,
original message set aside, re-derive the one-sentence request it implies and
compare that sentence to what the user wrote. Divergence is logged in
`.mission/decisions.md` and surfaced in the readback. Round-trip correctness is
the one fidelity check validated without a reference answer, and the comparison
localizes the drift rather than merely detecting it. A divergence demotes the
constraints that caused it, under the one-way rule above.

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

Before asking, exhaust the cheaper routes: repo inspection; docs; tests and
issue history; authoritative external documentation; a safe experiment; a
nearby implementation; a reversible default; deferral; isolating the branch.

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

## Non-blocking questions

This is the non-blocking channel, distinct from the gate above: it rides
on the readback, its defaults are already in force, and the work is already
moving. Nothing waits on an answer. A question that meets the gate's six
conditions is a blocking packet instead; this section relaxes none of them.
(Not to be confused with the calibration reference — that calibration is the
runtime tuning its own emission to the observed model and host; this is the
user-facing, optional-answer channel.)

A non-blocking question qualifies on four counts:

| Qualifier | Basis |
|---|---|
| It names the decision its answer changes | A question that names no decision is not asked |
| Its answer is not derivable from the repo, tests, docs, or history | Deriving beats asking on both cost and reliability |
| Inspection came first | Exploration-first questioning outperformed immediate upfront questioning, which risks asking for specifics beyond what the user knows |
| Its question type is new this mission | A repeat carries a recorded reason |

Nine framing mistakes disqualify a question: generic or domain-independent; too
long; jargon; technical rather than domain-level; mispitched for this user's
demonstrated depth; several requirement types mixed into one; vague with
several readings; vague with no clear reading; and the load-bearing one —
asking for a solution rather than a need, which collects a preference the user
has not reasoned through. Unguided questions rate at human parity, while
questions written against this list beat human-written ones significantly.

A delegated agent cannot ask the user anything — the asking tool does not exist
inside a subagent. A specialist returns the question upward in its report, and
the orchestrator owns the ask.
