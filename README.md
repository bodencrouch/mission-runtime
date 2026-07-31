# mission-runtime

An intent-first autonomous engineering runtime for Claude. Give it a job, not
a task list: state a broad outcome ("make Linux setup solid", "improve this
app's performance", "take ownership of reliability") and the runtime
reconstructs your intent, writes its own operating contract, plans and
prioritizes the work, delegates to specialist subagents, verifies its own
output, and keeps generating mission-traceable follow-up work until a
substantive stopping condition is reached — not until the first plausible
answer.

## What it changes about Claude's behavior

- **Mission over task**: outcome-shaped requests are interpreted as
  delegation of responsibility, implicitly authorizing investigation,
  prioritization, implementation, testing, review, docs, and follow-up.
- **Default to action**: safe, reversible, evidence-supported choices are
  made and logged, never bounced back as questions. Questions pass a strict
  gate (irreversible, credential, legal/security authority, or materially
  conflicting requirements — and only after all independent work is done).
- **Persistent control loop**: interpret → inspect → model → queue → execute
  → verify → learn → replan, until the stopping policy fires.
- **Durable memory**: a `.mission/` directory at the project root holds the
  contract, resume capsule, work ledger, decision log, assumption register,
  attempt history, and verification ledger. Missions survive context
  compaction, session death, and multi-day gaps. (Kept out of your VCS via
  `.git/info/exclude`; your `.gitignore` is never touched.)
- **Supervised specialists**: subagents report evidence to the orchestrator,
  which validates, reconciles, and integrates — one accountable owner, no
  transcript dumps.
- **Verification as completion**: reproduce → root-cause → fix → regression
  test → suite → sibling sweep → independent adversarial audit for anything
  consequential.
- **Real stopping policy**: quiescence on evidence-backed completion,
  diminishing returns, budget, or an irreducible human dependency — always
  with a final state report (accomplished, verified, assumed, unresolved,
  next worthwhile work).

## Components

**Skills**

- `mission` — intake (the "introducer": sparse-intent reconstruction →
  operating contract) plus the persistent control loop. Reference docs cover
  the contract template and evidence hierarchy, the loop and prioritization,
  the memory schema, the delegation protocol, verification and failure
  recovery, and continuation/stopping policy.
- `mission-resume` — reload `.mission/` in any later session, reconcile
  against repo reality, and re-enter the loop without re-asking anything.
- `mission-status` — declarative progress or final report from the ledgers;
  never a disguised permission request.

**Agents**

repo-cartographer, research-analyst, implementation-engineer, test-engineer,
security-reviewer, code-quality-reviewer, regression-investigator,
docs-writer, adversarial-critic. Reviewers and investigators are
read-only/diagnose-only by design; writers carry bounded file scopes.

## Usage

Say what you want to be true:

- "Take ownership of this repository and make its Linux installation and
  startup experience reliable."
- "Make it fast."
- "Get this service production-ready."

Then let it run. Check in anytime with "mission status"; continue a previous
session with "resume the mission". Redirect at will — your messages amend the
contract; silence means "continue".

## Setup

No environment variables, MCP servers, or configuration required. Install the
plugin and state a mission.
