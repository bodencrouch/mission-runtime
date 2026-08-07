#!/usr/bin/env python3
"""Summarize mission-runtime telemetry into benchmark numbers.

Reads the NDJSON records written by mr_record.py and answers the question the
store exists to answer: what did mission-runtime do, what did it cost, and how
do mission sessions compare to sessions where it was not driving.

    python3 scripts/mr_report.py                  # summary for all runs
    python3 scripts/mr_report.py --days 7         # last 7 days
    python3 scripts/mr_report.py --sessions       # per-session table
    python3 scripts/mr_report.py --json           # machine-readable
"""

from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import statistics
import sys

SPAWN_EVENTS = {"SubagentSpawn"}
START_EVENTS = {"SubagentStart"}
STOP_EVENTS = {"SubagentStop"}


def store_root() -> str:
    override = os.environ.get("MISSIONRUNTIME_HOME")
    if override:
        return os.path.abspath(os.path.expanduser(override))
    return os.path.join(os.path.expanduser("~"), ".missionruntime")


def parse_ts(value: str):
    if not value:
        return None
    try:
        return _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def load_records(root: str, days: int | None):
    cutoff = None
    if days:
        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days)
    pattern = os.path.join(root, "sessions", "*", "*.jsonl")
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except Exception:
                        # One corrupt line must not sink the whole report.
                        continue
                    if cutoff:
                        ts = parse_ts(rec.get("ts", ""))
                        if ts and ts < cutoff:
                            continue
                    yield rec
        except OSError:
            continue


def summarize_sessions(records):
    sessions: dict[str, dict] = {}
    for rec in records:
        sid = str(rec.get("session_id") or "unknown")
        s = sessions.setdefault(sid, {
            "session_id": sid,
            "host": rec.get("host", "unknown"),
            "first": None, "last": None,
            "prompts": 0, "tool_calls": 0,
            "subagents": 0,
            # Spawns and stops are counted separately, then reconciled. A run
            # can be missing either side: the fallback path may only record
            # spawns, and a session that ends mid-flight records a spawn with
            # no stop. Taking the max per type avoids both undercounting a
            # repeated agent type and double-counting a completed one.
            "_spawns": {}, "_stops": {},
            "agent_types": {},
            "skills": {},
            "mission_active": False,
            "cwd": rec.get("cwd"),
            "_agent_starts": {},
            "agent_durations_ms": [],
            "stop_status": None,
        })
        ts = parse_ts(rec.get("ts", ""))
        if ts:
            if s["first"] is None or ts < s["first"]:
                s["first"] = ts
            if s["last"] is None or ts > s["last"]:
                s["last"] = ts
        if rec.get("mission_active"):
            s["mission_active"] = True

        event = rec.get("event")
        if event == "UserPromptSubmit":
            s["prompts"] += 1
        elif event == "PostToolUse":
            s["tool_calls"] += 1
        elif event == "SkillInvoke":
            ti = rec.get("payload", {}).get("tool_input")
            name = ti.get("skill") if isinstance(ti, dict) else None
            if name:
                s["skills"][name] = s["skills"].get(name, 0) + 1
        elif event in SPAWN_EVENTS:
            # Spawn carries the delegated prompt; the type is the useful key.
            atype = rec.get("subagent_type") or rec.get("agent_type")
            if atype:
                s["_spawns"][atype] = s["_spawns"].get(atype, 0) + 1
        elif event in START_EVENTS:
            aid = rec.get("agent_id")
            if aid and ts:
                s["_agent_starts"][aid] = ts
        elif event in STOP_EVENTS:
            s["subagents"] += 1
            atype = rec.get("agent_type") or rec.get("subagent_type")
            if atype:
                s["_stops"][atype] = s["_stops"].get(atype, 0) + 1
            # Prefer a host-reported duration; otherwise pair with the start.
            dur = rec.get("duration_ms")
            if isinstance(dur, (int, float)):
                s["agent_durations_ms"].append(float(dur))
            else:
                aid = rec.get("agent_id")
                start = s["_agent_starts"].pop(aid, None)
                if start and ts:
                    s["agent_durations_ms"].append(
                        (ts - start).total_seconds() * 1000.0)
        elif event in ("Stop", "SessionEnd"):
            s["stop_status"] = rec.get("status") or s["stop_status"]

    for s in sessions.values():
        s.pop("_agent_starts", None)
        spawns, stops = s.pop("_spawns"), s.pop("_stops")
        for atype in set(spawns) | set(stops):
            s["agent_types"][atype] = max(spawns.get(atype, 0),
                                          stops.get(atype, 0))
        # A session interrupted mid-delegation records spawns without stops;
        # counting only stops would silently under-report the work done.
        s["subagents"] = max(s["subagents"], sum(s["agent_types"].values()))
        if s["first"] and s["last"]:
            s["duration_s"] = round((s["last"] - s["first"]).total_seconds(), 1)
        else:
            s["duration_s"] = 0.0
        s["first"] = s["first"].isoformat() if s["first"] else None
        s["last"] = s["last"].isoformat() if s["last"] else None
    return sessions


