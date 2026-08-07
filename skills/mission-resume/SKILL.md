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
  version: "0.3.0"
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
   state.md, then mission.md (including Amendments), then queue.md; skim
   recent decisions, assumptions, attempts. Check capsule freshness — a
   ledger entry newer than the capsule means the last session died before
   its refresh, so rebuild the capsule from the ledgers before trusting it.
   Demote Active queue entries to Pending with an orphan note: no agent
   survived the old session.
3. Reconcile against reality before acting — the repo may have changed while
   the runtime was away: `git log <capsule sha>..HEAD` (the capsule records
   its HEAD anchor), `git status`, a cheap test run if the suite is fast.
   Fold discrepancies into the queue as new evidence, and re-verify any Done
   items whose files changed externally.
4. Rebuild the session task list from `queue.md` (TaskCreate), mark the
   active task in progress, and execute the capsule's "Next action".
5. Re-enter the full control loop exactly as defined by the `mission` skill
   and its references. All contract terms — authority tiers, question gate,
   communication rules, stopping policy — remain in force unchanged. If the
   resuming message steers the mission, it is a mid-mission directive:
   triage it per the mission skill's amendment protocol and log the outcome.

Give the user one short declarative line on re-entry ("Resuming: <mission>.
Last completed X; picking up with Y."), re-present any question packet
parked under Blocked, and continue working. Do not ask whether to continue —
resumption is the user's answer.
