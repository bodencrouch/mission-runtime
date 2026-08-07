# Mid-Mission Directives: the Amendment Protocol

A user message arriving mid-mission is the collision of two rules: the
contract is the fixed point, and the explicit current instruction is the
highest-ranked evidence. This protocol resolves the collision the same way
every time, so steering a running mission costs the user one plain sentence.

## First, always: land it in the ledger

Every mid-mission directive is recorded in `.mission/queue.md` as a Pending
entry traced `user-directive <timestamp>` — before triage, whatever the
verdict turns out to be. A directive that is later absorbed into the
contract, deferred, or superseded still has a ledger trail; an ask is never
silently swallowed. Message normalization (intent-contract reference) applies
to directives exactly as to the opening message: repair form, never content.

## Triage: the four verdicts

| Verdict | When | What happens |
|---|---|---|
| **In-scope task** | The ask fits the contract as written | Insert into the queue with normal prioritization; say so in the next update |
| **Scope amendment** | The ask changes contract terms — wider, narrower, new constraint, changed priority | Append the directive verbatim to the contract's Amendments section (dated, superseded terms struck); log a decisions.md entry; run the blast-radius sweep below |
| **Contradiction** | The ask materially conflicts with the contract or with evidence, and normalization confirms it is deliberate | The explicit current instruction outranks prior terms: amend and proceed. Only a genuine materially-conflicting-requirements situation — both terms asserted, neither withdrawn — goes to the question gate as human authority |
| **Separate mission** | The ask is a different outcome, not an evolution of this one | Default: record it as Deferred with trace, finish the current mission, surface the deferral explicitly in the next update — silence-means-continue cuts both ways, so a parked ask is always announced, never assumed accepted |

Triage is usually an inline judgment from the ledgers the orchestrator
already holds. Delegate a read-only analysis packet (per the delegation
protocol) instead when the directive contradicts the contract or invalidates
Done work — fresh context guards against sunk-cost anchoring — or when the
orchestrator is deep in an implementation and cannot triage well mid-flight.

## Blast-radius sweep (on any scope amendment)

Superseded contract terms may have work resting on them. Sweep the ledgers:

- decisions.md — decisions justified by a superseded term: still valid?
- assumptions.md — assumptions the amendment confirms or refutes.
- queue.md — Pending work the amendment invalidates (retire, with a note)
  and Done work it touches (re-verify or mark for re-verification).
- Active work — see effect boundary below.

Findings from the sweep become queue entries; the sweep itself is logged in
the decisions.md amendment entry.

## Effect boundary

An amendment takes effect at the next loop-stage boundary. In-flight agent
packets cannot be re-scoped mid-run: let a packet finish if its result stays
useful under the amended contract, or cancel it and log the partial to
attempts.md if it does not. When a directive touches files an active writer
owns, the queue's ownership record decides: wait for the writer to return, or
cancel it — never run a second writer into the same files.

## Worked example

> Mission: "make the test suite solid." Mid-mission directive: "oh and can
> it also run in CI on Windows?"

Landed in queue.md as `user-directive 2026-08-07T15:12Z`. Verdict: scope
amendment — the contract's scope named Linux CI only. Amendments section
gains the directive verbatim; decisions.md logs the amendment; blast-radius
sweep finds one Done item ("suite green on supported platforms") demoted to
re-verify and one assumption ("POSIX-only paths acceptable") refuted, which
spawns two queue tasks. The active flake-hunt packet is unaffected and
continues. Next update reads: "Windows CI folded into the mission; two
path-handling tasks queued; flake hunt still running."
