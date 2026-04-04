from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tools.testbed.check_phase_595_rc0_1_strike_force import check_phase_595_strike_force

DOC_PATH = Path('docs/specs/ilc_rc0_1_strike_force_consolidation_and_runtime_hardening_595_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
RUNNER_PATH = Path('tools/testbed/run_phase_595_rc0_1_strike_force.py')
CHECKER_PATH = Path('tools/testbed/check_phase_595_rc0_1_strike_force.py')
TEST_PATH = Path('tests/test_phase_595_rc0_1_strike_force_consolidation_and_runtime_hardening.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_595_g8_rc0_1_strike_force_consolidation_and_runtime_hardening_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_595_SUBJECT_TOKEN = 'phase 595 strike force consolidation and runtime hardening'
PHASE_595_BACKFILL_SUBJECT_TOKEN = 'phase 595 walkthrough and status backfill'
REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(RUNNER_PATH),
    str(CHECKER_PATH),
    str(TEST_PATH),
}
OPTIONAL_MAIN_PATHS = {
    'tools/agent_loop_v1.py',
    'ilc_core/rc/economic_cycle_runtime.py',
    'tools/query_rc0_1_economic_state.py',
    'tools/check_rc0_1_economic_state.py',
    'tools/run_rc0_1_economic_proof.py',
    'tools/testbed/run_economic_replay_drills.py',
    'tools/testbed/run_economic_negative_path_drills.py',
    'tools/run_rc0_1_release_gate.py',
    'tools/check_rc0_1_release_gate.py',
    'tools/run_rc0_1_release_candidate.py',
}
ALLOWED_MAIN_PATHS = REQUIRED_MAIN_PATHS | OPTIONAL_MAIN_PATHS
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Consolidation mandate and historical boundary',
    '## 2. Dependency tiers, inherited canon, and allowed runtime surfaces',
    '## 3. Residual Phase 582-584 obligations absorbed here',
    '## 4. Runtime hardening tranche executed here',
    '## 5. Deterministic release evidence, claim discipline, and gate tightening',
    '## 6. Genesis/testnet posture and public-boundary non-goals',
    '## 7. Forbidden interpretations and exclusions',
    '## 8. Explicit deferrals to later windows and lanes',
)
REQUIRED_TOKENS = (
    'phase_595_consolidates_remaining_rc0_1_testnet_closure_and_hardening',
    'phase_595_supersedes_unexecuted_582_584_as_execution_units_not_historical_inputs',
    'cdl_v7_reproducibility_disposition_must_be_explicit_in_post_594_form',
    'outbound_http_machine_payment_skill_must_be_attached_or_explicitly_deferred',
    'phase_583_and_584_closure_obligations_are_absorbed_here',
    'runtime_hardening_must_preserve_576_581_boundaries',
    'wallet_history_query_and_export_must_remain_read_only_and_durable',
    'settlement_replay_negative_path_and_release_gate_must_be_committed_head_green',
    'release_candidate_and_release_gate_outputs_must_remain_machine_legible',
    'rc0_1_testnet_claims_remain_bounded_not_public_legitimacy_claims',
    'curated_genesis_testnet_posture_remains_in_force_without_public_upgrade',
    'genesis_carry_forward_queue_remains_explicit_not_silently_closed',
    'inbound_http_machine_payment_ingress_remains_deferred_to_later_window',
    'phase_595_outputs_feed_window_595_plus_planning_without_replacing_it',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_phase_575_584_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`',
    '`docs/specs/ilc_rc0_1_persisted_graph_contract_lock_577_v0.1.md`',
    '`docs/specs/ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md`',
    '`docs/specs/ilc_rc0_1_agent_behavioral_loop_runtime_cutover_579_v0.1.md`',
    '`docs/specs/ilc_rc0_1_7_plus_1_panel_live_submission_integration_580_v0.1.md`',
    '`docs/specs/ilc_rc0_1_ecu_settlement_wallet_query_integration_581_v0.1.md`',
    '`docs/specs/ilc_post_586_strike_force_runtime_hardening_packet_v0.1.md`',
    '`docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md`',
    '`docs/specs/ilc_window_585_594_handoff_594_v0.1.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`tools/agent_loop_v1.py`',
    '`tools/query_rc0_1_economic_state.py`',
    '`tools/check_rc0_1_economic_state.py`',
    '`tools/run_rc0_1_economic_proof.py`',
    '`tools/testbed/run_economic_replay_drills.py`',
    '`tools/testbed/run_economic_negative_path_drills.py`',
    '`tools/run_rc0_1_release_gate.py`',
    '`tools/check_rc0_1_release_gate.py`',
    '`tools/run_rc0_1_release_candidate.py`',
    '`tools/run_rc0_1_release_claim.py`',
    '`tools/check_rc0_1_release_claim.py`',
    '`tools/render_rc0_1_readiness_delta.py`',
)
SECTION_THREE_RULES = (
    'The reproducibility disposition in this packet is explicit and bounded.',
    'protocol completeness is not implied by silence',
    'the outbound `HTTP machine-payment skill` lane is recorded here as an explicit',
    'The coherence and closure obligations assigned to candidate Phases 583-584 are',
)
SECTION_FOUR_RULES = (
    'The runtime hardening tranche executed here covers wallet/history hardening,',
    'Committed-head replay, negative-path, release-gate, release-candidate, and',
    'preserve the Phase 576 accounting-only wallet boundary',
)
SECTION_FIVE_RULES = (
    'Release-candidate, release-gate, release-claim, and readiness-delta outputs',
    'Bounded RC0.1 claims remain operator-auditable testnet evidence.',
    'The checker and runner fail closed if the reproducibility disposition,',
)
SECTION_SIX_RULES = (
    'The RC0.1 curated Genesis/testnet posture remains bounded, operator-managed,',
    'This phase does not silently settle Genesis governance dilution,',
    'Any reference to Genesis in this packet stays within RC0.1 lineage, bootstrap,',
)
SECTION_SEVEN_RULES = (
    '- claiming that candidate Phases 582-584 executed historically when they did not',
    '- treating the post-594 consolidation packet as authority to reopen public-release law',
    '- treating inbound `HTTP machine-payment ingress` as part of this phase',
)
SECTION_EIGHT_RULES = (
    '- inbound `HTTP machine-payment ingress` to a later window',
    '- Genesis governance dilution closure to its dedicated carry-forward lane',
    '- the post-Genesis capability-proof lane to its separate future vehicle',
    'This packet feeds Window 595+ planning without replacing it.',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(*, subject_token: str) -> str:
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
        changed_paths = _changed_paths_for_commit(commit_ref)
        if REQUIRED_MAIN_PATHS.issubset(changed_paths) and changed_paths.issubset(ALLOWED_MAIN_PATHS):
            return commit_ref
        if changed_paths == EXACT_REQUIRED_BACKFILL_PATHS:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_token}')


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_carries_mandatory_dependency_bundle_and_tier_labels() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text
    for item in (
        'the 585-594 outputs are frozen public-boundary inputs, not surfaces reopened by this phase',
        'the runtime and release tools are bounded RC0.1 implementation surfaces, not self-executing public law',
        'the curated Genesis/testnet posture from Phase 578 remains in force for RC0.1',
        'the Genesis carry-forward queue from the 594 handoff remains explicit, open, and non-equal-canon for this phase',
    ):
        assert item in text


