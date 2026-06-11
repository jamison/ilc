from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1555p_v0.1.md"
OLD_MATRIX = ROOT / "docs/specs/ilc_accepted_adr_cdl_public_rc_coverage_matrix_1387a_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix17_adr_cdl_coverage_matrix_refresh_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1545p_fix17_g10_adr_cdl_coverage_matrix_refresh_and_acceptance_batch.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_matrix_emits_required_part_a_and_part_b_tokens() -> None:
    text = read(MATRIX)
    for token in (
        "phase_1545p_fix17_adr_cdl_coverage_matrix_refresh_committed",
        "adr_cdl_coverage_matrix_refreshed_through_phase_1555p",
        "adr_0018_deferred_outside_public_rc_phase_1545p_fix17",
        "adr_0015_deferred_outside_public_rc_phase_1545p_fix17",
        "adr_0017_deferred_outside_public_rc_phase_1545p_fix17",
        "new_cdl_rows_091_097_covered_in_matrix_phase_1545p_fix17",
        "adr_0040_through_0044_covered_in_matrix_phase_1545p_fix17",
        "public_path_remains_blocked_phase_1545p_fix17",
        "adr_0010_accepted_phase_1545p_fix17",
        "adr_0013_accepted_phase_1545p_fix17",
        "adr_0014_accepted_phase_1545p_fix17",
        "adr_0016_accepted_phase_1545p_fix17",
        "adr_0024_acceptance_deferred_evidence_gap_phase_1545p_fix17",
        "adr_0024_optional_harness_layer_not_public_rc_blocker_phase_1545p_fix17c",
        "skill_node_l3_deferred_phase_1545p_fix17c",
    ):
        assert token in text

    assert "adr_0024_accepted_phase_1545p_fix17" not in text


def test_old_matrix_is_tombstoned_to_1555p_refresh() -> None:
    text = read(OLD_MATRIX)
    assert "superseded_by_phase_1545p_fix17_matrix_1555p" in text
    assert "ilc_accepted_adr_cdl_public_rc_coverage_matrix_1555p_v0.1.md" in text


def test_new_adr_and_cdl_rows_are_covered_with_no_unknown_or_blocking_rows() -> None:
    text = read(MATRIX)
    for adr in ("ADR-0040", "ADR-0041", "ADR-0042", "ADR-0043", "ADR-0044"):
        assert f"| {adr} |" in text
    for cdl in ("CDL-053", "CDL-091", "CDL-092", "CDL-093", "CDL-094", "CDL-095", "CDL-096", "CDL-097"):
        assert f"| {cdl} |" in text
    assert "| Unknown rows | 0 | pass |" in text
    assert "| Public-RC blocking rows | 0 | pass |" in text
    assert "public_rc_blocking" not in text


def test_deferred_and_evidence_gap_adrs_are_explicitly_classified() -> None:
    text = read(MATRIX)
    assert "| ADR-0015 | Proposed | explicitly_deferred_outside_public_rc |" in text
    assert "| ADR-0017 | Proposed | explicitly_deferred_outside_public_rc |" in text
    assert "| ADR-0018 | Proposed | explicitly_deferred_outside_public_rc |" in text
    assert "| ADR-0024 | Proposed | proposed_deferred_optional_harness_layer |" in text
    assert "| ADR-0010 | Accepted | implemented_or_verified_for_public_rc |" in text
    assert "| ADR-0013 | Accepted | governance_or_documentation_only |" in text
    assert "| ADR-0014 | Accepted | implemented_or_verified_for_public_rc |" in text
    assert "| ADR-0016 | Accepted | explicitly_deferred_outside_public_rc |" in text
    assert "root skills are not required for public RC" in text
    assert "`.codex-plugin/skills/*` remains a local adapter surface, not protocol canon" in text
    assert "Graph-native `skill_node` semantics are deferred to Tier 3 / L3" in text


def test_part_b_accepts_only_verified_adr_status_lines() -> None:
    for adr in ("0010", "0013", "0014", "0016"):
        candidates = list((ROOT / "docs/adr").glob(f"ADR_{adr}_*.md"))
        assert len(candidates) == 1
        text = read(candidates[0])
        assert "**Status:** Accepted" in text
        assert f"adr_{adr}_accepted_phase_1545p_fix17" in text

    candidates = list((ROOT / "docs/adr").glob("ADR_0024_*.md"))
    assert len(candidates) == 1
    assert "**Status:** Proposed" in read(candidates[0])


def test_non_accepted_proposed_adr_status_lines_remain_proposed() -> None:
    for adr in ("0010", "0013", "0014", "0016", "0024"):
        candidates = list((ROOT / "docs/adr").glob(f"ADR_{adr}_*.md"))
        assert len(candidates) == 1
    for adr in ("0015", "0017", "0018", "0024"):
        candidates = list((ROOT / "docs/adr").glob(f"ADR_{adr}_*.md"))
        assert len(candidates) == 1
        assert "**Status:** Proposed" in read(candidates[0])


def test_status_planning_prompt_and_walkthrough_record_part_a_boundary() -> None:
    for path in (STATUS, PLANNING_INDEX, WALKTHROUGH):
        text = read(path)
        assert "phase_1545p_fix17_adr_cdl_coverage_matrix_refresh_committed" in text
        assert "public_path_remains_blocked_phase_1545p_fix17" in text
    assert "GO Fix17-B" in read(STATUS)
    assert "adr_0016_accepted_phase_1545p_fix17" in read(STATUS)
    assert "adr_0024_public_rc_boundary_reframed_phase_1545p_fix17c" in read(STATUS)
    assert "adr_0024_optional_harness_layer_not_public_rc_blocker_phase_1545p_fix17c" in read(PLANNING_INDEX)

    prompt = read(PROMPT)
    assert "PUBLIC_RC_EXCLUDE: phase_1545p_fix17_private_prompt" in prompt


def test_adr0024_remains_proposed_but_is_not_public_rc_blocker() -> None:
    adr = read(ROOT / "docs/adr/ADR_0024_Agent_Skills_Infrastructure.md")
    assert "**Status:** Proposed" in adr
    assert "Absence of a root `skills/` directory is not a public-RC blocker." in adr
    assert "Agent Skills are procedural instructions for agent harnesses" in adr
    assert "becomes ILC-homoiconic only if a later protocol explicitly ingests it" in adr
    assert ".codex-plugin/skills/*` surface is a local Codex/plugin harness adapter" in adr
    assert "Do not treat root `skills/` as a public-RC requirement." in adr
