from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path('docs/specs/ilc_integration_coherence_report_573_v0.1.md')
CAPSULE_PATH = Path('docs/specs/ilc_antigravity_context_capsule_v3.0.md')
TEST_PATH = Path('tests/test_phase_573_coherence_report_and_capsule_v3_0.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_573_SUBJECT_TOKEN = 'phase 573 coherence report and capsule v3.0'
EXACT_REQUIRED_MAIN_PATHS = {
    str(COHERENCE_PATH),
    str(CAPSULE_PATH),
    str(TEST_PATH),
}
REQUIRED_TOKENS = (
    'three_machine_transport_wrapper_lane_complete',
    'json_static_peer_config_and_startup_lane_complete',
    'venv_systemd_testbed_packaging_lane_complete',
    'three_machine_smoke_gate_complete',
    'http_machine_payment_skill_deferred_to_575_584',
    'http_machine_payment_ingress_deferred_to_595_plus',
    'multi_hop_still_deferred_after_573',
    'full_node_orchestration_redesign_still_pending',
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


def _resolve_phase_573_commit_ref() -> str:
    result = subprocess.run(
        ['git', 'log', '--format=%H%x09%s'],
        capture_output=True,
        check=True,
        text=True,
    )
    matching: list[str] = []
    for line in result.stdout.splitlines():
        if '\t' not in line:
            continue
        commit_hash, subject = line.split('\t', 1)
        if PHASE_573_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_573_commit_not_present_in_local_history')


def test_coherence_report_exists_and_contains_all_required_tokens() -> None:
    text = _read(COHERENCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_capsule_exists_is_versioned_v3_0_and_uses_current_forward_language() -> None:
    text = _read(CAPSULE_PATH)
    assert CAPSULE_PATH.name == 'ilc_antigravity_context_capsule_v3.0.md'
    assert text.splitlines()[0] == '# ILC Antigravity Context Capsule v3.0'
    assert 'Supersedes: docs/specs/ilc_antigravity_context_capsule_v2.9.md' in text
    assert 'HTTP machine-payment skill' in text
    assert 'HTTP machine-payment ingress' in text
    assert 'x402' not in text.lower()


def test_report_records_transport_config_packaging_and_smoke_lanes_as_complete() -> None:
    text = _read(COHERENCE_PATH)
    assert 'three_machine_transport_wrapper_lane_complete' in text
    assert 'json_static_peer_config_and_startup_lane_complete' in text
    assert 'venv_systemd_testbed_packaging_lane_complete' in text
    assert 'three_machine_smoke_gate_complete' in text
    assert 'phase_572_real_three_machine_operator_proof_recorded' in text


def test_report_records_deferred_items_correctly() -> None:
    text = _read(COHERENCE_PATH)
    assert 'http_machine_payment_skill_deferred_to_575_584' in text
    assert 'http_machine_payment_ingress_deferred_to_595_plus' in text
    assert 'multi_hop_still_deferred_after_573' in text
    assert 'full_node_orchestration_redesign_still_pending' in text


def test_phase_573_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_573_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_573_main_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_573_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
