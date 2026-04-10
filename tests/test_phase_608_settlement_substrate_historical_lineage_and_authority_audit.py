from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

LINEAGE_AUDIT_PATH = Path('docs/specs/ilc_settlement_substrate_historical_lineage_audit_608_v0.1.md')
AUTHORITY_CLASSIFICATION_PATH = Path(
    'docs/specs/ilc_settlement_substrate_authority_tier_classification_608_v0.1.md'
)
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_608_settlement_substrate_historical_lineage_and_authority_audit.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_608_g8_window_607_612_settlement_substrate_historical_lineage_and_authority_audit_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_608_SUBJECT_TOKEN = 'phase 608 settlement substrate lineage audit'
PHASE_608_BACKFILL_SUBJECT_TOKEN = 'phase 608 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(LINEAGE_AUDIT_PATH),
    str(AUTHORITY_CLASSIFICATION_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
LINEAGE_HEADINGS = (
    '## 1. Audit target and inherited lock',
    '## 2. June 2025 exploratory option space',
    '## 3. December 2025 off-chain-first / later-chain strategic direction',
    '## 4. February 2026 drift-carrier and boundary language',
    '## 5. Current runtime and current-authority posture',
    '## 6. Audit conclusions and carry-forward constraints',
)
AUTHORITY_HEADINGS = (
    '## 1. Classification target',
    '## 2. Tier definitions and precedence rules',
    '## 3. Source-by-source classification',
    '## 4. Drift-carrier, bounded-claims, and safe-authority findings',
    '## 5. Phase 609 and 610 routing notes',
)
LINEAGE_TOKENS = (
    'phase_608_historical_lineage_audit_classifies_source_layers_without_settling_final_substrate',
    'june_2025_blockchain_and_settlement_discussion_is_exploratory_option_space',
    'december_2025_off_chain_first_later_chain_direction_is_historical_strategy_not_current_closure',
    'february_2026_capsule_v0_4_v0_5_language_is_historical_drift_carrier_not_final_substrate_law',
    'phase_602_public_tokenomics_statement_is_bounded_current_public_claims_surface_not_final_substrate_closure',
    'current_rc_runtime_internal_epoch_settled_ledger_truth_is_current_implementation_not_final_substrate_by_implication',
    'wallet_handoff_ilc_ecu_conflation_and_overbroad_anti_blockchain_language_are_phase_609_reconciliation_inputs',
    'historical_chat_and_whitepaper_material_must_not_outrank_current_canon',
)
AUTHORITY_TOKENS = (
    'phase_608_authority_classification_enforces_current_canon_over_historical_strategy',
    'capsule_v0_4_and_v0_5_classified_as_historical_drift_carriers',
    'capsule_v3_2_classified_as_current_context_surface_without_inheriting_v0_4_language',
    'wallet_agnostic_signing_handoff_classified_as_current_boundary_input_with_known_wording_inconsistency',
    'phase_600_classified_as_bounded_evidence_surface',
    'phase_602_classified_as_bounded_current_public_claims_surface',
    'adr_0026_classified_as_accepted_boundary_surface',
    'adr_0012_and_adr_0013_classified_below_accepted_boundary_authority',
    'whitepaper_v5_2_classified_as_historical_strategy_not_current_closure',
    'phase_609_must_consume_known_drift_carriers_and_safe_boundary_sources_separately',
)
REQUIRED_LAYER_STRINGS = (
    'June 2025 exploratory option space',
    'December 2025 off-chain-first / later-chain strategic direction',
    'February 2026 drift-carrier and boundary language',
    'current runtime and current-authority posture',
)
REQUIRED_DRIFT_CLASSIFICATIONS = (
    'historical drift-carrier language rather than silently inherited closure',
    'line-12 `ILC coin (ECU)` wording is a known inconsistency',
    'Phase 602 is a bounded current public-claims surface rather than final substrate closure',
)
ADR_CLASSIFICATION_STRINGS = (
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md` | Accepted | Tier A',
    '`docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md` | Proposed | Tier C',
    '`docs/adr/ADR_0013_External_Payment_Boundary_and_Third_Party_Independence.md` | Proposed | Tier C',
)
PHASE_609_ROUTING_STRINGS = (
    'Phase 609 must:',
    'line-12 `ILC coin (ECU)` inconsistency',
    'explicit reconciliation targets rather than inherited law',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _resolve_commit_ref(*, subject_token: str, expected_paths: set[str]) -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if subject_token not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f'commit_not_yet_present:{subject_token}')


def test_lineage_audit_exists_and_contains_required_headings() -> None:
    text = _read(LINEAGE_AUDIT_PATH)
    for heading in LINEAGE_HEADINGS:
        assert heading in text


def test_authority_classification_exists_and_contains_required_headings() -> None:
    text = _read(AUTHORITY_CLASSIFICATION_PATH)
    for heading in AUTHORITY_HEADINGS:
        assert heading in text


def test_lineage_audit_contains_required_tokens() -> None:
    text = _read(LINEAGE_AUDIT_PATH)
    for token in LINEAGE_TOKENS:
        assert token in text


def test_authority_classification_contains_required_tokens() -> None:
    text = _read(AUTHORITY_CLASSIFICATION_PATH)
    for token in AUTHORITY_TOKENS:
        assert token in text


def test_lineage_audit_separately_classifies_the_four_required_source_layers() -> None:
    text = _read(LINEAGE_AUDIT_PATH)
    for item in REQUIRED_LAYER_STRINGS:
        assert item in text


def test_lineage_audit_explicitly_classifies_drift_carriers_and_phase_602_as_bounded_surface() -> None:
    text = _read(LINEAGE_AUDIT_PATH)
    for item in REQUIRED_DRIFT_CLASSIFICATIONS:
        assert item in text


def test_authority_classification_places_adr_0026_above_adr_0012_and_adr_0013() -> None:
    text = _read(AUTHORITY_CLASSIFICATION_PATH)
    for item in ADR_CLASSIFICATION_STRINGS:
        assert item in text


def test_audit_packet_flags_wallet_handoff_inconsistency_and_routes_it_to_phase_609() -> None:
    lineage_text = _read(LINEAGE_AUDIT_PATH)
    authority_text = _read(AUTHORITY_CLASSIFICATION_PATH)
    assert 'line-12 `ILC coin (ECU)` wording is a known inconsistency' in lineage_text
    for item in PHASE_609_ROUTING_STRINGS:
        assert item in authority_text


def test_phase_608_main_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_608_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_608_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_608_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_608_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_608_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_608_backfill_commit_touches_expected_paths_only() -> None:
    _require_commit_or_skip(PHASE_608_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_608_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_608_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    _require_commit_or_skip(PHASE_608_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_608_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
