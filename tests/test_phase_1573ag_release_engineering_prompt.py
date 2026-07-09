from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1573ag_g8_release_engineering_track_disposition_audit.md"
)
PHASE_1574_PROMPT = (
    REPO_ROOT
    / "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_1573ag_prompt_quarantines_release_engineering_track() -> None:
    text = _text(PROMPT)

    assert "# Phase 1573ag-G8: Release Engineering Track Disposition Audit" in text
    assert "**Sensitivity:** **NON-SENSITIVE**" in text
    assert "release-engineering-track` remains quarantined" in text
    assert "No wholesale merge is authorized" in text
    assert "No runtime changes are accepted from the branch in this phase" in text
    assert "No `ILC_CDL_MUTATION_AUTHORIZED` required" in text


def test_1573ag_prompt_requires_specific_supersession_dispositions() -> None:
    text = _text(PROMPT)

    assert "| `tools/public_export_sync.py` | `superseded` |" in text
    assert "| `config/public_surface_manifest_v0.1.json` | `superseded` |" in text
    assert "Superseded by Phase 1573n Option C and future graph-derived export" in text
    assert (
        "Superseded by Phase 1573n Option C and future "
        "`public_mirror_category`/AtlasSliceManifest export"
    ) in text


def test_1573ag_prompt_forbids_merge_publication_and_cherrypick() -> None:
    text = _text(PROMPT)

    for forbidden_claim in (
        "Merge `release-engineering-track`.",
        "Cherry-pick any commit from `release-engineering-track`.",
        "Push to GitHub or any public mirror.",
        "Change repository visibility.",
        "Grant public RC authority.",
    ):
        assert forbidden_claim in text


def test_1573ag_prompt_requires_file_by_file_disposition_and_tests() -> None:
    text = _text(PROMPT)

    assert "Every disposition row uses only `superseded`, `salvage_candidate`, or `reject`" in text
    assert "All files from `git diff --name-only main...release-engineering-track` are listed" in text
    assert "tests/test_phase_1573ag_release_engineering_track_disposition.py" in text
    assert "docs/specs/ilc_release_engineering_track_disposition_1573ag_v0.1.md" in text


def test_phase_1574_prompt_depends_on_1573ag_disposition() -> None:
    text = _text(PHASE_1574_PROMPT)

    assert "release_engineering_track_disposition_audit_committed_phase_1573ag" in text
    assert "quarantined release-engineering branch disposition complete" in text
