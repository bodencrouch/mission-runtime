---
title: Commission Synthesis - Plan
type: feat
date: 2026-08-12
topic: commission-synthesis
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-brainstorm
execution: code
---

# Commission Synthesis - Plan

## Goal Capsule

**Objective.** Make the generation of specialist briefs the spine of the
mission flow: every mission derives the commissions its own objective demands,
each one validated before dispatch, with no drift from what the user asked for.

**Product authority.** `STRATEGY.md` (Intent reconstruction; Role synthesis and
briefing). Evidence base: `.mission/notes/002`, `003`, `004`.

**Open blockers.** None.

## Product Contract

### Summary

The runtime gains a synthesis stage between the contract and dispatch. It emits
a **commission** — one typed artifact carrying both the role and the brief for
a unit of delegated work — and validates it mechanically before anyone acts on
it. The nine existing agents stop being the routing space and become
**chassis**: authority capsules that a commission runs on.

### Problem Frame

Intake already recovers intent well and writes a contract. Everything after
that hands work to one of nine fixed agents using a nine-slot template that
nothing validates. The value the product promises — the runtime doing the
prompt engineering — stops at the contract and never reaches the briefs.

Three measured facts set the shape of the fix. Agents disobey their *task*
specification about 22× more often than their *role* specification, so
comprehensiveness belongs in the specification, not in persona prose. Step
repetition is the single largest failure mode in the field's only validated
failure taxonomy, and it comes from briefs that do not say what their siblings
own. And expansion of a sparse request is only reliably positive when it
produces structure the model would not default to — added prose is a coin flip.

### Key Decisions

- **Commissions, not personas.** Role and brief are one generated artifact
  with one gate. Persona framing gets exactly one sentence, because the
  measured accuracy benefit of a persona is ~0 and the docs endorse it only
  for behavior and tone. _Governs R1, R2, R11._
- **Expansion adds structure, never volume.** Every generated surface adds
  typed slots, not paragraphs. _Governs R1, R12, R16._
- **Chassis over roster.** The nine agents become authority capsules; the
  commission varies per mission. This gets per-task specification without
  role drift, and without depending on writing agent files at runtime.
  _Governs R7, R8._
- **Mechanical checks before judgmental ones.** LLM self-verification of
  plans produced 38 false positives per 100; the first gate must be decidable
  without a model. _Governs R3, R4, R5, R6._
- **Fidelity checks are asymmetric.** A failed entailment check demotes a
  constraint; a passed one certifies nothing. Agreement across independent
  expansions is not evidence of faithfulness. _Governs R14._
- **Calibration is not the question gate.** The blocking gate stays as it is.
  A separate non-blocking channel carries optional, defaulted questions.
  _Governs R17, R18, R19._

### Requirements

**The commission artifact**

R1. A commission carries nine slots and no free prose outside them: identity
(one sentence), objective (one sentence, outcome-shaped), context, scope,
non-goals and what siblings own, authority, evidence standard, output
contract, budget.

R2. The identity slot is one sentence naming domain and scope, with no
superlatives and no claim of infallibility.

R3. A commission is self-contained: every file path, error string, prior
decision, and prior finding the agent needs appears in the commission itself
or at a path the agent can read. No referent may point outside it — no "the
file we discussed", "as above", "the earlier finding".

R4. The authority slot never exceeds the contract's authority tier for that
work, and never exceeds what the chassis's tool grant allows.

R5. The evidence standard names a check the agent can run, or records
explicitly that none exists. The bar is stated so a second reader can decide
whether it was met.

R6. The output contract enumerates the report's required sections and states
where the report lands.

R7. Every commission binds to a chassis whose tool grant satisfies its
authority slot.

R8. A commissioned role that matches no existing chassis semantics runs on a
role-neutral chassis inside the plugin's tool boundaries, never on an
unbounded general-purpose agent.

**The pre-dispatch gate**

R9. No commission dispatches until it passes a check that is decidable without
a model: all nine slots present and non-empty; self-containment; authority
within tier; output contract enumerated; tool grant non-empty.

R10. Across a set of commissions dispatched together: every acceptance
criterion in the contract is owned by exactly one commission; no two
commissions share an objective and scope; no two write-capable commissions
name overlapping files.

R11. Whenever more than one commission ships in the same message, each states
what the others own.

R12. A commission that fails the gate is repaired at the failing slot, not
regenerated.

**Drift control on the contract**

