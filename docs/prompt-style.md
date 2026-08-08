# Prompt style guide

How to write instruction files in this repository: skills (`SKILL.md`),
reference docs, agent definitions, `CLAUDE.md`, and the manifests'
descriptions. Rewrites and reviews check against this document. Every rule
carries a source tag; the key is at the end. Rules that are house judgment
rather than sourced guidance say so.

## Contents

- [The one test](#the-one-test)
- [Framing](#framing)
- [Altitude](#altitude)
- [Register](#register)
- [Model-agnostic emission](#model-agnostic-emission)
- [Structure](#structure)
- [Examples](#examples)
- [Skills](#skills)
- [Agents](#agents)
- [CLAUDE.md and user-facing docs](#claudemd-and-user-facing-docs)
- [Checking a prompt change](#checking-a-prompt-change)
- [Sources](#sources)

## The one test

Every sentence must survive: *would removing this cause a mistake?* If not,
cut it. Bloated instruction files cause the model to miss the rules that
matter. [CCBP] Minimal means fully specifying, not short. [CE] Assume the
reader model is already smart: add only what it cannot know — this
project's contracts, schemas, and boundaries — never general engineering
wisdom or self-evident practice. [SBP][CCBP]

## Framing

State the desired behavior affirmatively, and give the reason. The model
generalizes from rationale; a bare rule invites literal, brittle
compliance. "Append to the ledger as events happen, so a dead session
loses minutes of state, not hours" beats "Don't defer ledger updates."
[C4BP][F5]

Reserve blunt prohibitions for the narrow bridges — actions that are
irreversible, fragile, or integrity-critical. There, a prohibition with its
rationale is the correct tool; keep it blunt and do not soften it for
style. [SBP][C4BP] This repository's narrow bridges:

- The recorder exits 0 on every path; recording never blocks a session.
- Telemetry never leaves the machine.
- Read-only agents do not write; the `tools:` list enforces it, prose
  explains it.
- `.mission/` stays out of version control via `.git/info/exclude`, never
  the project's `.gitignore`.
- No dependencies beyond the Python 3 standard library.
- No hand-written telemetry records while hooks are live.
- Host transcript files are never parsed.

Where a guarantee can be enforced mechanically — a tool list, a hook, a
test — enforce it there and let the prose explain the mechanism. Prose is
advisory; mechanisms are deterministic. [CCBP][SA]

Numbers and thresholds carry a stated basis. An unexplained constant is one
the model cannot apply well or adapt correctly. [SBP]

## Altitude

Write heuristics with a boundary example, not case enumerations. Current
models degrade under over-prescription: a short principle steers better
than a list that tries to name every case. [F5][CE]

Calibrate specificity to fragility ("degrees of freedom") [SBP]:

| Freedom | Use for (this repo) | Form |
|---|---|---|
| High | prioritization, replanning, intent reconstruction | principles + one example |
| Medium | delegation packets, the operating contract | template with slots |
| Low | ledger schemas, telemetry record shape, test and doctor commands | exact template, exact command |

## Register

Normal prose register. Emphasis capitals ("IMPORTANT", "YOU MUST",
"ALWAYS") are not house style; on current models they cause overtriggering,
and official tooling calls all-caps rules a yellow flag. Escalate emphasis
only as a recorded repair for an observed miss. [F5][SC]

Never write anti-laziness prompting ("if in doubt, do X", "proactively",
"aggressively") — written for older models, it now causes overtriggering.
[C4BP]

Never instruct a model to echo, transcribe, or explain its internal
reasoning; ask for evidence and conclusions instead. Reasoning-echo
instructions can trigger refusals on current models. [F5]

## Model-agnostic emission

Two audiences read what this repository produces: the model running the
runtime, and the models the runtime dispatches. Neither is known when the
files are written, so no runtime surface names a model or model family,
asserts what "current models" need, or tunes its scaffolding to a capability
level. A capability claim frozen into a prompt file cannot be observed, cannot
be retired, and is wrong the moment the host changes its default. Sourced
findings about specific model behavior belong here, in this guide, as a rule
with a tag; the runtime surfaces carry only the behavior. (House rule; the
conformance suite greps skills, agents, and references for model names.)

The corollary for authors: name the failure any new scaffolding repairs.
Scaffolding whose failure cannot be named is scaffolding the next model will
not need, and prescription that a model has outgrown lowers output quality
rather than protecting it. At run time the same principle is a mechanism —
the ratchet in `skills/mission/references/calibration.md` adds packet detail
only against an observed miss and retires it when the returns stop showing
one. [F5][CE]

## Structure

Markdown headers delineate sections; sibling files keep the same section
shape so a reader (human or model) knows where to look. XML tags appear
only to delimit examples or variable content inside a prompt. [C4BP][CE]

Numbered lists only where order or completeness matters; otherwise prose or
bullets. [C4BP] In delegation packets and long prompts, bulk context comes
first and the ask comes last. [C4BP]

One term per concept, everywhere:

| Concept | The term |
|---|---|
| Outcome-shaped job | mission |
| Bounded work item | task |
| `.mission/mission.md` | the contract |
| `.mission/` files | ledgers |
| `.mission/state.md` | the resume capsule |
| A delegation's full brief | packet |
| An agent's returned output | report |
| `~/.missionruntime/` | the store |
| Loop stages | interpret, inspect, model, queue, execute, verify, update memory, generate follow-ups, replan |

("Learn" is not a stage name; use "update memory" and "generate
follow-ups".) [SBP: consistent terminology]

## Examples

One canonical worked example of an artifact (a filled packet, a queue
entry, a decision record) teaches more than a paragraph of schema prose.
Use 3–5 diverse, canonical examples at most; never accumulate edge-case
laundry lists. [C4BP][CE][SBP]

## Skills

**Description (frontmatter).** The trigger surface. Third person, always.
What the skill does + when to use it, with concrete quoted trigger
phrases; the strongest trigger first; at most 1,024 characters; no XML
tags. Include boundaries ("a bounded micro-task is just done, without the
runtime") so the skill also knows when to stay quiet. Be deliberately
generous with trigger phrases — undertriggering is the documented default
failure mode. [SBP][SC][CCS]

**Body.** Under 500 lines; ~2,000-word target. Imperative, verb-first
instructions (skill bodies speak to the runtime; second person is for
agents). The body is a table of contents that carries the standing rules
and points to references for depth — information lives in the body or a
reference, never both. Standing rules go in the first ~5,000 tokens: that
is what gets re-attached after context compaction. [SBP][PD][CCS]

**References.** One level deep. Every reference is linked from SKILL.md
exactly once, with when-to-read guidance ("Read `references/stopping.md`
after each deliverable"). A reference over 100 lines opens with a table of
contents. References do not link to each other — they name concepts, and
SKILL.md owns the map. [SBP]

**Paths.** SKILL.md links its own references as `references/<file>.md`.
Other skills reach them as
`${CLAUDE_PLUGIN_ROOT}/skills/mission/references/<file>.md`. `CLAUDE.md`
uses full repo-relative paths. (House rule; fixes observed drift.)

## Agents

**Description.** Plain prose, current official style — not transcript
`<example>` blocks: state the capability, 2–4 trigger scenarios, a
proactive cue, and when *not* to invoke. Descriptions for all agents load
whenever the plugin is registered, so brevity here is paid for nine times
over. [SA][PD]

**Body.** Second person. Shape: role → method → quality bar → required
report format, ending on the report format. 500–3,000 characters works
best. A short "When to invoke" bullet list in the body carries the worked
scenarios that used to live in `<example>` blocks. [SA][PD]

**Frontmatter.** `tools:` is always declared, least privilege — omitting
it grants everything. Leave `Agent` out of the list so specialists cannot
sub-delegate. `hooks`, `mcpServers`, and `permissionMode` are ignored for
plugin agents; never rely on them. `model: inherit` unless a measured
reason says otherwise. Colors come from: red, blue, green, yellow, purple,
orange, pink, cyan. [SA]

**CLAUDE.md awareness.** Subagents load the project's CLAUDE.md. An agent
body that restates a CLAUDE.md rule in different words creates a live
conflict inside the agent's context — reference the rule or trust it, and
never restate it divergently. [SA][CCS]

**Shared boilerplate.** A sentence that must appear in many agent files
(report-delivery protocol, read-only note) has one canonical wording,
recorded here or in the delegation reference, and is copied exactly.
(House rule; nine-way copy-paste drift was observed.)

## CLAUDE.md and user-facing docs

`CLAUDE.md` holds facts and conventions — what is true about this repo and
what its tests enforce. Procedure belongs to the skills; when a CLAUDE.md
section grows into a procedure, it moves into a skill or reference and
leaves a pointer. It obeys the same removal test as everything else.
[CCS][CCBP]

`README.md` and all user-facing text: plain language. Short sentences, one
idea per sentence, no metaphors, no buzzwords, verb-first headings — clear
to a smart fifteen-year-old. (House rule.)

The manifests duplicate the plugin description on purpose; a description
change lands in `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` together. [CCP]

## Checking a prompt change

1. `python3 -m unittest discover -s tests` — exactly this command; the
   suite guards hook invariants and manifest structure, and
   `test_runtime_conformance.py` mechanically enforces most rules in this
   guide (frontmatter shape, tool boundaries, link counts, hazard greps).
2. `claude plugin validate . --strict` where the CLI is available. [CCP]
3. Grep the changed files for the five hazards: reasoning-echo phrasing,
   emphasis capitals, anti-laziness prompts, "think hard" rituals, and model
   or model-family names in a runtime surface. All five counts were zero at
   baseline (2026-08-07) and stay zero.
4. Cross-references resolve; the terminology table is respected; every
   skill description keeps or strengthens its concrete trigger phrases.
5. For consequential rewrites: a fresh-context adversarial review, told to
   flag only gaps that affect correctness or the stated requirements —
   reviewers prompted merely to "find gaps" will invent some. [F5][CCBP]

## Sources

| Tag | Source |
|---|---|
| C4BP | platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices |
| F5 | platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5 |
| SBP | platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| CE | anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| CCBP | code.claude.com/docs/en/best-practices |
| CCS | code.claude.com/docs/en/skills |
| SA | code.claude.com/docs/en/sub-agents |
| CCP | code.claude.com/docs/en/plugins-reference |
| SC | skill-creator (Anthropic official plugin tooling) |
| PD | plugin-dev (Anthropic official plugin tooling) |
