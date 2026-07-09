from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"
PROMPT_SCHEMA = ROOT / "docs/antigravity_tasks/README.md"
PROMPT_1574 = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)
PROMPT_1575 = (
    ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1575_g10_block6_public_rc_gate_001.md"
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_agents_records_sanitized_mirror_as_private_derived_artifact() -> None:
    text = _flat(AGENTS)
    assert "## Sanitized Public Mirror Maintenance Policy" in text
    assert "private canonical repository is the source of truth" in text
    assert "sanitized public mirror is a derived artifact" in text
    assert "Keep the sanitized mirror private" in text
    assert "Phase prompts must include a public-mirror maintenance task" in text
    assert "Normal `git push origin main` to the private canonical repo" in text


def test_claude_requires_mirror_disposition_in_prompts_and_walkthroughs() -> None:
    text = _flat(CLAUDE)
    assert "Sanitized public mirror policy" in text
    assert "must remain private until an explicit Phase" in text
    assert "Phase prompts and walkthroughs must record the mirror disposition" in text
    assert "source_private_commit" in text
    assert "filtered_public_head_sha" in text


def test_prompt_schema_requires_public_mirror_maintenance_section() -> None:
    text = _flat(PROMPT_SCHEMA)
    assert "## Public Mirror Maintenance section requirements" in text
    assert "Every phase prompt must include a `## Public mirror maintenance` section" in text
    assert "The sanitized mirror is a derived artifact and must not be hand-edited" in text
    assert "public mirror push, mirror repository visibility change" in text


def test_validator_enforces_public_mirror_maintenance_for_phase_1574_plus(tmp_path) -> None:
    prompt = tmp_path / "antigravity_prompt__phase_1574_g10_missing_public_mirror.md"
    prompt.write_text(
        "\n".join(
            [
                "# Phase 1574-G10: Missing Public Mirror Section",
                "## Mission",
                "x",
                "## Inputs",
                "x",
                "### §0a — Known-token audit",
                "x",
                "### §0b — Concept-discovery search",
                "x",
                "### §0c — Contradiction and non-claim search",
                "x",
                "### §0d — Source expansion and newly discovered tokens",
                "`If MemPalace is used, direct-read every returned path.`",
                "## Scope",
                "x",
                "## Deliverables",
                "x",
                "## Verification commands",
                "x",
                "## Walkthrough requirements",
                "No ellipses in walkthrough.",
                "## STATUS update requirements",
                "STATUS.md",
                "## LMDB Node Registration",
                "x",
                "## Commit",
                "x",
            ]
        ),
        encoding="utf-8",
    )
    assert "missing_section:public_mirror_maintenance" in validate(prompt)


def test_pending_publication_prompts_have_public_mirror_maintenance_policy() -> None:
    text_1574 = PROMPT_1574.read_text(encoding="utf-8")
    text_1575 = PROMPT_1575.read_text(encoding="utf-8")

    assert "## Public mirror maintenance" in text_1574
    assert "does not authorize public mirror push" in text_1574
    assert "source_private_commit" in text_1574
    assert "filtered_public_head_sha" in text_1574
    assert validate(PROMPT_1574) == []

    assert "## Public mirror maintenance" in text_1575
    assert "must remain private until the explicit public-RC authorization step" in text_1575
    assert "must not invent a target remote" in text_1575
    assert validate(PROMPT_1575) == []
