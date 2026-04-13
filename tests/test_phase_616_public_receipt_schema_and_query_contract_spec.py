from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path(
    'docs/specs/ilc_public_receipt_schema_and_query_contract_spec_616_v0.1.md'
)
TEST_PATH = Path('tests/test_phase_616_public_receipt_schema_and_query_contract_spec.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_616_g8_public_receipt_schema_and_query_contract_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_616_SUBJECT_TOKENS = ('phase 616', 'receipt')
PHASE_616_BACKFILL_SUBJECT_TOKENS = ('phase 616', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Receipt schema contract target and inherited discipline',
    '## 2. Minimum common public-authority field schema',
    '## 3. Receipt class schemas',
    '## 4. Receipt query contract',
    '## 5. Verification and failure-token discipline',
    '## 6. Explicit exclusions and deferred items',
)
REQUIRED_GOVERNANCE_TOKENS = (
    'public_receipt_schema_and_query_contract_spec_locked',
    'public_receipt_schema_anchors_to_phase_586_cluster',
    'minimum_common_field_schema_is_locked',
    'receipt_query_contract_is_read_only',
    'receipt_verification_must_fail_closed',
    'phase_616_carries_phase_612_mvp_gate_dependency',
    'receipt_issuance_and_query_is_second_of_five_mvp_touchpoints',
    'receipt_schema_does_not_widen_wallet_or_admission_authority',
)
REQUIRED_COMMON_FIELD_LINES = (
    '`artifact_kind` (string): identifies the receipt class carried by the object.',
    '`schema_version` (string): records the semantic version of the receipt schema.',
    '`receipt_id` (string): carries the unique deterministic receipt identifier.',
    '`signer_agent_id` (string): records the key-derived `agent_id` of the',
    '`authority_scope` (string): states the bounded scope of this receipt\'s',
    '`lineage_ref` (string or null): points to the predecessor receipt or Genesis',
    '`epoch_id` (string): records the validation epoch or issuance epoch',
    '`issued_at` (integer): stores the UTC issuance timestamp in seconds since the',
    '`verification_material_ref` (string or null): references deterministic',
    '`verification_status` (string): records one of `valid`, `failed`, or',
)
REQUIRED_CLASS_SCHEMA_ITEMS = (
    'public identity activation receipt:',
    '`activated_agent_id` (string, key-derived canonical agent_id),',
    '`admission_authority_scope` (string),',
    '`stake_binding_ref_or_null` (string or null)',
    'public namespace authority receipt:',
    '`namespace_label` (string),',
    '`bound_agent_id` (string),',
    '`activation_receipt_ref` (string)',
    'public quorum eligibility receipt or proof:',
    '`eligibility_subject_agent_id` (string),',
    '`snapshot_or_epoch_root_ref` (string),',
    '`proof_material_ref` (string)',
    'settlement-linked public legitimacy receipt:',
    '`settled_public_action_ref` (string),',
    '`quorum_receipt_ref` (string),',
    '`settlement_receipt_ref` (string),',
    '`payout_or_attribution_ref` (string)',
)
REQUIRED_FAILURE_TOKENS = (
    '`missing_lineage`',
    '`missing_scope`',
    '`missing_attestation`',
    '`schema_mismatch`',
    '`version_mismatch`',
    '`receipt_not_found`',
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


def _subject_matches(subject: str, tokens: tuple[str, ...]) -> bool:
    lowered = subject.lower()
    return all(token in lowered for token in tokens)


def _find_commit_ref(*, subject_tokens: tuple[str, ...]) -> str | None:
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
        if _subject_matches(subject, subject_tokens):
            return commit_hash
    return None


def _resolve_commit_ref(
    *, subject_tokens: tuple[str, ...], expected_paths: set[str]
) -> str:
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
        if _subject_matches(subject, subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError(f'commit_not_present_in_local_history:{subject_tokens}')


def _require_commit_or_skip(subject_tokens: tuple[str, ...]) -> None:
    if _find_commit_ref(subject_tokens=subject_tokens) is None:
        pytest.skip(f'commit_not_yet_present:{subject_tokens}')


def test_spec_document_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_all_required_governance_tokens_are_present() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_GOVERNANCE_TOKENS:
        assert token in text


def test_section_1_states_receipt_issuance_query_touchpoint_and_phase_586_anchor() -> None:
    text = _read(SPEC_PATH)
    assert 'receipt issuance and query touchpoint of the Phase 612' in text
    assert 'This spec anchors to the Phase 586 public receipt representation cluster' in text
    assert 'The common field set follows Phase 586 Section 4 exactly' in text
    assert 'no new receipt classes may be introduced beyond those locked in Phase' in text
    assert 'CDL-062 is not opened, and no substrate selection occurs here.' in text


def test_section_2_locks_all_ten_required_common_fields_with_type_and_description() -> None:
    text = _read(SPEC_PATH)
    for line in REQUIRED_COMMON_FIELD_LINES:
        assert line in text


def test_section_3_defines_schema_extensions_for_all_four_receipt_classes() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_CLASS_SCHEMA_ITEMS:
        assert item in text
    assert 'No fifth receipt class is introduced by this spec.' in text


def test_section_4_locks_query_contract_as_read_only_with_required_query_modes() -> None:
    text = _read(SPEC_PATH)
    assert 'Receipts are queryable by:' in text
    assert '- `receipt_id`' in text
    assert '- `signer_agent_id`' in text
    assert '- `artifact_kind + epoch_id`' in text
    assert 'The query response is a JSON array of matching receipt objects.' in text
    assert 'The query surface is read-only.' in text
    assert 'return an explicit error object with a machine-legible failure token' in text
    assert 'The query contract must respect the Phase 576 wallet boundary' in text


def test_section_5_locks_verification_failure_closed_discipline_and_minimum_failure_tokens() -> None:
    text = _read(SPEC_PATH)
    assert 'Receipt verification must fail closed on:' in text
    assert 'missing `lineage_ref` when required' in text
    assert 'missing `authority_scope`' in text
    assert 'missing attestation or `verification_material_ref`' in text
    assert 'schema mismatch' in text
    assert 'version mismatch' in text
    assert 'Verification failure must set `verification_status: failed`' in text
    assert '`failure_token` field with a structured code' in text
    for token in REQUIRED_FAILURE_TOKENS:
        assert token in text


def test_section_6_defers_runtime_implementation_and_claimability_semantics() -> None:
    text = _read(SPEC_PATH)
    assert '- runtime implementation of receipt issuance' in text
    assert '- runtime implementation of receipt query' in text
    assert '- public claimability or settlement semantics bound to receipt state' in text
    assert '- VRF mechanics for quorum eligibility proofs' in text
    assert '- final governance policy for receipt succession or revocation' in text


def test_phase_616_main_commit_touches_exactly_spec_and_test_paths() -> None:
    _require_commit_or_skip(PHASE_616_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_616_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_616_main_commit_touches_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_616_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_616_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_616_backfill_commit_touches_exactly_walkthrough_and_status_and_no_adr_cdl_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_616_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_616_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_BACKFILL_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
