# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VERIFY_DOC = REPO / "docs/specs/ilc_cdl017_prelock_evidence_reverification_GAP_CDL017_PRELOCK_VERIFY_00_v0.1.md"


def _read(path: str | Path) -> str:
    return (REPO / path if isinstance(path, str) else path).read_text(encoding="utf-8")


def test_verification_doc_records_phase_tokens() -> None:
    text = _read(VERIFY_DOC)
    assert "cdl017_prelock_evidence_reverified_GAP_CDL017_PRELOCK_VERIFY_00" in text
    assert "cdl017_already_ratified_phase_765_confirmed_GAP_CDL017_PRELOCK_VERIFY_00" in text
    assert "cdl017_duplicate_open_ratify_blocked_GAP_CDL017_PRELOCK_VERIFY_00" in text


def test_decision_log_records_cdl017_ratified_phase_765() -> None:
    text = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    cdl017_rows = [line for line in text.splitlines() if line.startswith("| CDL-017 |")]
    assert len(cdl017_rows) == 1
    row = cdl017_rows[0]
    assert "| ratified |" in row
    assert "ratified_phase: 765" in row
    assert "ilc_cdl_017_validator_governance_framework_ratification_evidence_765_v0.1.md" in row


def test_prelock_evidence_records_q1_q6_and_completion_token() -> None:
    text = _read("docs/research/ilc_validator_agent_design_evidence_v0.1.md")
    for expected in (
        "q1_q6_answers_recorded_for_cdl_017_prelock",
        "cdl_017_prelock_codex_side_complete",
        "Derived sub-key with provable linkage",
        "Threshold-gated eligibility pool",
        "validation pools",
        "vrf_upgrade_threshold_validator_count 10",
        "distinct_cluster_floor_recommendation 4",
        "max_cluster_share_ceiling_recommendation 33",
    ):
        assert expected in text


def test_sim_validator_01_results_are_replayable_evidence() -> None:
    text = _read("docs/research/ilc_sim_validator_01_results_v0.1.md")
    assert "sim_validator_01_verdict=pass" in text
    assert "stake_floor_candidate_interval_micro_ecu 400000000-450000000" in text
    assert "vrf_upgrade_threshold_validator_count 10" in text
    assert "1944" in text


def test_sim_topology_01_results_lock_diversity_thresholds() -> None:
    text = _read("docs/research/ilc_sim_topology_01_results_v0.1.md")
    assert "sim_topology_01_verdict=pass" in text
    assert "validator_cluster_id" in text
    assert "distinct_cluster_floor_recommendation 4" in text
    assert "max_cluster_share_ceiling_recommendation 33" in text


def test_rust_validator_hooks_are_implemented_not_placeholders() -> None:
    text = _read("ilc_consensus/src/validator.rs")
    admit_start = text.index("pub fn admit_validator(")
    eject_start = text.index("pub fn eject_validator(")
    hook_region = text[admit_start : eject_start + 800]
    assert "pub fn admit_validator(" in hook_region
    assert "pub fn eject_validator(" in hook_region
    assert "unimplemented!" not in hook_region
    assert "ValidatorSet::rebuild_with" in hook_region


def test_forward_plan_blocks_duplicate_cdl017_open_ratify_path() -> None:
    text = _read("docs/specs/ilc_comprehensive_forward_plan_post_1575c_v0.1.md")
    assert "GAP-CDL017-PRELOCK-VERIFY-00 | NON-SENSITIVE | NO-PROMPT | COMPLETE" in text
    assert "GAP-CDL017-OPEN-00 | SENSITIVE" in text
    assert "SUPERSEDED" in text
    assert "CDL-017 already ratified at Phase 765" in text

