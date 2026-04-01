from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_transport_operationalization_boundary_lock_566_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_566_transport_operationalization_boundary_lock.py')
PHASE_566_SUBJECT_PREFIX = 'phase 566'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Purpose and pass target',
    '## 2. Selected runtime boundary',
    '## 3. Transport-kind operationalization rule',
    '## 4. TLS and identity posture',
    '## 5. Explicit exclusions',
    '## 6. Governance tokens',
)
REQUIRED_TOKENS = (
    'minimal_http_transport_wrapper_selected',
    'fallback_first_operational_proof_permitted_under_explicit_config',
    'kind_quic_remains_production_binding',
    'kind_http_may_satisfy_testbed_proof_when_explicitly_selected',
    'server_tls_plus_ilc_signature_locked_for_565_574',
    'full_node_orchestration_redesign_deferred_post_574',
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


def _resolve_phase_566_commit_ref() -> str:
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
        normalized = subject.lower()
        if PHASE_566_SUBJECT_PREFIX not in normalized:
            continue
        if 'transport operationalization' not in normalized and 'boundary lock' not in normalized:
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_566_commit_not_present_in_local_history')


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_all_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_runtime_boundary_names_http_gossip_transport_runtime_explicitly() -> None:
    text = _read(DOC_PATH)
    assert 'ilc_core/network/d2d/http_gossip_transport_runtime.py' in text
    assert 'must not duplicate the CDL-061 header contract' in text
    assert 'delegate path and header build/validation to `gossip_transport.py`' in text


def test_transport_kind_rule_preserves_quic_and_permits_explicit_http_proof() -> None:
    text = _read(DOC_PATH)
    assert 'ADR-0025 continues to define `kind=quic` as the production binding.' in text
    assert 'The first operational three-machine proof may use `kind=http`' in text
    assert 'does not authorize hidden downgrade logic' in text


def test_phase_566_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_566_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_566_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_566_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