R13. The contract carries the user's original message verbatim in a section no
replan may rewrite.

R14. Every acceptance criterion and every non-goal carries a provenance tag:
stated by the user, entailed by the stated outcome, observed in the repo with
a file reference, or reversible engineering default. An untagged constraint is
removed rather than debated.

R15. The readback restates the contract in full rather than summarizing it,
and re-entry after a pause re-emits full terms rather than a delta.

R16. The contract has a bounded number of acceptance criteria and a line
ceiling. Past the bound, a new criterion displaces an existing one.

R17. Before the contract is accepted, the runtime re-derives a one-line
request from the contract alone and compares it to the user's original
message. Divergence is logged and surfaced.

**Calibration and questions**

R18. The readback may carry a small number of optional calibration questions.
Each names the decision its answer changes, states the default already in
force, and never blocks work.

R19. A generated question avoids nine named framing mistakes, of which the
load-bearing one is asking for a solution rather than a need.

R20. A question type is not repeated within a mission without a recorded
reason.

R21. A question is disqualified when its answer is derivable from the repo,
tests, docs, or history.

**Host reality**

R22. The mission skill states that a user's mission request is itself the
authorization to delegate.

R23. Generated commissions carry no standing verification-depth instruction,
because that guidance splits by model generation.

R24. A commission never instructs an agent to ask the user a question, because
the asking tool does not exist inside a subagent.

### Success Criteria

- `python3 -m unittest discover -s tests` passes, with new tests covering R1,
  R9, R13, R14, R16, and the chassis roster.
- The four hazard greps still return zero.
- Net line count across `skills/mission/SKILL.md` and `docs/prompt-style.md`
  does not grow, despite the added stage — the structure-not-volume rule
  applied to the runtime's own surfaces.
- Every rule added to a prompt surface traces to a research citation, a repo
  observation, or a recorded repair.

### Scope Boundaries

- No changes to the telemetry scripts beyond what a new record field requires.
- No new runtime dependencies.
- No rewrite of the stopping, amendment, or memory references except where
  commissions touch them.
- Agent proliferation is bounded: a new agent must earn its slot with a tool
  grant or charter the roster cannot already express. Current budget: one.
- Writing agent files at runtime is out of scope. It works on this host under
  conditions, and it is not the mechanism the design rests on.

### Dependencies / Assumptions

- The per-dispatch variable is the prompt text; the system prompt and tool
  grant are fixed in the agent file. Verified: `.mission/notes/001`.
- Persona framing carries no measured accuracy benefit. Verified against the
  primary source: `.mission/notes/003`.
- Interaction gains reported in the clarification literature are upper bounds,
  because every cited benchmark uses an LLM user simulator with ground-truth
  access. Carried as a caution: `.mission/notes/004`.

### Outstanding Questions

**Deferred to planning**

- The exact criterion cap and contract line ceiling. Starting values are a
  judgment call; the runtime's own telemetry can calibrate them later.
- Whether the calibration channel renders through the host's question tool or
  as plain text in the readback.

### Sources / Research

- `.mission/notes/001` — subagent mechanics, verified against
  code.claude.com/docs/en/sub-agents.
- `.mission/notes/002` — prompt and context engineering standards; the
  four-slot brief schema; the self-containment constraint.
- `.mission/notes/003` — persona efficacy, MAST failure taxonomy, chassis
  argument, counter-evidence on multi-agent cost.
- `.mission/notes/004` — expansion failure modes, drift-control mechanisms,
  question quality.

**Product Contract preservation:** unchanged. Planning added the sections below
and altered no requirement.

---

## Planning Contract

### Assumptions

- The criterion cap is 7 and the contract line ceiling is 120. Both are
  judgment calls set by analogy to the instruction-count degradation curve;
  neither is measured for this runtime. They are enforced mechanically so they
  can be recalibrated from telemetry later.
- Compressing the model-portability prose does not weaken the invariant,
  because the invariant is also enforced by the hazard greps and by the
  verification-depth rule this plan adds.
- Repo research for this plan ran inline rather than in a dispatched context.
  External research was independently dispatched; the repo reading was not, and
  carries no independent corroboration.

### Key Technical Decisions

**KTD1. `commission.md` is a new reference; `delegation.md` keeps routing.**
One rule, one owner. The commission artifact, its slots, and its gate live in
the new file. `delegation.md` keeps the chassis table, dispatch rules, the
integration protocol, and anti-patterns, and loses the work-packet template it
currently owns. _Governs R1–R12._

