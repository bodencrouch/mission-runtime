# AGENTS.md

Repository-wide guidance for coding agents. For the full architecture and
authoring rules, read `CLAUDE.md` first — it is the source of truth for how
the skills, agents, references, and telemetry scripts fit together.

## Cursor Cloud specific instructions

This repo is a Claude Code plugin: markdown/JSON prompt surfaces plus a few
Python 3 telemetry scripts. There is **no build step, no package manager, no
network access, and no third-party dependencies** — the scripts import only
the Python 3 standard library. The only runtime requirement is `python3`
(3.12 is present on the VM), so the startup update script does not install
anything.

### Test / lint / build / run

- Tests (this is the whole suite; both files run together):
  `python3 -m unittest discover -s tests`
- There is no separate linter. `tests/test_runtime_conformance.py` acts as
  the lint gate for the markdown runtime (frontmatter shape, description
  length/person, `metadata.version` == plugin version, cross-references,
  agent tool least-privilege, hazard greps). Treat a passing unittest run as
  both "tests" and "lint".
- Nothing to build.
- The "application" is the telemetry subsystem in `scripts/`. Exercise it
  directly:
  - `python3 scripts/mr_doctor.py` — health check; exits non-zero on a
    problem.
  - Record an event: pipe a JSON hook payload to
    `python3 scripts/mr_record.py` (reads one payload from stdin, appends
    NDJSON, always exits 0).
  - `python3 scripts/mr_report.py [--sessions|--json]` — aggregate recorded
    sessions.
  - `python3 scripts/mr_install_hooks.py --host cursor|copilot|codex` —
    dry-run by default; add `--apply` to write.

### Non-obvious caveats

- The recorder writes to `~/.missionruntime/` by default (outside the repo).
  Set `MISSIONRUNTIME_HOME=<path>` to redirect it to a temp dir for
  experiments so you do not pollute the real store — the tests already do
  this. `mr_install_hooks.py` does not honor `MISSIONRUNTIME_HOME`.
- `mr_record.py` deliberately exits 0 on every path (hostile input,
  unwritable store, path-traversal session ids) and logs its own failures to
  `~/.missionruntime/recorder.err`; a non-zero exit would make hosts block
  the traced action. Keep that invariant when editing it.
- A record is flagged `mission_active: true` when the event's cwd contains a
  `.mission/` directory — the benchmark comparison in `mr_report.py` is built
  on that flag.
- When changing the recorder or a hook config, run the test suite and then
  `python3 scripts/mr_doctor.py`; both must stay green.
