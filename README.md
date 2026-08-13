# mission-runtime

A Claude Code plugin that turns a one-sentence goal into finished, verified
engineering work.

You say what you want to be true: "make this reliable", "clean up this
codebase", "get it production-ready". The plugin works out what you actually
need, writes the plan down, does the work, tests it, and tells you when it is
done and why. You do not have to write careful prompts. You do not have to
manage steps. You do not have to repeat yourself tomorrow.

## Install

In Claude Code, run:

```
/plugin marketplace add bodencrouch/mission-runtime
/plugin install mission-runtime@mission-runtime
```

That is the whole setup. There are no packages to install and no accounts to
create. The plugin's scripts need Python 3, which most systems already have.

**Know before you install:** the plugin records what each run did — including
your prompts, in full — to a folder on your own computer
(`~/.missionruntime/`). Nothing leaves your machine. To record nothing, set
the environment variable `MISSIONRUNTIME_TELEMETRY=off`. Details in
[Telemetry](#telemetry).

## Start your first mission

Tell Claude the outcome you want:

> Take ownership of this repository and make its Linux install reliable.

Then let it run. Here is what happens:

1. Claude reads your message and your repository, and works out the goal
   behind your words. Vague words like "reliable" become concrete checks it
   can test.
2. It writes a contract: the goal, what counts as done, what it may do on its
   own, and where it must stop. The contract lives in a `.mission/` folder in
   your project.
3. Its first reply opens with a readback: what it understood, and what it is
   doing first. If it misread you, one corrective line fixes it.
4. It plans the work and does the highest-value task first. For specialist
   jobs it sends out its own agents — one maps the repo, one researches, one
   writes code, one tests, one tries to break the finished work.
5. It reports when something real happens: a finding, a decision, a risk, a
   finished piece. Your silence means "keep going".
6. It stops when the goal is met with evidence — or tells you honestly why it
   cannot get there — and leaves a final report.

You can close your laptop mid-mission. The `.mission/` folder holds
everything. Say "resume the mission" in any later session and it picks up
where it left off, without you re-explaining anything.

## Say it, get it

| You say | What happens |
|---|---|
| Any outcome-shaped goal — "make the tests solid" | A mission starts (`/mission-runtime:mission`) |
| Something half-explained — "make it better", "just figure it out", "idk" | It works out the gaps and offers you a short pick-list (`/mission-runtime:mission-brief`) |
| "mission status", "what's left?" | A progress report (`/mission-runtime:mission-status`) |
| "resume the mission" | Picks up a paused mission (`/mission-runtime:mission-resume`) |
| "how much did that mission cost?", "stop recording my prompts" | Telemetry answers and settings (`/mission-runtime:mission-telemetry`) |

Mid-mission, just talk. "Oh, and it should also run on Windows" folds into
the plan. "Just the task" scales a mission down to the one thing you named.
Every ask you make lands in the work ledger — nothing you say gets silently
dropped.

## How it works

**The contract.** Your message is treated as evidence of what you need, not
as a literal task list. The plugin writes down its interpretation before it
works, so a wrong guess is cheap to catch and correct.

**The loop.** Plan, do the most valuable task, verify it, learn from the
result, replan. Finishing the obvious first task is not the end — the loop
asks what the goal still needs, and keeps going until a real stopping
condition is met.

**The agents.** Ten specialists handle bounded jobs: mapping the repo,
research, implementation, tests, security review, code review, failure
diagnosis, docs, a final independent audit, and one general analyst for jobs
the others do not cover. Reviewers cannot write files; writers get exact file
boundaries.

**The brief.** Before sending an agent anywhere, the plugin writes the brief
it would want to be given: what the job is, what counts as evidence, what is
out of bounds, what the other agents are doing, and what the report must
contain. It checks that brief against a list before anyone acts on it. This is
the prompt engineering you would otherwise do yourself.

**Any model, any phrasing.** You never have to tune your wording, and you
never have to know what the plugin is running on. Your message is turned into
the plugin's own working brief, and each agent is told the goal, the reason
behind it, what must not break, and what counts as proof — not a script of
steps. If an agent comes back having missed something, the plugin adds the
one instruction that would have prevented it, writes down why, and drops it
again when it is no longer needed.

**Verification.** Work does not count until it is proven: reproduce the
problem first, fix the cause, add a test that fails without the fix, run the
suite, and — for anything consequential — have an independent agent try to
break the claim.

**Questions.** It only interrupts you when evidence genuinely cannot decide
— missing credentials, an irreversible step, two of your requirements in
direct conflict. Even then it finishes everything else first, and tells you
what happens if you never answer.

**Half-explained asks.** If what you said is too vague to build from, you do
not get an interrogation. You get one short pick-list: at most three
questions, each with real answers already filled in from your own project,
one of them marked as what it will do anyway. Work starts right away, and
ignoring the list is a valid answer — the marked option just happens. Every
list also has a "decide for me" option that switches off the questions for
the rest of the mission. Say "just figure it out" up front and it skips the
list entirely.

**Stopping.** It stops when the goal is verifiably met, when what remains is
not worth the cost, or when it has honestly failed — and says which, with
evidence. Never with a bare "done".

## The .mission folder

Missions keep their memory in `.mission/` at your project root: the
contract, the current state, the work queue, decisions, assumptions, failed
attempts, and test evidence. This folder is why a mission survives closed
sessions and multi-day gaps.

It is kept out of your version control automatically (via
`.git/info/exclude` — your `.gitignore` is never touched). Deleting the
folder deletes the mission's memory.

## Telemetry

Every run leaves a local record, so you can measure what the plugin costs
you instead of guessing.

What is recorded: session timings, tool activity, agents launched, and your
prompts — in full, by default. Where: `~/.missionruntime/` on your machine.
Nothing is ever transmitted.

Read the numbers:

```
python3 scripts/mr_report.py             # summary; missions vs. ordinary sessions
python3 scripts/mr_report.py --sessions  # one row per session
```

The report gives costs only — time, tool calls, agent counts. It does not
claim the runtime was worth it; that judgment needs your own verdict on what
each run produced.

Check recording works:

```
python3 scripts/mr_doctor.py
```

Turn it down or off (environment variables win over the config file):

- `MISSIONRUNTIME_TELEMETRY=off` — record nothing.
- `MISSIONRUNTIME_REDACT=1` — store text lengths instead of text.
- `MISSIONRUNTIME_HOME=<path>` — move the store.
- `~/.missionruntime/config.json` — the same switches, in a file.

Delete history by removing `~/.missionruntime/sessions/`.

Claude Code records automatically. Config templates for Cursor, Copilot, and
Codex ship in `hooks/` but have not been tested against those hosts — treat
them as unproven. Install one with
`python3 scripts/mr_install_hooks.py --host cursor --apply`. The full design
is in `skills/mission/references/telemetry.md`.

## Requirements

- Claude Code.
- Python 3 for the telemetry scripts. They use only the standard library.

No other dependencies. No build step. No network calls.
