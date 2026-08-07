#!/usr/bin/env python3
"""Install mission-runtime telemetry hooks into a non-Claude host.

Claude Code needs nothing from this script — it loads `hooks/hooks.json` from
the plugin directly and expands `${CLAUDE_PLUGIN_ROOT}` itself. Cursor, Copilot,
and Codex read hook configs from fixed locations outside the plugin and have no
equivalent placeholder, so their configs must be written out with an absolute
path to the recorder.

This writes to files the host owns, so it prints a plan and does nothing unless
you pass --apply. Existing files are backed up, never silently replaced.

    python3 scripts/mr_install_hooks.py --host cursor            # show plan
    python3 scripts/mr_install_hooks.py --host cursor --apply    # write it
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
RECORDER = os.path.join(HERE, "mr_record.py")

# Where each host looks for hook configuration. `user` is the safer default:
# it applies everywhere without needing per-project trust.
TARGETS = {
    "cursor": {
        "template": "cursor.json",
        "user": "~/.cursor/hooks.json",
        "project": ".cursor/hooks.json",
        "note": "Cursor merges hook sources; project files need workspace trust.",
    },
    "copilot": {
        "template": "copilot.json",
        "user": "~/.copilot/hooks/mission-runtime.json",
        "project": ".github/hooks/mission-runtime.json",
        "note": "Copilot CLI reads ~/.copilot/hooks/*.json; VS Code reads "
                ".github/hooks/*.json and marks hooks as Preview.",
    },
    "codex": {
        "template": "codex.json",
        "user": "~/.codex/hooks.json",
        "project": ".codex/hooks.json",
        "note": "Codex requires one-time approval of command hooks via /hooks, "
                "and re-prompts whenever the command string changes.",
    },
}


def build_command() -> str:
    """The recorder invocation, quoted so an install path with spaces works."""
    return f'python3 "{RECORDER}"'


def resolve_target(host: str, scope: str, project: str) -> str:
    spec = TARGETS[host]
    if scope == "user":
        return os.path.abspath(os.path.expanduser(spec["user"]))
    return os.path.abspath(os.path.join(project, spec["project"]))


def render(host: str) -> str:
    path = os.path.join(PLUGIN_ROOT, "hooks", TARGETS[host]["template"])
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    # The command is substituted inside a JSON string literal and itself
    # contains double quotes (to survive install paths with spaces), so it must
    # be JSON-escaped or the rendered file is not parseable.
    escaped = json.dumps(build_command())[1:-1]
    rendered = text.replace("__MR_CMD__", escaped)
    # Fail loudly here rather than writing a config the host will reject.
    json.loads(rendered)
    return rendered


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", required=True, choices=sorted(TARGETS))
    ap.add_argument("--scope", default="user", choices=("user", "project"))
    ap.add_argument("--project", default=os.getcwd(),
                    help="Project root for --scope project (default: cwd)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write. Without this, only the plan is shown.")
    args = ap.parse_args()

    if not os.path.isfile(RECORDER):
        print(f"error: recorder not found at {RECORDER}", file=sys.stderr)
        return 1

    target = resolve_target(args.host, args.scope, args.project)
    try:
        rendered = render(args.host)
    except Exception as exc:
        print(f"error: could not render template: {exc}", file=sys.stderr)
        return 1

    print(f"host      {args.host}")
    print(f"scope     {args.scope}")
    print(f"recorder  {RECORDER}")
    print(f"target    {target}")
    print(f"note      {TARGETS[args.host]['note']}")
    exists = os.path.exists(target)
    if exists:
        print(f"WARNING   {target} already exists.")
        print("          It will be backed up, then replaced. If you hand-wrote")
        print("          hooks there, merge them manually instead.")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
        return 0

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        if exists:
            stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = f"{target}.bak-{stamp}"
            shutil.copy2(target, backup)
            print(f"backed up {backup}")
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(rendered)
    except Exception as exc:
        print(f"error: write failed: {exc}", file=sys.stderr)
        return 1

    print(f"wrote     {target}")
    print("Restart the host (or reload plugins) for hooks to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
