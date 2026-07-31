---
name: mission-status
description: >
  This skill should be used when the user asks "mission status", "how's the
  mission going", "what's left", "what have you done so far", "where are we",
  or requests a progress or final report on an active or completed
  mission-runtime mission. It reports from the durable `.mission/` ledgers
  without pausing or redirecting the work.
metadata:
  version: "0.1.0"
---

# Mission Status

Report state from the ledgers; do not stop, replan, or transfer control. A
status request is read-only with respect to the mission.

1. Read `.mission/state.md`, `queue.md`, and recent `verification.md` and
   `decisions.md` entries. If `.mission/` is absent, say there is no active
   mission (one line) and stop.
2. Produce a declarative report:
   - Mission (one line) and overall position against the outcome model's
     acceptance criteria.
   - Discovered: material findings since the last report.
   - Completed: grouped by theme, with what was verified and how.
   - In progress: current task(s) and what is being validated.
   - Plan changes and consequential decisions, each with its reason.
   - Risks and unverified assumptions worth the user's attention.
   - Blocked: only genuine blockers, each stated per the question gate —
     the specific external need plus everything already completed around it.
   - Next: the upcoming highest-value work.
3. If the mission has reached a stopping condition, deliver the full final
   state report using the template in
   `${CLAUDE_PLUGIN_ROOT}/skills/mission/references/stopping.md` instead.
4. Match length to substance: a mid-mission check-in is a dozen tight lines,
   not a document. No disguised permission requests — never end the report
   with "shall I continue?"; if work remains and no blocker exists, the
   report's last line states what is being done next, and the work continues.
