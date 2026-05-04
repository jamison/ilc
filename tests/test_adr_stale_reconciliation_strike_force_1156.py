from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MEMO = REPO_ROOT / "docs/specs/ilc_adr_stale_reconciliation_strike_force_1156_v0.1.md"
GUIDANCE = REPO_ROOT / "docs/specs/ilc_window_1156_1165_candidate_phase_grouping_v0.1.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reconciliation_memo_exists_with_gate_token() -> None:
    text = _read(MEMO)

    assert "adr_stale_reconciliation_strike_force_1156" in text
    assert "This document does not accept any ADR" in text
    assert "mutate the signed Genesis v0.1 artifacts" in text


def test_reconciliation_memo_routes_near_term_adr_candidates() -> None:
    text = _read(MEMO)

    for token in (
        "adr_0020_acceptance_review_ready_priority",
        "adr_0012_acceptance_review_likely_ready",
        "adr_0022_acceptance_review_likely_ready_with_boundary_scope",
        "adr_0023_acceptance_review_scope_narrow_not_full_architecture",
        "adr_0008_acceptance_review_complete_boundary_ready",
    ):
        assert token in text


def test_reconciliation_memo_defers_non_current_window_adr_families() -> None:
    text = _read(MEMO)

    assert "adr_0009_0010_deferred_transport_distribution_reconciliation" in text
    assert "adr_0015_0016_0017_deferred_economic_rewrite_not_quick_cleanup" in text
    assert "larger economics rewrite/review" in text


def test_window_guidance_consumes_reconciliation_memo() -> None:
    text = _read(GUIDANCE)

    assert "ilc_adr_stale_reconciliation_strike_force_1156_v0.1.md" in text
    assert "ADR stale-reconciliation intake" in text
    assert "preserve its per-ADR routing tokens" in text


def test_window_guidance_no_longer_default_defers_adr_0008() -> None:
    text = _read(GUIDANCE)

    assert "previous default-defer posture is superseded" in text
    assert "boundary-acceptance candidate after the reconciliation commit" in text
    assert "Default routing for ADR-0008 is defer due to known open policy issues" not in text
    assert "adr_0008_acceptance_deferred_phase_1158_open_policy_issues" not in text


def test_window_guidance_records_adr_0023_scope_guard() -> None:
    text = _read(GUIDANCE)

    assert "ADR-0023 is the highest-risk Phase 1158 candidate" in text
    assert "adr_0023_acceptance_deferred_phase_1158_scope_overclaims_quality_signal_finality" in text
    assert "B5 | ADR-0023 accepted only with explicit scoped-acceptance" in text
