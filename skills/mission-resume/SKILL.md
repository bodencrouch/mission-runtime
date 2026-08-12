---
name: mission-resume
description: >
  This skill should be used when the user says "resume the mission", "continue
  the mission", "pick up where you left off", or starts a new session in a
  project that contains a `.mission/` directory from a previous mission-runtime
  run. Generic continuation phrases like "keep going" trigger it only when the
  `.mission/` state is fresh or the conversation is about the mission —
  mid-unrelated-work, "keep going" means the current work, not a stale mission.
  It reloads the durable mission state and re-enters the control loop without
  asking the user to restate anything.
metadata:
  version: "0.5.0"
---

# Resume a Mission

Re-enter a paused or interrupted mission from durable state. Never ask the
user to restate the objective, prior decisions, or context that exists in
`.mission/` — reading those files IS the handoff.

1. Locate `.mission/` at the project root (search upward or via a quick find
   if the working directory is nested). If none exists, there is no mission to
   resume: say so in one line and, if the user's message contains an
   objective, start a fresh mission via the `mission` skill instead.
2. Follow the resumption protocol in
   `${CLAUDE_PLUGIN_ROOT}/skills/mission/references/memory.md`: read
   state.md, then mission.md (including Amendments), then queue.md, then
   roles.md; skim recent decisions, assumptions, attempts. Check capsule
   freshness — a ledger entry newer than the capsule means the last session
   died before its refresh, so rebuild the capsule from the ledgers before
   trusting it. Demote Active queue entries to Pending and mark active
   roles.md entries orphaned, each with an orphan note: no agent survived
   the old session. Re-commission orphaned work from its roles.md entry, so
   the resumed mission re-instantiates the same team instead of deriving a
   different one and re-running work the ledgers already paid for.
3. Reconcile against reality before acting — the repo may have changed while
   the runtime was away: `git log <capsule sha>..HEAD` (the capsule records
   its HEAD anchor), `git status`, a cheap test run if the suite is fast.
   Fold discrepancies into the queue as new evidence, and re-verify any Done
   items whose files changed externally.
4. Where the host provides a session task list (e.g. TaskCreate), rebuild it
   from `queue.md` and mark the active task in progress — `queue.md` stays
   authoritative either way. Then execute the capsule's "Next action".
5. Re-enter the full control loop exactly as defined by the `mission` skill
   and its references. Reload the contract's terms in full — objective,
   acceptance criteria, non-goals, authority tiers, question gate,
   communication rules, stopping policy — rather than a delta summary,
   because the failure being repaired is premature commitment to an early
   reading rather than forgotten text, and restating the complete
   accumulated instruction recovers substantially more than a partial recap.
   If the resuming message steers the mission, it is a mid-mission directive:
   triage it per the mission skill's amendment protocol and log the outcome.

The full terms in step 5 are what the runtime reloads into its own working
context; what the user sees is one short declarative line ("Resuming:
<mission>. Last completed X; picking up with Y."). Re-present any question
packet parked under Blocked, then continue working. Do not ask whether to
continue — resumption is the user's answer.
