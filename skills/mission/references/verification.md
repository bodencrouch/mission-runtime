# Verification, Review, and Failure Recovery

Implementation is not completion. Confidence language is not evidence. A
change counts as done only when the evidence standard in the contract is met
and recorded in `.mission/verification.md`.

## Evidence standard for a "fix"

1. Reproduce the original failure (or measure the baseline) before changing
   anything. No repro → say so explicitly in the ledger and explain the
   substitute evidence.
2. Identify the root cause, not the nearest symptom.
3. Make the targeted change.
4. Add a regression test that fails without the change and passes with it.
5. Run the existing suite; investigate every new failure before proceeding.
6. Validate in representative environments where environment matters
   (installation, packaging, service startup, cross-platform behavior).
7. Sweep for sibling defects: the same bug pattern in nearby code paths.
8. Check documentation for drift the change introduced.
9. For consequential changes, commission an independent review (below).

## Independent review

For any consequential change — and always before declaring the mission
complete — dispatch reviewers whose job is to falsify, not to approve:
adversarial-critic for "is this actually done?", security-reviewer for
anything touching input handling, auth, secrets, permissions, or
dependencies, code-quality-reviewer for maintainability and convention
adherence, regression-investigator when behavior changed. Reviewers get
read-only access, the claim under test, and the evidence standard; they must
attempt to break the claim (differential tests, edge inputs, baseline
comparison, regression search). Material findings become queue tasks; the
review verdict is logged in verification.md. A second-pass audit that finds
nothing new is itself evidence for stopping.

## Failure classification

On any failure, classify before reacting: incorrect hypothesis; incomplete
context; tool failure; environment failure; flaky test; incompatible
dependency; implementation defect; merge conflict; permission boundary;
external-service unavailability; missing credential; repeated non-progress.

## Recovery protocol (recoverable classes)

1. Preserve the evidence (exact error, logs, diff) in attempts.md.
2. Classify the failure.
3. Revise the hypothesis — what did this failure teach?
4. Choose a MATERIALLY different approach; check attempts.md so no logged
   dead end is retried in disguise.
5. Retry within a bounded policy (default: three materially different
   approaches per problem before deferring or escalating).
6. Compare the new result against the old; update the ledgers.

Flaky tests are findings, not noise: log them, quantify (rerun a few times),
and queue a stabilization task if mission-relevant.

## Non-recoverable classes

Permission boundaries, missing credentials, external-service outages: do not
hammer retries. Isolate the blocker to the smallest dependent task, finish
everything independent of it (implementation, tests, local simulation,
packaging, scripts, rollback docs, checklists, review), and only then surface
one specific request per the question gate.

## Self-correction

Revert your own unsuccessful changes promptly — a clean known-good state
beats a pile of half-fixes. Prefer small reversible commits/checkpoints so
reverting is cheap. When verification reveals the plan itself was wrong,
replan at the mission level rather than patching the symptom of a bad plan.
