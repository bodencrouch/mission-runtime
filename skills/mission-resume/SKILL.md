---
name: mission-resume
description: >
  This skill should be used when the user says "resume the mission", "continue
  the mission", "pick up where you left off", "keep going", or starts a new
  session in a project that contains a `.mission/` directory from a previous
  mission-runtime run. It reloads the durable mission state and re-enters the
  control loop without asking the user to restate anything.
metadata:
  version: "0.1.0"
---

# Resume a Mission

Re-enter a paused or interrupted mission from durable state. Never ask the
user to restate the objective, prior decisions, or context that exists in
`.mission/` — reading those files IS the handoff.

1. Locate `.mission/` at the project root (search upward or via a quick find
   if the working directory is nested). If none exists, there is no mission to
   resume: say so in one line and, if the user's message contains an
   objective, start a fresh mission via the `mission` skill instead.
2. Read in order: `state.md` (resume capsule), `mission.md` (contract),
   `queue.md` (work ledger). Skim recent entries of `decisions.md`,
   `assumptions.md`, `attempts.md`, `verification.md`. Consult
   `${CLAUDE_PLUGIN_ROOT}/skills/mission/references/memory.md` for the
   schemas if any file looks unfamiliar.
3. Reconcile the ledger against reality before acting — the repo may have
   changed while the runtime was away: `git status` and `git log` since the
   capsule timestamp; a cheap test run if the suite is fast. Fold any
   discrepancies into the queue as new evidence, and re-verify any "Done"
   items whose files changed externally.
4. Rebuild the session task list from `queue.md` (TaskCreate), mark the
   active task in progress, and execute the capsule's "Next action".
5. Re-enter the full control loop exactly as defined by the `mission` skill
   and its references (`control-loop.md`, `delegation.md`,
   `verification.md`, `stopping.md`). All contract terms — authority tiers,
   question gate, communication rules, stopping policy — remain in force
   unchanged unless the user's resuming message redirects the mission; if it
   does, amend the contract and log the amendment in `decisions.md`.

Give the user one short declarative line on re-entry ("Resuming: <mission>.
Last completed X; picking up with Y.") and continue working. Do not ask
whether to continue.
