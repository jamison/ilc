from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_rc0_1_curated_genesis_bootstrap_lineage_lock_578_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_578_rc0_1_curated_genesis_bootstrap_lineage_lock.py')
PHASE_578_SUBJECT_TOKEN = 'phase 578 rc0.1 curated genesis bootstrap lineage lock'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Bounded RC target',
    '## 2. Curated lineage scope',
    '## 3. Bootstrap admission and promotion contract',
    '## 4. Key-compromise and rollback/tombstone posture',
    '## 5. Validator identity-binding boundary',
    '## 6. Explicit deferrals to RC0.1+',
)
REQUIRED_TOKENS = (
    'curated_genesis_lineage_testnet_only',
    'bootstrap_inventory_not_admission_authority_by_itself',
    'candidate_discovery_not_active_peer_admission',
    'explicit_promotion_required_before_runtime_peer_use',
    'cdl_002_compromise_containment_revoke_recover_preserved',
    'rollback_and_tombstone_posture_explicit_for_curated_testnet',
    'validator_identity_binding_gap_not_silently_closed',
    'permissionless_public_admission_deferred_post_rc0_1',
)
BOOTSTRAP_RULES = (
    'Bootstrap inventory is not admission authority by itself.',
    'Candidate discovery is not active-peer admission.',
    'Explicit promotion is required before runtime peer use.',
    'Approved runtime peer sets derive from approved inventory plus overrides minus',
    'TLS fingerprint verification',
)
POSTURE_RULES = (
    'The CDL-002 compromise trigger, containment, revocation, replacement, and',
    'Rollback or tombstone posture for the curated testnet must remain explicit,',
    'Revoked or quarantined lineage state must not remain authoritative',
    'Compromise or rollback handling must not silently re-admit or silently',
)
IDENTITY_BOUNDARY_RULES = (
    'The deferred CDL-052 binding gap between node-submission identity and canonical',
    'operator-authorized curated non-validator submission identity model',
    'must not rely on silent validator-identity equivalence',
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


def _resolve_phase_578_commit_ref() -> str:
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
        if PHASE_578_SUBJECT_TOKEN not in subject.lower():
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_578_commit_not_present_in_local_history')


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_three_contains_bootstrap_admission_and_promotion_rules() -> None:
    text = _read(DOC_PATH)
    for rule in BOOTSTRAP_RULES:
        assert rule in text


def test_section_four_contains_compromise_and_rollback_tombstone_rules() -> None:
    text = _read(DOC_PATH)
    for rule in POSTURE_RULES:
        assert rule in text


def test_section_five_contains_validator_identity_binding_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for rule in IDENTITY_BOUNDARY_RULES:
        assert rule in text


def test_phase_578_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_578_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_578_commit_touches_no_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_phase_578_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
