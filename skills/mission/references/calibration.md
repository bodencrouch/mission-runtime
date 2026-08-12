# Model-Agnostic Execution and Capability Calibration

The runtime sits between however the user typed their message and whichever
model executes the work. Neither end is fixed. The same mission may run on a
model that needs its route drawn for it and on one that plans the work better
than any packet could. So the runtime holds no prior belief about which end it
is on: capability is observed during the mission and recorded, never declared
in advance, and nothing the runtime emits is tuned to a named model.

## Contents

- [What every emitted prompt fixes](#what-every-emitted-prompt-fixes)
- [Constructs the runtime does not emit](#constructs-the-runtime-does-not-emit)
- [The scaffolding ratchet](#the-scaffolding-ratchet)
- [Calibration signals and their repairs](#calibration-signals-and-their-repairs)
- [Depth is dispatch configuration](#depth-is-dispatch-configuration)
- [Host capability probe](#host-capability-probe)
- [Where calibration state lives](#where-calibration-state-lives)

## What every emitted prompt fixes

Every packet, retry, and self-instruction the runtime writes fixes five things
and deliberately leaves the sixth free:

| Element | Content |
|---|---|
| Destination | the outcome, as an observable end state |
| Reason | the governing principle behind it, so unenumerated cases resolve correctly |
| Terrain | state and evidence already established (pointers, not pastes) |
| Laws | invariants that must survive, and the scope fence |
| Evidence of arrival | what makes a claim of completion acceptable |
| *Free: the route* | which files to open, which searches to run, in what order, in how many steps |

Fixing the route as well caps a capable executor at the author's plan, and
teaches a weaker one nothing that the invariants and the evidence standard do
not already say. Route detail enters a packet only through the ratchet below,
as a repair for something already observed.

Stating the reason is load-bearing, not decoration. A rule reaches the cases
the packet forgot to name only when the principle travels with it: "the
serialized form is a compatibility surface consumed by tools outside this
repo" covers files that no do-not-touch list anticipated.

## Constructs the runtime does not emit

| Construct | Why it fails across the range of executors |
|---|---|
| A step-by-step route through work the packet already bounds | Caps a strong executor at the author's plan; adds nothing a weak one cannot get from the invariants |
| A request to narrate or reproduce how an answer was reached | Costs range from wasted tokens to an outright refusal depending on the executor, and the evidence standard already secures the auditable part |
| Intensity language ("try hard", "be exhaustive", "leave no stone unturned") | Carries no information the depth setting and evidence standard lack; an obedient executor inflates cost without changing the outcome |
| An enumerated permission list ("you may read files, you may run tests, …") | Always incomplete, and the omissions read as prohibitions. State the authority boundary as a rule instead |
| A fixed agent count or a mandated phase sequence | Parallelism follows from independence, and phases from dependency — neither from a number chosen in advance |
| A remaining-context countdown | An executor watching its own context spends the work budget on wrapping up; context is the orchestrator's to manage |
| A reporting threshold that also constrains searching ("only look for severe defects") | An obedient executor narrows discovery to match. Separate the two: search the whole scope, report by severity |
| A role preamble with no operative content ("you are a world-class engineer") | Zero weight on the outcome; it displaces the constraints that are not zero weight |

## The scaffolding ratchet

Default to the lean form of every packet. Add scaffolding only as a repair for
a miss observed in this mission, record the observation that justified it, and
retire it when it stops earning. Scaffolding carried "just in case" is
indistinguishable in the ledger from scaffolding that is load-bearing, and a
later session cannot tell which is which.

Three rules keep this a ratchet rather than a drift:

1. The repair is minimal and aimed at the observed defect — one packet field,
   not a template rewrite.
2. The repair names its observation: "delegate 4 refactored a module outside
   its scope; added an explicit do-not-touch list to writer packets."
3. The repair is scoped to the agent role or the task class the evidence
   supports. A repair applied to every packet on one observation over-fits.

Retirement is evidence-driven too: when a repair has ridden along for several
dispatches and nothing in the reports suggests it is still binding, remove it
and watch the next return. Removing one mechanism at a time is what keeps its
cost legible.

## Calibration signals and their repairs

| Observed in a report, a diff, or a run | Minimal repair |
|---|---|
| Work outside the packet's scope — drive-by refactor, unrequested cleanup, abstraction for a hypothetical need | Name the fence explicitly and add "no changes not required by the objective" |
| Findings returned when a change was wanted, or a change made when findings were wanted | Put the deliverable type in the packet's first line and re-check the action boundary |
| A conclusion with no file:line and no rerunnable command | Restate the evidence standard as the report's acceptance condition and reject the report until it is met |
| Progress claimed that the run's tool results do not support | Add the grounding rule to the packet and re-verify the claim before integrating anything |
| The delegate stopped to ask something the contract already answers | Move the answer into the packet's terrain section; a delegate's question is answered from the ledgers, never forwarded to the user |
| The delegate returned a plan for work it was authorized to perform | State the authority as an instruction to execute and name the completed state |
| The point of an ambiguous requirement was missed | Add the governing principle — not more steps |
| Large cost, small finding | Narrow the objective and lower the dispatch depth: a smaller question, not a shorter answer |
| A previously failed approach was tried again | Carry the relevant attempts.md excerpt in the packet's terrain as do-not-repeat notes |

## Depth is dispatch configuration

Express task difficulty where the host accepts it — a depth or effort control,
a model selection, a task budget — and not as prose inside the packet. Prose
intensifiers behave differently on every executor; a dispatch setting is
either honored or absent, which is a fact the runtime can observe and record.

Where the host exposes no such control, express difficulty as constraints
instead: a narrower objective, a higher verification tier, an additional
independent verifier. Those change the work; adjectives only ask for more of
it.

Route depth by consequence, and record the mapping in the contract when the
mission's mix is unusual:

- routine mechanical work — the cheapest setting that has produced acceptable
  results in this mission
- ordinary bounded implementation and review — the default
- difficult diagnosis, cross-cutting change, architecture, completion audits —
  the highest setting the budget supports

A work budget (total effort the mission may spend) and a context budget (what
fits in one window) are different resources with different owners. The control
loop owns both; a delegate is handed neither.

## Host capability probe

Hosts differ in what the runtime can actually use, so establish the facts once
at mission start, cheaply, and record them: whether subagent dispatch exists,
whether several can run concurrently, whether a delegate can be continued
rather than respawned, whether isolated worktrees exist, whether a task list,
a scheduler, or a depth control exists, and whether hooks run (telemetry
reference).

Every absent capability has a degradation, not a stop: no subagents means the
orchestrator does the work inline and keeps the packet as its own written
scope; no parallelism means sequencing by dependency and cost; no worktrees
means serializing writers by file ownership; no scheduler means the capsule
carries the next action across turns. Record each degradation in state.md so a
later session does not mistake a host limit for a decision someone made.

## Where calibration state lives

Calibration is mission state, not conversation state. The resume capsule
carries a short Calibration block: host capabilities probed, packet repairs in
force with the observation each answers, and the depth settings that have
produced acceptable results. Adding or retiring a repair is a decision and
lands in decisions.md with its evidence, like any other. A resumed session
inherits the calibration rather than rediscovering it at the same cost.