**KTD2. One new agent, read-only, role-neutral.** `commissioned-analyst` with
`Read, Grep, Glob, Bash, WebSearch, WebFetch`. It earns its slot because no
existing chassis offers a role-neutral read-only charter — running a
performance-profiling commission on `regression-investigator` puts the
commission's identity line in conflict with the agent body, which is the exact
failure the style guide's CLAUDE.md-restatement rule warns about. No
write-capable vessel is added: `implementation-engineer` is already
role-neutral ("executing a decided plan"). _Governs R8._

**KTD3. The gate is a checklist in prose plus assertions in the test suite.**
Prose is advisory; mechanisms are deterministic. Whatever can be checked
statically (slot presence in the template, roster/tool boundaries, contract
caps, provenance-tag vocabulary, hazard patterns) is a test. The set-based
checks over a live queue (coverage, disjointness, file overlap) cannot be
static, so they are stated as a checklist the orchestrator runs. _Governs
R9, R10._

**KTD4. Compression pays for the new stage.** SKILL.md's "Any model, any
phrasing" section and `prompt-style.md`'s "Model portability" section restate
one invariant across ~45 lines. Collapsing them funds the synthesis stage
within the existing line budget, which is the plan's own instance of
"expansion adds structure, never volume". _Governs the net-line success
criterion._

**KTD5. Verification-depth guidance is expressed as an invariant, not a
procedure.** "Consequential changes get an independent, non-authoring check"
holds on every model; "use a subagent to verify" is wrong on at least one.
_Governs R23._

---

## Implementation Units

### U1. Add the commission reference and re-scope delegation

**Goal.** Create the commission artifact and its pre-dispatch gate; remove the
work-packet template from `delegation.md` so one rule has one owner.

**Requirements.** R1–R7, R9–R12.

**Dependencies.** None.

**Files.**
- `skills/mission/references/commission.md` (new)
- `skills/mission/references/delegation.md` (modify)

**Approach.**
1. `commission.md` opens with a table of contents (over 100 lines), then: the
   nine slots with one line each; the chassis table mapping authority shape to
   agent; the pre-dispatch gate as a numbered checklist split into per-commission
   checks and across-commission checks; one filled worked example.
2. The self-containment rule (R3) states the reason — a subagent sees none of
   the conversation, none of the files already read — because the rule is
   otherwise easy to rationalize away.
3. `delegation.md` drops its `## Work packet` section, gains a pointer to
   `commission.md`, and keeps roster, dispatch rules, integration, anti-patterns.
   Rename its roster section to chassis and add the authority-shape column.
4. Add `NON-GOALS / OWNED BY OTHERS` to the slot list, with the sibling rule.

**Patterns to follow.** Existing reference shape: ToC, `##` sections, one
canonical worked example. `verification.md`'s numbered-standard style.

**Test scenarios.**
- `commission.md` is linked from `skills/mission/SKILL.md` exactly once.
- Every one of the nine slot names appears in `commission.md`.
- `delegation.md` no longer contains a second work-packet template (no
  duplicate slot-name block across the two files).
- The four hazard greps return zero on both files.
- Covers R11: the sibling-ownership rule appears in the slot list.

**Verification.** `python3 -m unittest discover -s tests` passes; the
exactly-once reference-link test covers the new file without modification.

---

### U2. Add the role-neutral read-only chassis

**Goal.** Give a commissioned role that fits no existing specialty a vessel
inside the plugin's tool boundaries.

**Requirements.** R8, R4.

**Dependencies.** U1.

**Files.**
- `agents/commissioned-analyst.md` (new)
- `tests/test_runtime_conformance.py` (modify — add to `READ_ONLY_AGENTS`)
- `skills/mission/references/delegation.md` (modify — chassis table row)

**Approach.** Body follows the house shape: role → When to invoke → method →
discipline → report format. The body states that its role comes from the
commission and that it may narrow its authority but never widen it past the
tool grant. Description is prose, names the when-not-to (a rostered specialist
fits → use it).

**Test scenarios.**
- Frontmatter name matches filename; color is in the valid set.
- `tools` declared, excludes every write tool, excludes `Agent`.
- Description contains no `<example>` block.
- Appears in the delegation roster (existing test enforces this).
- Body carries no hazard pattern.

**Verification.** Suite green; roster test passes with the agent added to
`READ_ONLY_AGENTS`.

---

