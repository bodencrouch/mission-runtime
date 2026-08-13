# Answer Cards

The artifact a brief delivers: a question the user can answer by picking,
with a default that fires if they never do.

## Contents

- [Card anatomy](#card-anatomy)
- [Where the options come from](#where-the-options-come-from)
- [The default and what silence does](#the-default-and-what-silence-does)
- [The hands-off option](#the-hands-off-option)
- [Cards that should not be sent](#cards-that-should-not-be-sent)
- [Worked cards](#worked-cards)
- [Relationship to the question gate](#relationship-to-the-question-gate)

## Card anatomy

A card is one decision, three real options, and an exit.

```
**<the decision, as a short question>**
A. <option, named in the project's own terms>  (default)
B. <the defensible alternative>
C. <the cheap or narrow version>
D. Decide for me — no more questions this mission
Silence picks A. <what is already running regardless>
```

Hold to three substantive options plus the hands-off exit. Two is usually a
false binary; five is a form to fill in. Free text always works — a user who
types a sentence instead of picking a letter has answered, and the sentence
governs.

Where the platform offers a structured question tool, use it so the options
are clickable, and keep the hands-off option as the last choice. Where it
does not, the lettered list above is the fallback and loses nothing.

## Where the options come from

An option is autofilled when it names something real in the user's project.
"Fix the 3 flaky tests in `conftest.py`" is autofilled; "improve test
reliability" is a placeholder wearing an option's clothes. Draw from these,
in order of strength:

| Source | What it yields |
|---|---|
| Repository inspection | Real names and counts: the failing tests, the untested modules, the two config paths that disagree |
| Prior conversation and the ledgers | Preferences the user already stated, offered back rather than re-asked |
| Project documentation and conventions | The choice this codebase already made elsewhere |
| The user's own message | The mechanism they named, kept as one option so their idea is on the list |
| Engineering default | The conventional reversible choice, when nothing above decides |

Do the inspection before composing the card. A card written without looking
is a survey, and it costs the user more than it returns — the point of
autofill is that the agent has already done the reading.

When two options came from different sources, say which is which in six
words or fewer: `(what the repo already does)`, `(your suggestion)`,
`(conventional default)`. Provenance is what makes a default trustworthy
enough to accept without thinking.

## The default and what silence does

Every card marks exactly one option as the default, and the default is the
most reversible option that is consistent with the evidence — not the most
ambitious one. Reversibility is the criterion because a wrong default that
can be undone costs a rerun, and a wrong default that cannot costs the
mission.

State what silence does in the same breath as the card, and then honor it:
the default fires on the next work cycle, not at some unnamed later point.
Record the fired default in `.mission/assumptions.md` with the option that
fired, the options that did not, and the impact if it turns out wrong, so a
later correction is a one-line amendment rather than an excavation.

## The hands-off option

The last option on every card is the same, and it means what it says:

> Decide for me — no more questions this mission

Selecting it does four things: records a decision in `.mission/decisions.md`,
sets `Autonomy: hands-off` in the contract, fires the recommended default on
every card in that turn, and suppresses answer cards for the remainder of
the mission.

What it does not do is waive authority. The mission's question gate still
surfaces the rare item carrying real authority or irreversibility — missing
credentials, destructive operations, publishing outward, a legal or
financial commitment. A user who declined to arbitrate scope has not
transferred ownership of their production data, and treating those as the
same waiver is the one way this option can do harm.

Hands-off can also arrive pre-selected in the original message. "Just figure
it out", "do whatever you think", "build as much as you can", "you decide"
are selections, not vagueness. When one appears, skip the cards entirely:
state the reading, register the assumptions, and build. Asking a user who
pre-authorized autonomy to confirm their autonomy is the exact interruption
they were avoiding.

## Cards that should not be sent

Apply one test before sending: **if every option leads to the same work, the
card is noise.** Cut it, take the default silently, and log the assumption.

Also cut:

- Cards whose options are not mutually exclusive, so picking one does not
  actually decide anything.
- Cards that differ only in wording — three phrasings of the same plan.
- Cards asking for information the repository answers. Read it instead.
- Cards asking permission. "Shall I start?" is not a decision; it is the
  disguised permission request the runtime does not make.
- Cards about the user rather than the work. The brief recovers what to
  build.
- A fourth card in the same turn. Three is the ceiling; default the rest.

## Worked cards

**Scope is missing.** The user said "make the test suite solid" after a
week of red CI.

> **Flaky tests or missing coverage first?**
> A. The 3 intermittent failures — all touch the shared `conftest.py`
>    fixture *(default, reversible)*
> B. The 4 modules with no tests *(conventional default elsewhere in
>    this repo)*
> C. Both, flakes first
> D. Decide for me — no more questions this mission
> Silence picks A. Fixture isolation is running either way.

**Criteria are missing.** The user asked "containerd vs dockerd?" — a bare
comparison with nothing to choose against. The card supplies the missing
axis rather than the missing answer.

> **Choosing against which constraint?**
> A. Whatever the k3s nodes already run — least migration *(default)*
> B. Whatever has the better local debugging story
> C. Whatever survives the smallest node — memory is the binding limit
> D. Decide for me — no more questions this mission
> Silence picks A. Checking what the existing nodes run now.

**No card at all.** The user said "map my perfect setup into workflows,
build as much as you can". Hands-off is pre-selected and the outcome is
inferable, so the correct brief is a readback with no questions in it:

> Reading this as: turn the compose stack in `deploy/` into CI workflows
> that build, test, and publish each service, matching the tags already in
> `docker-compose.yml`. Running hands-off — assumptions are going in
> `.mission/assumptions.md` as I make them, and the two I am least sure of
> are the registry namespace and whether the staging job should deploy or
> just build. Starting with the build job.

## Relationship to the question gate

The question gate — stated canonically in the mission skill's intent-contract
reference — governs questions that *block*: rare, high-bar, parked in the
queue under Blocked. Answer cards are a different instrument: they never block, they
carry a default that fires on silence, and they exist to make the readback's
standing invitation ("one line overrides this") cost one keystroke instead
of a paragraph.

The two do not compete. A card that would stop work if unanswered is not a
card; it is a gate question, and it follows the gate's rules including the
full question packet.
