# The Commission: Role and Brief in One Artifact

## Contents

- [What a commission is](#what-a-commission-is)
- [The nine slots](#the-nine-slots)
- [Self-containment](#self-containment)
- [Chassis and the authority rule](#chassis-and-the-authority-rule)
- [The pre-dispatch gate](#the-pre-dispatch-gate)
- [A filled commission](#a-filled-commission)

## What a commission is

A commission is one generated artifact carrying both the role and the brief for
one unit of delegated work. It is derived from the operating contract, checked
before dispatch, and handed to a subagent as the whole of what that subagent
will ever see.

The effort goes into the specification, not the persona. Across 1,600+
annotated multi-agent traces, agents disobeyed their *task* specification about
22× more often than their *role* specification; a study over 162 personas and
2,410 factual questions found no accuracy benefit from persona framing at all.
Identity gets one sentence because it steers behavior and tone and costs
nothing. The other eight slots carry the work.

## The nine slots

A commission carries these nine and no free prose outside them. They run
context-first and ask-last: identity and objective frame the work in two lines,
bulk context follows, and the deliverable comes last — an ordering measured at
up to a 30% improvement in instruction-following.

**`IDENTITY`** — one sentence naming the domain and the scope of this work. No
superlatives and no claim of infallibility: over-constrained personas ("a
world-renowned expert who never makes mistakes") are the documented failure,
and a second sentence buys nothing measurable.

**`OBJECTIVE`** — one sentence, outcome-shaped: the end state this unit
produces, not the activity it performs. It fixes the deliverable type —
assessment, change, or both — because an ambiguous deliverable verb is exactly
what intake normalization repairs, and it repairs it once.

**`CONTEXT`** — the mission line plus the state this agent needs: file paths,
error strings verbatim, prior decisions, prior findings, and the conventions
and quality bar binding this work. Inline what is short; point at a path the
agent can read for anything long. This is the largest slot.

**`SCOPE`** — the files and systems in bounds, named individually, plus the
statement that everything else is out of bounds and the scope fence: no
unrequested refactors, features, or cleanups riding along. Name the files
rather than gesturing at a category — current models do not silently
generalize an instruction from a named item to an unnamed one, so an unnamed
file is an unfenced one.

**`NON-GOALS / OWNED BY OTHERS`** — what this commission does not do, and which
sibling commission owns each adjacent piece. Required whenever more than one
commission ships in the same message. Step repetition is the single most
frequent failure mode in the field's validated failure taxonomy (~17% of
annotated traces), and it comes from briefs that never say what the neighbors
are doing.

**`AUTHORITY`** — read-only, may run *these* commands, may edit *these* files.
Stated in prose here and enforced by the chassis's tool grant below.

**`EVIDENCE STANDARD`** — the check that makes a claim acceptable here, named
so a second reader can decide whether it was met: a command to rerun, a
measurement to take, a file:line to point at. Where no check exists, say so and
name the substitute. Long-running commissions add the grounding clause — audit
each claim against a tool result from this run, and report unverified work as
unverified — which is reported to nearly eliminate fabricated status. Where the
commission also sets a reporting bar, write search breadth and reporting bar as
two clauses, so a bar meant to filter the report does not quietly narrow the
search.

**`OUTPUT CONTRACT`** — the report's required sections, enumerated, and where
the report lands. A read-only chassis returns the report whole as its final
message and the orchestrator saves it to
`.mission/notes/<seq>-<agent>-<slug>.md`; a write-capable chassis saves its own
note file at that path and returns a terse summary. Asking a read-only agent to
write its report to a file spends a cycle against its charter. The final
message is data for the orchestrator, not prose for the user.

**`BUDGET`** — a rough effort bound, and what to report if the bound arrives
before the objective does.

## Self-containment

The only thing that reaches a subagent is the prompt string. It sees none of
this conversation, none of the skills already invoked, and none of the files
already read. A commission that refers to something outside itself refers to
nothing.

The test: read the commission with no other knowledge and confirm every
referent resolves inside it. No "the file we discussed", no "as above", no "the
earlier finding", no pronoun whose antecedent is missing from the text. Every
file path, error string, prior decision, and prior finding either appears in
the commission or sits at a path the commission names.

## Chassis and the authority rule

The plugin's agents are not the routing space. They are chassis — authority
capsules differing by tool grant — and the commission is what varies per
mission. Bind each commission to the chassis whose grant satisfies its
`AUTHORITY` slot.

| Authority shape | Chassis | Tool grant |
|---|---|---|
| Read and run, read-only by charter | repo-cartographer, security-reviewer, regression-investigator, adversarial-critic | Read, Grep, Glob, Bash |
| Read, run, and fetch; role-neutral | commissioned-analyst | Read, Grep, Glob, Bash, WebSearch, WebFetch |
| Read only, no execution | code-quality-reviewer | Read, Grep, Glob |
| Read and fetch, no execution | research-analyst | Read, Grep, Glob, WebSearch, WebFetch |
| Write within a decided scope | implementation-engineer, test-engineer | Read, Grep, Glob, Bash, Write, Edit |
| Write documentation only | docs-writer | Read, Grep, Glob, Bash, Write, Edit (docs files by charter) |

Where two chassis both satisfy the authority slot, prefer the one whose body
agrees with the identity sentence — an identity contradicting the agent body
puts two role statements in one context. A commissioned role matching no
specialty runs on `commissioned-analyst`, which is role-neutral by design,
rather than on an unbounded general-purpose agent.

**The authority rule.** A commission narrows authority below its chassis's
grant and never widens it. The grant is fixed in the agent file and prose
cannot reach it, so a commission asking for more produces an agent that fails
mid-task rather than one with more reach. Authority also stays inside the
contract's authority tier for that work: a commission cannot hand out what the
contract reserved for execute-and-report or for human authority.

## The pre-dispatch gate

Both checklists are decidable without a model, which is why they run first —
LLM self-verification of plans produced 38 false positives per 100 in a
published trial, so judgment runs after the checkable part rather than instead
of it.

**Per commission**, decidable by reading it alone:

1. All nine slots present and non-empty.
2. Self-contained by the test above.
3. Authority within the contract's tier for this work, and within the bound
   chassis's grant.
4. The evidence standard names a check the agent can run, or records that none
   exists and names the substitute.
5. The output contract enumerates the report's sections and states where the
   report lands.
6. The bound chassis's tool grant is non-empty.
7. No slot tells the agent to ask the user anything. The asking tool is
   stripped from every subagent, so such an instruction produces a stall or an
   invented answer. A specialist that needs a decision returns the question in
   its report; the orchestrator owns the ask.
8. No slot carries a standing verification-depth instruction — no "double-check
   your work", no "add a final verification step", no "verify with a subagent".
   Guidance on verification depth splits by model generation, so an instruction
   that helps one model wastes tokens on another. Depth is set by the chassis
   and by the evidence standard, not by intensity prose.

**Across a set dispatched together:**

1. Every acceptance criterion in the contract is owned by exactly one
   commission.
2. No two commissions share an objective and scope.
3. No two write-capable commissions name overlapping files.
4. Each commission states what its siblings own.

A commission failing a check is repaired at the failing slot. Regenerating the
whole artifact re-rolls the slots that already passed and discards the evidence
that put them there.

A commission that passes gets an entry in `.mission/roles.md` before it is
dispatched — id, chassis, objective, scope, status, and where its report will
land. Writing it first means a session that dies mid-dispatch leaves a record
of what was in flight; writing it afterward means an orphaned agent with no
trace. Update the entry's status when the report returns and again when it is
integrated or rejected.

## A filled commission

Mission: `svcd` starts reliably on a clean Linux install. This is the first
commission of that mission, bound to the `regression-investigator` chassis.

```markdown
IDENTITY: Failure-reproduction analyst for this project's Linux service
  startup path.
OBJECTIVE: A deterministic reproduction of the reported startup failure on a
  clean Fedora 42 install, with the failing component named.
CONTEXT: Mission — `svcd` starts reliably on a clean Linux install
  (`.mission/mission.md`). The user's report, verbatim: "fresh install, then
  `systemctl --user start svcd` exits 1 and journalctl shows nothing". Two
  install paths exist: `packaging/deb/postinst` and `packaging/rpm/svcd.spec`.
  The unit file is `packaging/systemd/svcd.service`. Nobody has attempted a
  reproduction yet and `.mission/notes/` is empty. Quality bar: production-
  ready (contract, Quality bar). Convention: this repo's existing regression
  reports use the shape in `.mission/notes/002-*.md` — match it.
SCOPE: `packaging/` in full, `src/svcd/startup.py`, and the throwaway
  container or VM used to reproduce. Read anything else in the repo that
  serves the evidence; change nothing.
NON-GOALS / OWNED BY OTHERS: Do not propose or write a fix — a later
  commission consumes this report and owns the fix. `commission-2`
  (commissioned-analyst) owns the Debian packaging audit under
  `packaging/deb/` in this same dispatch; record what you observe there and
  leave the audit to it.
AUTHORITY: Read anything in the repo. Run read-only inspection and
  reproduction commands (`systemctl`, `journalctl`, package install into a
  throwaway container, the test suite). No edits to the repository.
EVIDENCE STANDARD: A reproduction is the command sequence from a clean image
  to the failure, with exit code and captured output, such that rerunning the
  sequence reproduces the failure. If it does not reproduce in three attempts,
  say so and give the substitute evidence — differential logs against a
  working install, or the conditions under which the failure did appear. Every
  root-cause claim carries a file:line.
OUTPUT CONTRACT: Return the report as your final message, with these sections:
  Reproduction (exact commands and outputs), Root cause (file:line, or the
  narrowest bracket reached), Sibling defects observed, Uncertainties. The
  orchestrator saves it to `.mission/notes/003-regression-investigator-svcd-startup.md`.
BUDGET: About one clean-image cycle plus one confirming rerun. If the failure
  has not reproduced by then, report the narrowed bracket instead of
  continuing.
```