def test_section_three_contains_residual_582_584_closure_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_THREE_RULES:
        assert item in text


def test_section_four_contains_runtime_hardening_tranche_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FOUR_RULES:
        assert item in text


def test_section_five_contains_deterministic_release_evidence_and_claim_discipline_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_FIVE_RULES:
        assert item in text


def test_section_six_contains_genesis_testnet_posture_and_non_goal_rules() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SIX_RULES:
        assert item in text


def test_section_seven_contains_forbidden_interpretations() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_SEVEN_RULES:
        assert item in text


def test_section_eight_contains_explicit_defers() -> None:
    text = _read(DOC_PATH)
    for item in SECTION_EIGHT_RULES:
        assert item in text


def test_runner_and_checker_exist_and_are_importable() -> None:
    assert RUNNER_PATH.exists()
    assert CHECKER_PATH.exists()
    subprocess.run(['python3', '-m', 'py_compile', str(RUNNER_PATH), str(CHECKER_PATH)], check=True)


def test_checker_passes_on_deterministic_synthetic_valid_manifest(tmp_path: Path) -> None:
    spec_path = tmp_path / 'spec.md'
    spec_path.write_text(_read(DOC_PATH), encoding='utf-8')
    candidate_manifest_path = tmp_path / 'candidate.json'
    release_manifest_path = tmp_path / 'release.json'
    claim_manifest_path = tmp_path / 'claim.json'
    delta_manifest_path = tmp_path / 'delta.json'
    phase_581_manifest_path = tmp_path / 'phase_581.json'
    economic_claim_summary = {
        'runtime_store_kind': 'lmdb_public_runtime_v0.1',
        'settlement_status': 'applied',
    }
    _write_json(candidate_manifest_path, {'release_claim_manifest_path': str(claim_manifest_path)})
    _write_json(release_manifest_path, {'release_verdict_stdout': 'rc0_1_release_verdict=pass'})
    _write_json(claim_manifest_path, {
        'candidate_manifest_path': str(candidate_manifest_path),
        'claim_verdict_stdout': 'rc0_1_release_claim_verdict=pass',
        'economic_claim_summary': economic_claim_summary,
    })
    _write_json(delta_manifest_path, {'economic_claim_summary': economic_claim_summary})
    _write_json(phase_581_manifest_path, {'marker': 'phase_581_settlement_wallet_query_ok'})
    manifest_path = tmp_path / 'manifest.json'
    _write_json(manifest_path, {
        'phase_581': {'marker': 'phase_581_settlement_wallet_query_ok', 'manifest_path': str(phase_581_manifest_path)},
        'reproducibility_disposition': {
            'status': 'explicit_bounded_post_594_disposition',
            'completion_non_claim': 'protocol completeness is not implied by silence',
            'known_approximations': [],
            'support_lane_caveats': ['outbound_http_machine_payment_skill_support_lane_only'],
        },
        'machine_payment_lane': {'status': 'explicit_defer', 'defer_reason': 'bounded_cli_mcp_surface_left_unchanged'},
        'runtime_hardening': {
            'phase_581_pass': True,
            'release_gate_pass': True,
            'release_claim_pass': True,
            'negative_path_pass': True,
            'replay_pass': True,
            'runtime_store_kind': 'lmdb_public_runtime_v0.1',
            'settlement_status': 'applied',
        },
        'release_candidate': {
            'candidate_manifest_path': str(candidate_manifest_path),
            'release_manifest_path': str(release_manifest_path),
            'claim_manifest_path': str(claim_manifest_path),
            'delta_manifest_path': str(delta_manifest_path),
            'release_candidate_ready': True,
            'claim_verdict_pass': True,
            'publication_pending_items': ['publish_release_notes'],
            'post_rc_deferred_scope': [{'item': 'mutual_tls_rollout'}],
        },
        'genesis_boundary': {
            'status': 'curated_testnet_posture_preserved',
            'public_upgrade': False,
            'carry_forward_queue': [
                'Genesis governance dilution closure',
                'freshness-gate provenance closure',
                'Genesis accrual-governor provenance reconciliation',
                'post-Genesis capability-proof lane disposition',
            ],
        },
        'window_integrity': {
            'phase_575_584_sequence_lock_token_present': True,
            'window_585_594_handoff_token_present': True,
            'required_window_tokens': [
                'cdl_v7_reproducibility_disposition_required_before_phase_584',
                'window_595_plus_is_next_authorized_strategic_boundary',
            ],
        },
    })
    payload = check_phase_595_strike_force(spec_path=spec_path, manifest_path=manifest_path)
    assert payload['marker'] == 'phase_595_rc0_1_strike_force_ok'


