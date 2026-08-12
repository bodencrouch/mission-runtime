"""Static conformance tests for the markdown runtime (skills and agents).

The telemetry tests guard the measurement layer; these guard the thing
measured. They are stdlib-only and purely static: frontmatter shape, tool
boundaries, reference linkage, style-guide hazard patterns, and manifest
parity. The rules they enforce live in docs/prompt-style.md.
"""

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = sorted((REPO / "skills").glob("*/SKILL.md"))
AGENTS = sorted((REPO / "agents").glob("*.md"))
REFERENCES = sorted((REPO / "skills" / "mission" / "references").glob("*.md"))

# Agents whose charter is read-only: they must not hold write tools.
READ_ONLY_AGENTS = {
    "repo-cartographer",
    "research-analyst",
    "security-reviewer",
    "code-quality-reviewer",
    "regression-investigator",
    "adversarial-critic",
    "commissioned-analyst",
}
WRITER_AGENTS = {"implementation-engineer", "test-engineer", "docs-writer"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}

# Documented agent color set (code.claude.com/docs/en/sub-agents).
VALID_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}

# Style-guide hazard patterns (docs/prompt-style.md, "Checking a prompt
# change"). Baseline was zero hits on 2026-08-07; rewrites must not
# introduce them.
HAZARDS = {
    "reasoning-echo": re.compile(
        r"show your (reasoning|thinking|thought)|explain your (reasoning|thinking)"
        r"|think out loud|your thought process|internal reasoning",
        re.IGNORECASE,
    ),
    "emphasis-caps": re.compile(r"\b(IMPORTANT|CRITICAL|YOU MUST|ALWAYS|NEVER)\b"),
    "anti-laziness": re.compile(
        r"if in doubt|when in doubt|aggressively|be proactive\b", re.IGNORECASE
    ),
    "think-ritual": re.compile(
        r"think hard|think carefully|think step|think deeply|ultrathink", re.IGNORECASE
    ),
}


def frontmatter(path):
    """Return (frontmatter_text, body_text). Naive but sufficient: the
    frontmatter is everything between the first two --- lines."""
    text = path.read_text(encoding="utf-8")
    parts = text.split("\n---\n", 1)
    if not text.startswith("---\n") or len(parts) != 2:
        raise AssertionError(f"{path}: missing frontmatter block")
    return parts[0][len("---\n"):], parts[1]


def frontmatter_value(fm, key):
    """Extract a scalar or block value for a top-level key. Block scalars
    (> or |) are joined; folded blocks join with spaces like YAML does."""
    lines = fm.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^{key}:\s*(.*)$", line)
        if m is None:
            continue
        rest = m.group(1).strip()
        if rest not in (">", "|", ">-", "|-"):
            return rest
        block, j = [], i + 1
        while j < len(lines) and (lines[j].startswith("  ") or lines[j] == ""):
            block.append(lines[j].strip())
            j += 1
        joiner = " " if rest.startswith(">") else "\n"
        return joiner.join(block).strip()
    return None


def plugin_version():
    manifest = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
    return manifest["version"]


class SkillConformance(unittest.TestCase):
    def test_skills_exist(self):
        self.assertEqual(
            {p.parent.name for p in SKILLS},
            {"mission", "mission-resume", "mission-status", "mission-telemetry"},
        )

    def test_frontmatter_shape(self):
        for path in SKILLS:
            fm, _ = frontmatter(path)
            self.assertEqual(
                frontmatter_value(fm, "name"), path.parent.name,
                f"{path}: frontmatter name must match the directory name "
                "(the discovery surface)",
            )
            desc = frontmatter_value(fm, "description")
            self.assertTrue(desc, f"{path}: description is the trigger surface")
            self.assertLessEqual(
                len(desc), 1024,
                f"{path}: description exceeds the 1,024-char portability limit",
            )
            self.assertNotIn("<", desc, f"{path}: no XML tags in skill descriptions")

    def test_version_tracks_plugin(self):
        want = plugin_version()
        for path in SKILLS:
            fm, _ = frontmatter(path)
            self.assertIn(
                f'version: "{want}"', fm,
                f"{path}: skill metadata.version must equal plugin.json "
                f"version {want} (bumped together by convention)",
            )

    def test_body_length_budget(self):
        for path in SKILLS:
            _, body = frontmatter(path)
            self.assertLessEqual(
                len(body.splitlines()), 500,
                f"{path}: SKILL.md body over the 500-line ceiling",
            )

    def test_mission_links_every_reference_exactly_once(self):
        body = (REPO / "skills" / "mission" / "SKILL.md").read_text()
        for ref in REFERENCES:
            count = body.count(f"references/{ref.name}")
            self.assertEqual(
                count, 1,
                f"reference {ref.name} linked {count} times: zero means "
                "Claude never reads it; more than one means SKILL.md is not "
                "the single map the style guide requires",
            )


