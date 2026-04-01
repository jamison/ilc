from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_genesis_package_lifecycle_scoping_567_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_567_genesis_package_lifecycle_scoping.py')
PHASE_567_SUBJECT_PREFIX = 'phase 567'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Scope target',
    '## 2. Static peer-config JSON contract',
    '## 3. Test-grade genesis import contract',
    '## 4. Lifecycle persistence rule',
    '## 5. Packaging target',
    '## 6. Required observability',
)
REQUIRED_TOKENS = (
    'json_peer_config_format_selected',
    'test_grade_genesis_import_contract_selected',
    'venv_systemd_packaging_selected',
    'minimal_persistence_only_no_epoch_buffer_durability',
    'three_machine_logs_must_preserve_deterministic_error_tokens',
    'duplicate_peers_rejected_at_config_loader_boundary',
)
CONFIG_FIELDS = (
    '`node_id`',
    '`transport.kind`',
    '`transport.bind_host`',
    '`transport.bind_port`',
    '`transport.tls_cert_path`',
    '`transport.tls_key_path`',
    '`peers`',
)
GENESIS_FIELDS = (
    '`network_id`',
    '`genesis_bundle_path`',
    '`genesis_bundle_sha256`',
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


def _resolve_phase_567_commit_ref() -> str:
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
        if PHASE_567_SUBJECT_PREFIX not in normalized:
            continue
        if 'genesis' not in normalized and 'lifecycle scoping' not in normalized:
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_567_commit_not_present_in_local_history')


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_all_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_peer_config_json_contract_contains_required_fields() -> None:
    text = _read(DOC_PATH)
    for field in CONFIG_FIELDS:
        assert field in text


def test_genesis_import_contract_contains_required_fields() -> None:
    text = _read(DOC_PATH)
    for field in GENESIS_FIELDS:
        assert field in text


def test_phase_567_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_567_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_567_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_567_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