def med(values):
    return round(statistics.median(values), 1) if values else 0.0


def compare(sessions: dict) -> dict:
    mission = [s for s in sessions.values() if s["mission_active"]]
    plain = [s for s in sessions.values() if not s["mission_active"]]

    def group(rows):
        return {
            "sessions": len(rows),
            "median_duration_s": med([r["duration_s"] for r in rows]),
            "median_tool_calls": med([r["tool_calls"] for r in rows]),
            "median_prompts": med([r["prompts"] for r in rows]),
            "median_subagents": med([r["subagents"] for r in rows]),
            "total_subagents": sum(r["subagents"] for r in rows),
        }

    return {"mission": group(mission), "non_mission": group(plain)}


def agent_leaderboard(sessions: dict) -> list:
    totals: dict[str, dict] = {}
    for s in sessions.values():
        for name, count in s["agent_types"].items():
            entry = totals.setdefault(name, {"agent": name, "spawns": 0})
            entry["spawns"] += count
    # Durations are not attributed per agent type by every host, so report the
    # spawn counts (always available) and a global duration median separately.
    return sorted(totals.values(), key=lambda e: -e["spawns"])


def verdict(cmp_: dict) -> list:
    """Turn the comparison into plain statements.

    This is deliberately descriptive rather than a single score. A "worth it"
    number would need a value-per-outcome weight that only you can supply —
    see the note printed alongside it.
    """
    lines = []
    m, p = cmp_["mission"], cmp_["non_mission"]
    if m["sessions"] == 0:
        lines.append("No mission sessions recorded yet — nothing to compare.")
        return lines
    if p["sessions"] == 0:
        lines.append("Only mission sessions recorded. Run some ordinary "
                     "sessions with the plugin installed to get a baseline.")
        return lines

    def ratio(a, b):
        return round(a / b, 1) if b else None

    for label, key in (("wall-clock time", "median_duration_s"),
                       ("tool calls", "median_tool_calls"),
                       ("subagents", "median_subagents")):
        r = ratio(m[key], p[key])
        if r is None:
            continue
        if r >= 1:
            lines.append(f"Mission sessions use {r}x the {label} "
                         f"({m[key]} vs {p[key]}).")
        else:
            lines.append(f"Mission sessions use {r}x the {label} "
                         f"({m[key]} vs {p[key]}) — less than baseline.")
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--sessions", action="store_true",
                    help="Print a per-session table")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = store_root()
    if not os.path.isdir(os.path.join(root, "sessions")):
        print(f"No telemetry found at {root}.")
        print("Either no session has run since the hooks were installed, or "
              "recording is disabled.")
        print("Check: python3 scripts/mr_doctor.py")
        return 0

    sessions = summarize_sessions(load_records(root, args.days))
    cmp_ = compare(sessions)
    all_durations = [d for s in sessions.values()
                     for d in s["agent_durations_ms"]]
    report = {
        "store": root,
        "sessions": len(sessions),
        "comparison": cmp_,
        "agents": agent_leaderboard(sessions),
        "median_subagent_duration_s": round(med(all_durations) / 1000.0, 1),
        "verdict": verdict(cmp_),
    }

    if args.json:
        if args.sessions:
            report["session_detail"] = sorted(
                sessions.values(), key=lambda s: s["first"] or "")
        print(json.dumps(report, indent=2, default=str))
        return 0

    print(f"mission-runtime telemetry — {root}")
    print(f"{len(sessions)} session(s) recorded"
          + (f", last {args.days} day(s)" if args.days else ""))
    print()
    print(f"{'':16} {'sessions':>9} {'dur(s)':>8} {'tools':>7} "
          f"{'prompts':>8} {'subagents':>10}")
    for label, key in (("mission", "mission"), ("non-mission", "non_mission")):
        g = cmp_[key]
        print(f"{label:16} {g['sessions']:>9} {g['median_duration_s']:>8} "
              f"{g['median_tool_calls']:>7} {g['median_prompts']:>8} "
              f"{g['median_subagents']:>10}")
    print("  (medians, not totals)")

    if report["agents"]:
        print("\nSpecialist usage")
        for entry in report["agents"][:15]:
            print(f"  {entry['spawns']:>4}  {entry['agent']}")
        print(f"\nMedian subagent wall-clock: "
              f"{report['median_subagent_duration_s']}s")

    print("\nRead-out")
    for line in report["verdict"]:
        print(f"  {line}")
    print("\n  These are cost figures. Whether the cost bought anything is a")
    print("  judgment about outcome quality that telemetry cannot make for")
    print("  you — see references/telemetry.md on scoring runs.")

    if args.sessions:
        print(f"\n{'session':<26} {'host':<8} {'M':<2} {'dur(s)':>8} "
              f"{'tools':>6} {'agents':>7}")
        for s in sorted(sessions.values(), key=lambda s: s["first"] or ""):
            flag = "y" if s["mission_active"] else "-"
            print(f"{s['session_id'][:26]:<26} {str(s['host'])[:8]:<8} "
                  f"{flag:<2} {s['duration_s']:>8} {s['tool_calls']:>6} "
                  f"{s['subagents']:>7}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