### U3. Drift controls and the calibration channel in the contract

**Goal.** Make the contract resist drift mechanically, and give the readback a
non-blocking way to ask.

**Requirements.** R13–R21.

**Dependencies.** None.

**Files.**
- `skills/mission/references/intent-contract.md` (modify)

**Approach.**
1. Contract template gains a `## Original request` section holding the user's
   message verbatim, marked as never rewritten by a replan.
2. Every acceptance criterion and non-goal carries one of four provenance tags.
   The tags reuse the existing confidence-tier vocabulary rather than inventing
   a parallel scheme.
3. Add the criterion cap and the displacement rule; add the line ceiling.
4. Add the round-trip check to the readback procedure: re-derive a one-line
   request from the contract alone, compare to the original, log divergence.
5. New `## Calibration` section, distinct from the question gate: optional,
   defaulted, non-blocking; each question names the decision it changes; the
   nine framing prohibitions; no repeated question type; the derivability
   disqualifier.
6. State the asymmetry: a failed fidelity check demotes a constraint; a passed
   one certifies nothing. State that agreement across expansions is not
   evidence.

**Execution note.** This file is already 256 lines and is the densest surface
in the repo. Add slots, not prose — cut where the new material makes an
existing paragraph redundant.

**Test scenarios.**
- The contract template contains `## Original request`.
- The four provenance tags appear as a named vocabulary.
- The calibration section is distinct from the question gate (both headings
  present, neither merged).
- Hazard greps zero.
- Covers R19: the nine framing prohibitions are enumerated.

**Verification.** Suite green; file length does not grow beyond its share of
the net-line budget.

---

### U4. Wire the synthesis stage into the skill body

**Goal.** Put commission synthesis in the loop, authorize delegation, and pay
for the additions by compressing the model-portability prose.

**Requirements.** R22, R23, and the linkage for R1–R12.

**Dependencies.** U1, U3.

**Files.**
- `skills/mission/SKILL.md` (modify)
- `skills/mission/references/control-loop.md` (modify)

**Approach.**
1. Add commission synthesis between queue and execute in the loop stage list,
   in both files. Ceremony scales with consequence, like every other stage.
2. Add one sentence stating that a user's mission request is the authorization
   to delegate.
3. Collapse "Any model, any phrasing" to a short paragraph; the invariant
   survives once and the verification-depth rule now carries its sharpest case.
4. Link `references/commission.md` exactly once.
5. Add the worker-count default (1 for what the orchestrator finishes in a
   handful of calls; 2–4 for a bounded comparison; more only on genuinely
   divided work) to `control-loop.md` beside the existing parallelism rules.

**Test scenarios.**
- Every reference including the new one is linked from SKILL.md exactly once.
- SKILL.md body stays under the 500-line ceiling.
- `metadata.version` still equals the plugin version.
- Hazard greps zero.

**Verification.** Suite green; net line count across SKILL.md and
`prompt-style.md` does not grow.

---

### U5. Persist the commissioned roles

**Goal.** A resumed mission re-instantiates the same team.

**Requirements.** R7, R10.

**Dependencies.** U1.

**Files.**
- `skills/mission/references/memory.md` (modify)
- `skills/mission-resume/SKILL.md` (modify)

**Approach.** Add a `roles.md` ledger with a compact schema (commission id,
chassis, objective, scope, owner status, note-file pointer). The resumption
protocol reads it after `queue.md` and treats an active commission the same way
it treats an Active queue entry — demoted, because no agent survives a session.
Full-restatement rule applies: re-entry re-emits complete contract terms.

**Test scenarios.**
- `memory.md` documents `roles.md` with the same schema style as the other
  ledgers.
- `mission-resume` references the roles ledger in its ordered read list.
- Covers R15: re-entry restates full terms rather than a delta.

**Verification.** Suite green.

---

### U6. Reviewer invariants

**Goal.** Express verification depth portably and give the critic a finding
type that prevents manufactured findings.

**Requirements.** R23.

**Dependencies.** None.

**Files.**
- `skills/mission/references/verification.md` (modify)
- `agents/adversarial-critic.md` (modify)

**Approach.** State the non-authoring invariant: the agent that produced a
change never verifies it. State the localized-repair rule: a failed criterion
is repaired at that criterion, not by regenerating the contract. Add the
asymmetry note for fidelity checks. In the critic, type findings as
correctness-affecting versus optional — the body already carries the
search-versus-report split, so this is an addition to the report format only.