class AgentConformance(unittest.TestCase):
    def test_roster(self):
        self.assertEqual(
            {p.stem for p in AGENTS}, READ_ONLY_AGENTS | WRITER_AGENTS
        )

    def test_frontmatter_shape(self):
        for path in AGENTS:
            fm, _ = frontmatter(path)
            self.assertEqual(frontmatter_value(fm, "name"), path.stem, path)
            self.assertTrue(frontmatter_value(fm, "description"), path)
            color = frontmatter_value(fm, "color")
            self.assertIn(color, VALID_COLORS, f"{path}: color {color!r}")

    def test_tools_declared_least_privilege(self):
        for path in AGENTS:
            fm, _ = frontmatter(path)
            raw = frontmatter_value(fm, "tools")
            self.assertTrue(
                raw, f"{path}: tools must be declared — omitting grants everything"
            )
            tools = set(json.loads(raw))
            self.assertNotIn(
                "Agent", tools,
                f"{path}: specialists must not sub-delegate",
            )
            if path.stem in READ_ONLY_AGENTS:
                self.assertFalse(
                    tools & WRITE_TOOLS,
                    f"{path}: read-only charter contradicted by write tools",
                )
            if path.stem in {"implementation-engineer", "test-engineer"}:
                self.assertTrue(
                    {"Write", "Edit"} <= tools,
                    f"{path}: writer without write tools cannot do its job",
                )

    def test_prose_descriptions(self):
        for path in AGENTS:
            fm, _ = frontmatter(path)
            self.assertNotIn(
                "<example>", fm,
                f"{path}: transcript-shaped examples are the retired pattern; "
                "use prose descriptions plus a 'When to invoke' body section",
            )

    def test_delegation_roster_matches_agents(self):
        roster = (REPO / "skills" / "mission" / "references" / "delegation.md").read_text()
        for path in AGENTS:
            self.assertIn(path.stem, roster, f"{path.stem} missing from roster")


COMMISSION = REPO / "skills" / "mission" / "references" / "commission.md"
DELEGATION = REPO / "skills" / "mission" / "references" / "delegation.md"
CONTRACT = REPO / "skills" / "mission" / "references" / "intent-contract.md"
VERIFICATION = REPO / "skills" / "mission" / "references" / "verification.md"

# The commission's slots. A generated brief that drops one of these is the
# failure the whole synthesis stage exists to prevent, so the vocabulary is
# pinned rather than left to prose drift.
COMMISSION_SLOTS = [
    "IDENTITY",
    "OBJECTIVE",
    "CONTEXT",
    "SCOPE",
    "NON-GOALS",
    "AUTHORITY",
    "EVIDENCE STANDARD",
    "OUTPUT CONTRACT",
    "BUDGET",
]


class CommissionConformance(unittest.TestCase):
    """The commission is the artifact the runtime generates; these guard its
    shape and its single ownership."""

    def test_every_slot_is_documented(self):
        text = COMMISSION.read_text(encoding="utf-8")
        for slot in COMMISSION_SLOTS:
            self.assertIn(
                slot, text,
                f"commission.md does not document the {slot} slot; a brief "
                "missing a slot is the defect the pre-dispatch gate exists "
                "to catch",
            )

    def test_slot_template_has_exactly_one_owner(self):
        """delegation.md used to carry the packet template. Two copies of a
        slot list drift independently and the runtime has no rule for which
        wins."""
        delegation = DELEGATION.read_text(encoding="utf-8")
        duplicated = [s for s in COMMISSION_SLOTS if s in delegation]
        self.assertEqual(
            duplicated, [],
            f"delegation.md restates commission slots {duplicated}; the slot "
            "vocabulary lives in commission.md alone",
        )

    def test_gate_covers_the_across_set_checks(self):
        """Step repetition — two agents doing the same work — is the largest
        measured multi-agent failure mode. The sibling-ownership rule is what
        prevents it."""
        text = COMMISSION.read_text(encoding="utf-8")
        for probe in ("owned by exactly one", "siblings own", "overlapping files"):
            self.assertIn(
                probe, text,
                f"commission.md's pre-dispatch gate is missing {probe!r}",
            )

    def test_gate_covers_the_per_commission_checks(self):
        """A commission that passes the across-set checks but skips the
        per-commission ones can still ship with an empty evidence standard or
        an authority claim its chassis cannot back."""
        text = COMMISSION.read_text(encoding="utf-8")
        for probe in (
            "slots present and non-empty",
            "Self-contained",
            "Authority within",
            "evidence standard names a check",
            "output contract enumerates",
            "tool grant is non-empty",
        ):
            self.assertIn(
                probe, text,
                f"commission.md's per-commission gate is missing {probe!r}",
            )

    def test_roster_names_resolve_to_real_agents(self):
        """The existing roster test is one-directional: it catches an agent
        missing from delegation.md but not a delegation.md row naming an agent
        that does not exist."""
        names = {p.stem for p in AGENTS}
        rows = re.findall(r"^\| ([a-z][a-z-]+) \|", DELEGATION.read_text(), re.M)
        unknown = sorted(set(rows) - names)
        self.assertEqual(
            unknown, [],
            f"delegation.md rosters agents that do not exist: {unknown}",
        )