def test_checker_fails_missing_reproducibility_disposition_with_required_token(tmp_path: Path) -> None:
    spec_path = tmp_path / 'spec.md'
    spec_path.write_text(_read(DOC_PATH), encoding='utf-8')
    manifest_path = tmp_path / 'manifest.json'
    _write_json(manifest_path, {
        'phase_581': {'marker': 'phase_581_settlement_wallet_query_ok'},
        'reproducibility_disposition': {'status': 'missing'},
        'machine_payment_lane': {'status': 'explicit_defer', 'defer_reason': 'x'},
        'runtime_hardening': {
            'phase_581_pass': True,
            'release_gate_pass': True,
            'release_claim_pass': True,
            'negative_path_pass': True,
            'replay_pass': True,
            'runtime_store_kind': 'lmdb_public_runtime_v0.1',
            'settlement_status': 'applied',
        },
        'release_candidate': {
            'candidate_manifest_path': str(tmp_path / 'candidate.json'),
            'release_manifest_path': str(tmp_path / 'release.json'),
            'claim_manifest_path': str(tmp_path / 'claim.json'),
            'delta_manifest_path': str(tmp_path / 'delta.json'),
            'release_candidate_ready': True,
            'claim_verdict_pass': True,
            'publication_pending_items': ['x'],
            'post_rc_deferred_scope': [{'item': 'y'}],
        },
        'genesis_boundary': {
            'status': 'curated_testnet_posture_preserved',
            'public_upgrade': False,
            'carry_forward_queue': [
                'Genesis governance dilution closure',
                'freshness-gate provenance closure',
                'Genesis accrual-governor provenance reconciliation',
                'post-Genesis capability-proof lane disposition',
            ],
        },
        'window_integrity': {
            'phase_575_584_sequence_lock_token_present': True,
            'window_585_594_handoff_token_present': True,
            'required_window_tokens': [
                'cdl_v7_reproducibility_disposition_required_before_phase_584',
                'window_595_plus_is_next_authorized_strategic_boundary',
            ],
        },
    })
    for path in ('candidate.json', 'release.json', 'claim.json', 'delta.json'):
        _write_json(tmp_path / path, {})
    try:
        check_phase_595_strike_force(spec_path=spec_path, manifest_path=manifest_path)
    except Exception as exc:
        assert getattr(exc, 'token', None) == 'phase_595_reproducibility_disposition_missing'
    else:
        raise AssertionError('expected_phase_595_reproducibility_disposition_missing')


def test_phase_595_main_commit_touches_required_paths_and_no_path_outside_allowed_set() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_595_SUBJECT_TOKEN)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert REQUIRED_MAIN_PATHS.issubset(changed_paths)
    assert changed_paths.issubset(ALLOWED_MAIN_PATHS)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)


def test_phase_595_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(subject_token=PHASE_595_BACKFILL_SUBJECT_TOKEN)
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_phase_575_584_sequence_lock') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_window_585_594_handoff_594') for path in changed_paths)
