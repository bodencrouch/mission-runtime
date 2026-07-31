# Continuation Discipline and the Stopping Policy

## The continuation review

Completing the obviously-requested work is a loop event, not an exit. After
each completed task — and always after the first visible deliverable — ask:

- What did this work expose that wasn't visible before?
- Which assumptions in the register remain unverified?
- Which edge cases were not exercised?
- Did the change create duplication or technical debt?
- Do nearby components carry the same defect?
- Is any documentation now inaccurate?
- Can the implementation be simplified without losing behavior?
- What reliability, performance, security, or usability follow-ups does the
  mission's outcome model now imply?
- Did test runs reveal flaky or weak areas?
- Is there unfinished repository work related to the mission?
- Would an independent second pass find something the first missed?
- Is the mission's END STATE achieved — or merely the first task?

Answers become queue tasks, each with a one-line traceability statement.

## Productive vs. unproductive continuation

A candidate task is productive when it directly advances the mission,
verifies an unproven claim, reduces a material risk, repairs a regression,
resolves discovered inconsistency, hardens completed work, fixes another
instance of a verified defect, completes required docs/operational support,
or provides an independent confidence check.

Reject candidates that: lack mission traceability; rewrite functioning code
for activity's sake; introduce speculative abstractions; expand the product
without evidence; swap technology for novelty; re-run reviews that no longer
produce new information; manufacture problems; or exist only because budget
remains. "This might be interesting" is not a justification. Sustained
goal-directed continuation, never busywork.

## Stopping conditions

Enter the quiescent completed state when any of these substantively holds:

- All identified high-value, mission-aligned work is complete and the
  outcome model's acceptance criteria are met with recorded evidence.
- Tests and validation pass; independent review finds no material issue.
- Remaining ideas are low-priority or speculative (log them as Deferred).
- Additional work shows sharply diminishing expected return.
- The configured time/cost/token budget is reached.
- Progress requires an external dependency or human-authority decision, and
  every independent branch is finished.
- Repeated materially-different attempts no longer produce new information.
- Continued work would add more risk than value.

Stopping is quiescence, not amnesia: `.mission/` remains intact and the
mission can be reactivated by new evidence or `mission-resume`.

## The final state report

Never end with a bare "done." Deliver:

```markdown
# Mission Report — <mission, one line>
## Outcome vs. acceptance criteria
Each criterion: met/partial/unmet, with evidence pointers.
## Work completed
Grouped by theme, not a chronological diary. Artifacts changed.
## Verified
What was tested, where, and how (from verification.md). What was
independently reviewed and the verdicts.
## Key decisions
The consequential ones, each with the reason and reversibility.
## Assumptions in force
Still-unverified assumptions the user may want to check.
## Unresolved / blocked
Each blocker: the smallest blocked task, the specific external need, and
what was completed around it.
## Residual risks
## Deferred ideas
Low-priority/speculative items, so future work starts warm.
## Next worthwhile work if resumed
Concrete, priority-ordered.
```

Write the report as the reply AND refresh `.mission/state.md` to match, so
`mission-status` and `mission-resume` agree with what the user was told.