class ContractDriftControls(unittest.TestCase):
    def test_template_preserves_the_original_request(self):
        """Premature commitment to an early reading, with no path back to the
        user's words, is the dominant long-conversation failure."""
        self.assertIn(
            "## Original request", CONTRACT.read_text(encoding="utf-8"),
            "the contract template must carry the user's message verbatim",
        )

    def test_criteria_carry_provenance_tags(self):
        text = CONTRACT.read_text(encoding="utf-8")
        for tag in ("[stated]", "[entailed]", "[repo:", "[default]"):
            self.assertIn(
                tag, text,
                f"provenance tag {tag} absent; an untagged constraint is an "
                "invented requirement with nothing to trace it to",
            )

    def test_framing_mistakes_are_named_and_counted(self):
        """Unguided questions rate at human parity; questions checked against
        a named mistake list beat human-written ones. An uncounted list drifts
        silently as it is edited."""
        text = CONTRACT.read_text(encoding="utf-8")
        match = re.search(r"Nine framing mistakes disqualify", text)
        self.assertIsNotNone(
            match, "the calibration section must name and count its framing "
            "mistakes, not leave them as an unheaded list"
        )
        self.assertIn(
            "asking for a solution rather than a need", text,
            "the load-bearing framing mistake is missing",
        )

    def test_constraint_budget_is_named_with_its_basis(self):
        """Instruction-following degrades with count, and long context
        degrades recall at every length increment — the cap and the ceiling
        are the mechanical answer, and an unstated number is unenforceable."""
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("at most seven", text)
        self.assertIn("120 lines", text)
        self.assertIn(
            "unmeasured", text,
            "the cap must say plainly that it is a starting value, not a "
            "measured one, or it will be mistaken for evidence it is not",
        )

    def test_calibration_is_not_the_question_gate(self):
        """Calibration is non-blocking and defaulted; the question gate blocks.
        Merging them would either silence calibration or loosen the gate."""
        text = CONTRACT.read_text(encoding="utf-8")
        self.assertIn("## Calibration", text)
        self.assertIn("## The question gate", text)


class VerificationPortability(unittest.TestCase):
    def test_no_standing_verification_procedure(self):
        """Verification depth splits by model generation: one model's guidance
        is to remove these instructions, another's is to add them. The
        invariant ports; the procedure does not."""
        text = VERIFICATION.read_text(encoding="utf-8")
        banned = re.compile(
            r"always verify|use a subagent to verify|double-check"
            r"|audit, always|always before declaring",
            re.IGNORECASE,
        )
        hits = banned.findall(text)
        self.assertFalse(
            hits, f"verification.md carries standing depth prose: {hits}"
        )

    def test_states_the_non_authoring_invariant(self):
        """Absence of bad phrasing is not presence of the rule. Agents asked to
        judge their own work praise it — one measured study found 38 false
        positives per 100 self-verified plans."""
        self.assertIn(
            "did not produce the work",
            VERIFICATION.read_text(encoding="utf-8"),
            "verification.md must state that the agent producing a change is "
            "not the one that verifies it",
        )


class StyleHazards(unittest.TestCase):
    def test_no_hazard_patterns(self):
        surfaces = SKILLS + AGENTS + REFERENCES + [REPO / "README.md"]
        for path in surfaces:
            text = path.read_text(encoding="utf-8")
            for name, pattern in HAZARDS.items():
                hits = pattern.findall(text)
                self.assertFalse(
                    hits, f"{path}: {name} pattern present: {hits[:3]}"
                )


class ManifestParity(unittest.TestCase):
    def test_descriptions_identical(self):
        plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(
            plugin["description"],
            market["plugins"][0]["description"],
            "plugin.json and marketplace.json descriptions are duplicated on "
            "purpose and must change together",
        )

    def test_version_lives_only_in_plugin_json(self):
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
        self.assertNotIn(
            "version", market["plugins"][0],
            "a marketplace-entry version is silently ignored in favor of "
            "plugin.json; keeping it out avoids skew",
        )


if __name__ == "__main__":
    unittest.main()
