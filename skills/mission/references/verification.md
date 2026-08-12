# Verification, Review, and Failure Recovery

## Contents

- [Verification depth scales with consequence](#verification-depth-scales-with-consequence)
- [Evidence standard for a "fix"](#evidence-standard-for-a-fix)
- [Independent review](#independent-review)
- [Fidelity checks are asymmetric](#fidelity-checks-are-asymmetric)
- [Localized repair](#localized-repair)
- [Failure classification](#failure-classification)
- [Recovery protocol](#recovery-protocol-recoverable-classes)
- [Non-recoverable classes](#non-recoverable-classes)
- [Self-correction](#self-correction)

Implementation is not completion. Confidence language is not evidence. A
change counts as done only when the evidence standard in the contract is met
and recorded in `.mission/verification.md`.

## Verification depth scales with consequence

- Every change: the relevant tests run, results recorded.
- Consequential changes (behavior users depend on, shared surfaces, risky
  areas): the full evidence standard below, including the sibling sweep and
  an independent review.
- Mission completion: an adversarial audit of the completion claim.

Assign the tier when the task enters the queue ("evidence needed for
completion"), so the expensive gates spend where the risk is.

**The non-authoring invariant.** The context that produced a change does not
decide whether it worked. Independence is the mechanism, not the ceremony: a
reviewer that never saw the work finds what self-review structurally cannot,
because an author's blind spots are correlated with the author's design. A
consequential change gets its check in a fresh context that did not author it
— self-verification of plans produced 38 false positives per 100 in one
measured study, and self-critique scored below an external check on the same
work. Self-review is the weakest check available; use it only when a separate
dispatch is impossible, and record the substitution in verification.md so the
evidence is not read as stronger than it is.

**Depth is not standing prose.** A generated brief carries no standing
verification-depth instruction. Current guidance splits by model generation:
one model's guidance is to strip explicit verification instructions because
they cause over-verification at no quality gain, another's is to make
self-verification explicit on long runs. The invariant above holds on both —
a consequential change gets an independent, non-authoring check — while a
procedure ("spawn a reviewer after each step") is wrong on one of them. How
deeply a given model checks itself is host configuration, or a repair recorded
with the failure it corrects.

## Evidence standard for a "fix"

1. Reproduce the original failure (or measure the baseline) before changing
   anything. No repro → record that explicitly in the ledger with the
   substitute evidence used (baseline measurement, differential logs,
   statistical recurrence) — a named substitute is a standard; an unnamed one
   is a loophole.
2. Identify the root cause, not the nearest symptom.
3. Make the targeted change.
4. Add a regression test that fails without the change and passes with it.
5. Run the existing suite; investigate every new failure before proceeding.
6. Validate in representative environments where environment matters
   (installation, packaging, service startup, cross-platform behavior).
7. Sweep for sibling defects: the same bug pattern in nearby code paths.
8. Check documentation for drift the change introduced.
9. Record the exact replay commands with the entry — a later audit reruns
   evidence instead of reconstructing it.
10. For consequential changes, commission an independent review (below).

## Independent review

A consequential change, and every completion claim, gets a review from a
context that did not produce the work — reviewers whose job is to falsify,
not to approve. Route by object: a completion claim or the ledgers → adversarial-critic;
input handling, auth, secrets, permissions, dependencies → security-reviewer;
maintainability and convention adherence → code-quality-reviewer; changed
behavior → regression-investigator. Reviewers get read-only access, the
claim under test, and the evidence standard; they attempt to break the claim
(differential tests, edge inputs, baseline comparison, regression search).

Reviewers search broadly, then report every finding that affects
correctness or the stated requirements and no others — the reporting bar
filters the report, never the search. Rank by severity, nits labeled as
nits: a real correctness defect is not dropped for being moderate, and a
thin report is not padded to look thorough — manufactured findings cost the
mission the cycles it takes to disprove them.
Material findings become queue tasks; the review verdict is logged in
verification.md. A second-pass audit that finds nothing new is itself
evidence for stopping.

## Fidelity checks are asymmetric

A faithfulness or entailment check — does this claim follow from the evidence
behind it? — carries weight in one direction only. A failed check demotes the
claim to unsupported and sends it back for evidence or withdrawal. A passed
check certifies nothing: such checks are biased against heavily paraphrased
text, and the best of them reach about 84% balanced accuracy, so a pass is
consistent with a claim that is wrong.

## Localized repair

When verification fails against one acceptance criterion, the repair happens
at that criterion: fix the check, the evidence, or the change it names, and
leave the rest of the contract as written. Regenerating a specification to fix
one clause is how constraints disappear between rewrites — the failure gets
attributed to a clause, and that clause gets repaired.

## Failure classification

On any failure, classify before reacting: incorrect hypothesis; incomplete
context; tool failure; environment failure; flaky test; incompatible
dependency; implementation defect; merge conflict; permission boundary;
external-service unavailability; missing credential; repeated non-progress.

## Recovery protocol (recoverable classes)

1. Preserve the evidence (exact error, logs, diff) in attempts.md, under the
   problem's `problem-id`, with the pre-attempt checkpoint named so revert
   is concrete.
2. Classify the failure.
3. Revise the hypothesis — what did this failure teach?
4. Choose a materially different approach; the new attempt entry cites the
   logged attempts it differs from, so no dead end is retried in disguise.
5. Retry within the bounded policy: three materially different approaches
   per problem-id. The third same-class failure forces stop-and-choose —
   revert, replan at mission level, defer the branch, or declare failure
   (stopping reference) — never a fourth retry, because "materially
   different" judged mid-circling stops meaning anything.
6. Compare the new result against the old; update the ledgers.

Flaky tests are findings, not noise: log them, quantify (rerun a few times),
and queue a stabilization task if mission-relevant.

## Non-recoverable classes

Permission boundaries, missing credentials, external-service outages: retries
cannot move them. Isolate the blocker to the smallest dependent task, finish
everything independent of it (implementation, tests, local simulation,
packaging, scripts, rollback docs, checklists, review), and only then surface
one specific question packet per the question gate.

## Self-correction

Revert your own unsuccessful changes promptly — a clean known-good state
beats a pile of half-fixes. Prefer small reversible commits/checkpoints so
reverting is cheap, and name the checkpoint in the attempt entry before a
consequential change. When verification reveals the plan itself was wrong,
replan at the mission level rather than patching the symptom of a bad plan.