**Test scenarios.**
- `verification.md` contains no standing "always verify" or "use a subagent to
  verify" phrasing.
- The critic's report format enumerates the two finding types.
- Hazard greps zero.

**Verification.** Suite green.

---

### U7. Correct and extend the style guide

**Goal.** Fix two defects found by research and encode the new sourced rules.

**Requirements.** Success criterion "every rule traces to a source".

**Dependencies.** U1–U6 (so the new rules describe what now exists).

**Files.**
- `docs/prompt-style.md` (modify)

**Approach.**
1. Replace the `C4BP` source row — the URL now redirects to the consolidated
   prompting-best-practices page. Add source tags for the pages this work drew
   on.
2. The claim that standing rules must sit in the first ~5,000 tokens to survive
   compaction carries three source tags and appears in none of them. Demote it
   to a house rule or cut it.
3. Add: the one-identity-sentence rule; the self-containment rule; the
   coverage-clause pairing; the no-standing-verification rule.
4. Resolve the proactive-cue conflict explicitly. Four agent descriptions carry
   "Use proactively", which the sub-agents docs recommend and the prompting
   page warns now overtriggers. Record the decision and its reason rather than
   letting the two rules coexist unreconciled.

**Test scenarios.**
- No source row points at a URL that redirects.
- The unsourced compaction claim is gone or marked house judgment.
- Hazard greps zero.

**Verification.** Suite green; `claude plugin validate . --strict` passes.

---

### U8. Tests, docs, and version

**Goal.** Make the new invariants mechanical and bring user-facing surfaces
into line.

**Requirements.** All — this is the enforcement unit.

**Dependencies.** U1–U7.

**Files.**
- `tests/test_runtime_conformance.py` (modify)
- `README.md`, `CLAUDE.md` (modify)
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (modify)
- `skills/*/SKILL.md` (modify — `metadata.version`)

**Approach.** Add assertions for: the commission slot vocabulary present in
`commission.md`; no duplicate slot-template block across references; the
contract template's `## Original request` and provenance tags; the four
framing-prohibition markers; the roster including the new chassis; no standing
verification phrasing in `verification.md`. Update the "nine specialists" count
in `README.md`, `CLAUDE.md`, and `prompt-style.md`. Bump to 0.5.0 in
`plugin.json` and in every skill's `metadata.version`; keep the two manifest
descriptions identical.

**Test scenarios.**
- Each new assertion fails against the pre-change tree and passes after.
- Manifest parity test still passes after the description edit.
- Version test passes across all four skills.

**Verification.** `python3 -m unittest discover -s tests` green;
`python3 scripts/mr_doctor.py` unaffected; `claude plugin validate . --strict`
passes.

---

## Verification Contract

- `python3 -m unittest discover -s tests` — the only test command; must be
  green with every new assertion present.
- The four hazard greps return zero across `skills/`, `agents/`, references,
  and `README.md`.
- `claude plugin validate . --strict` passes.
- Net line count across `skills/mission/SKILL.md` and `docs/prompt-style.md`
  does not exceed its pre-change total.
- Every reference under `skills/mission/references/` is linked from the mission
  SKILL.md exactly once.
- A new-assertion falsification check: each added test is confirmed to fail
  against the pre-change tree, so the suite is not passing vacuously.
- An independent adversarial pass over the finished change, in a fresh context,
  told to report only findings that affect correctness or the stated
  requirements.

## Definition of Done

- R1–R24 are each realized in a named file and covered by either a test or a
  stated checklist item.
- The suite is green and the new assertions are shown to be non-vacuous.
- The style guide carries no unsourced rule and no redirecting source URL.
- The plugin version and all skill versions match.
- The adversarial pass returns no blocking finding, or every blocking finding
  is resolved and re-audited.

## Risks

- **The fix becomes the disease.** This plan adds instruction surface to solve
  an instruction-quality problem. Mitigation: the net-line budget is a success
  criterion, not an aspiration, and KTD4 names where the budget comes from.
- **The gate is prose the runtime skips.** Mitigation: everything statically
  checkable is a test; the checklist covers only what genuinely cannot be.
- **Ceremony taxes small missions.** Mitigation: the synthesis stage scales
  with consequence like every other loop stage, and the worker-count default
  is 1.
- **The caps are guesses.** Mitigation: they are enforced in one place each, so
  recalibration is a one-line change, and the telemetry that would calibrate
  them already exists.
