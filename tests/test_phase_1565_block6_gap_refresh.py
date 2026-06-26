# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1565 Block 6 sequence lock and gap refresh checks."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SEQUENCE_LOCK = REPO_ROOT / "docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md"
GAP_REFRESH = REPO_ROOT / "docs/specs/ilc_gap_refresh_1565_pre_block6_v0.1.md"
MATRIX = REPO_ROOT / "docs/specs/ilc_block6_public_rc_activation_matrix_template_v0.1.md"
PROMPT = REPO_ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1565_g10_block6_sequence_lock_gap_refresh.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1565_deliverables_exist_and_are_public_rc_excluded() -> None:
    for path in (SEQUENCE_LOCK, GAP_REFRESH, MATRIX):
        assert path.exists(), path
        text = _read(path)
        assert "PUBLIC_RC_EXCLUDE" in text
        assert "Phase 1565" in text or "1565" in text


def test_sequence_lock_records_tokens_and_exact_next_go() -> None:
    text = _read(SEQUENCE_LOCK)
    required_tokens = {
        "window_1565_1575_opened",
        "window_1564_closed_inherits_to_window_1565",
        "block6_sequence_lock_committed_phase_1565",
        "gap_refresh_1565_pre_block6_committed",
        "mempalace_rebuild_complete_phase_1565",
        "public_rc_activation_matrix_template_committed_phase_1565",
        "boolean_token_census_orphan_disposition_confirmed_phase_1565",
        "public_path_remains_blocked_phase_1565",
    }
    for token in required_tokens:
        assert token in text
    assert "GO Phase 1566" in text
    assert "Phase 1573a" in text
    assert "PUBLIC-RC-GATE-001" in text


def test_gap_refresh_records_required_block6_surfaces() -> None:
    text = _read(GAP_REFRESH)
    for required in (
        "OpenClaw",
        "Codex local harness",
        "Accelerated Logical-Epoch",
        "Wall-Clock Soak",
        "possible_orphan",
        "still_blocking",
        "default_off_guard",
        "CDL-098",
        "public path remains blocked",
        "Sidecar Typed-Subgraph",
        "ADR-0029",
        "sidecar-specific hyperedge",
    ):
        assert required in text
    assert "No ClawHub publication" in text
    assert "No public installability claim" in text


def test_activation_matrix_is_template_only_and_non_authorizing() -> None:
    text = _read(MATRIX)
    assert "Phase 1565 does not authorize any row" in text
    assert text.count("`template_only_pending_phase_1574`") >= 24
    assert "Native sidecar registry and recipe metadata" in text
    assert "Public sidecar or graph-projection serving" in text
    assert "Third-party sidecar registration/installability" in text
    assert "Sidecar-specific hyperedge activation" in text
    forbidden_claims = (
        "public_rc_authorized",
        "public_repository_push_authorized",
        "genesis_v04_signed_phase_1573",
    )
    for forbidden in forbidden_claims:
        assert forbidden not in text


def test_prompt_contains_lmdb_node_registration_section() -> None:
    text = _read(PROMPT)
    assert "## LMDB Node Registration" in text
    assert "docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md" in text
