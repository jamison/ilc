from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

SPEC_PATH = Path('docs/specs/ilc_public_init_admission_contract_spec_614_v0.1.md')
TEST_PATH = Path('tests/test_phase_614_public_init_admission_contract_spec.py')
WALKTHROUGH_PATH = Path(
    'docs/phases/phase_614_g8_public_init_admission_contract_spec_walkthrough.md'
)
STATUS_PATH = Path('docs/phases/STATUS.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_614_SUBJECT_TOKENS = ('phase 614', 'init admission')
PHASE_614_BACKFILL_SUBJECT_TOKENS = ('phase 614', 'walkthrough', 'backfill')
EXACT_REQUIRED_MAIN_PATHS = {
    str(SPEC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Init/admission touchpoint target',
    '## 2. Dependency and inherited canon',
    '## 3. Public init flow boundary',
    '## 4. Admission receipt contract',
    '## 5. Namespace authority binding at admission',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_GOVERNANCE_TOKENS = (
    'public_init_admission_contract_spec_614_locked',
    'init_flow_must_bind_to_canonical_receipt_lineage',
    'admission_requires_settled_admission_or_stake_binding_receipt',
    'init_flow_is_spec_form_only_not_runtime',
    'spec_form_closure_necessary_but_not_sufficient_for_mvp_gate',
    'interface_runtime_form_required_window_623_plus',
    'broader_public_rc_claims_remain_blocked_until_spec_and_runtime_both_complete',
    'no_wallet_widening_at_init_admission',
    'init_admission_does_not_open_agent_skills_lane',
)
REQUIRED_SECTION_3_ITEMS = (
    'canonical key derivation',
    'canonical key-derived `agent_id`',
    'activation receipt request',
    'wallet spend or transfer authority',
    'chain-side admission',
    'permissionless admission',
    'payment runtime',
    'ADR-0026 protocol/harness split',
    'ADR-0027 canonical lineage requirements',
)
REQUIRED_RECEIPT_FIELDS = (
    '`artifact_kind`',
    '`schema_version`',
    '`receipt_id`',
    '`signer_agent_id`',
    '`authority_scope`',
    '`lineage_ref`',
    '`epoch_id`',
    '`issued_at`',
    '`verification_material_ref`',
    '`verification_status`',
)
REQUIRED_NAMESPACE_RULES = (
    'bind to admitted identity lineage',
    'derivative of the key-derived `agent_id` rule',
    'Display aliases remain derivative, not authoritative.',
    '`CDL-042`',
)
REQUIRED_EXCLUSIONS = (
    'treating local key existence as equivalent to canonical public activation',
    'treating the init/admission spec as widening wallet authority',
    'treating any non-equal-canon source as if it establishes init/admission law',
    'opening Agent Skills or any new sub-lane through init/admission work',
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


def test_spec_document_contains_required_governance_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_GOVERNANCE_TOKENS:
        assert token in text


def test_section_1_states_spec_form_only_target_window_623_plus_and_blocked_broader_public_rc_claims() -> None:
    text = _read(SPEC_PATH)
    assert 'This Phase 614 packet is a spec-form artifact only.' in text
    assert 'Interface/runtime form is deferred to Window 623+' in text
    assert (
        'Broader public RC claims remain blocked until both spec and runtime '
        'forms complete.'
    ) in text


def test_section_3_defines_init_flow_boundary_and_out_of_scope_items() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_SECTION_3_ITEMS:
        assert item in text


def test_section_4_defines_admission_receipt_contract_minimum_field_set() -> None:
    text = _read(SPEC_PATH)
    for field_name in REQUIRED_RECEIPT_FIELDS:
        assert field_name in text
    assert 'Phase 587 boundary lock plus' in text
    assert '`CDL-040` admission scope' in text
    assert 'stake binding is required' in text


def test_section_5_covers_namespace_authority_binding_at_admission() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_NAMESPACE_RULES:
        assert item in text


def test_section_6_explicitly_prohibits_wallet_widening_and_agent_skills_lane_opening() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_EXCLUSIONS:
        assert item in text
    assert 'This phase does not widen wallet write, transfer, withdrawal, or spend' in text


def test_phase_614_main_commit_touches_expected_paths_only_and_no_cdl_adr_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_614_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_614_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_614_backfill_commit_subject_and_exact_path_set() -> None:
    _require_commit_or_skip(PHASE_614_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_614_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_614_backfill_commit_touches_no_cdl_adr_or_ilc_core_paths() -> None:
    _require_commit_or_skip(PHASE_614_BACKFILL_SUBJECT_TOKENS)
    commit_ref = _resolve_commit_ref(
        subject_tokens=PHASE_614_BACKFILL_SUBJECT_TOKENS,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
