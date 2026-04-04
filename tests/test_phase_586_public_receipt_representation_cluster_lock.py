from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_586_public_receipt_representation_cluster_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_586_g8_public_receipt_representation_cluster_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_586_SUBJECT_TOKEN = 'phase 586 public receipt representation lock'
PHASE_586_BACKFILL_SUBJECT_TOKEN = 'phase 586 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Public receipt cluster target',
    '## 2. Receipt classes in scope',
    '## 3. Uniform representation discipline',
    '## 4. Common public-authority field set',
    '## 5. Receipt-class specific requirements',
    '## 6. Namespace authority receipt disposition',
    '## 7. Verification and failure-token discipline',
    '## 8. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'public_receipt_representation_cluster_locked',
    'public_identity_activation_receipt_required',
    'public_quorum_eligibility_receipt_or_proof_required',
    'settlement_linked_public_legitimacy_receipt_required',
    'public_namespace_authority_receipt_required',
    'receipt_representation_must_be_self_describing_lineage_aware_and_attested',
    'public_authority_boundaries_require_signed_cryptographic_attestation',
    'receipt_schema_and_verification_rules_precede_public_runtime_integration',
    'promotion_receipt_is_precedent_not_substitute_for_public_authority_cluster',
    'non_equal_canon_receipt_sources_must_be_labeled',
    'phase_586_carries_window_585_594_dependency_bundle',
    'receipt_schema_v0_1_draft_is_supporting_context_only',
)
DEPENDENCY_BUNDLE_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`',
    '`docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`',
    '`docs/specs/ilc_constitutional_decision_log_v0.1.md`',
    '`CDL-001`',
    '`CDL-002`',
    '`CDL-003`',
    '`CDL-004`',
    '`CDL-007`',
    '`CDL-009`',
    '`CDL-013`',
    '`CDL-022`',
    '`CDL-023`',
    '`CDL-040`',
    '`CDL-042`',
    '`CDL-045`',
    '`CDL-V6`',
)
REQUIRED_RECEIPT_CLASSES = (
    '- public identity activation receipt',
    '- public namespace authority receipt',
    '- public quorum eligibility receipt or proof',
    '- settlement-linked public legitimacy receipt',
)
REPRESENTATION_DISCIPLINE_ITEMS = (
    '- explicit artifact kind and schema version',
    '- canonical serialization rule',
    '- stable machine-legible field names',
    '- signer or attestor identity',
    '- authority scope',
    '- lineage or predecessor references where applicable',
    '- deterministic verification references or material',
    '- explicit verification outcome or failure-token vocabulary',
)
COMMON_FIELD_SET_ITEMS = (
    '- `artifact_kind`',
    '- `schema_version`',
    '- `receipt_id` or `proof_id`',
    '- `signer_agent_id` or `attestor_agent_id`',
    '- `authority_scope`',
    '- `lineage_ref`',
    '- `epoch_id`',
    '- `issued_at`',
    '- `verification_material_ref`',
    '- `verification_status`',
)
NON_EQUAL_CANON_ITEMS = (
    '`docs/specs/ilc_receipt_schema_v0.1.md` is draft supporting context only',
    '`CDL-038` is a narrow receipt precedent for extension structure',
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


def test_document_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_document_contains_required_governance_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_one_carries_mandatory_window_dependency_bundle() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_BUNDLE_ITEMS:
        assert item in text


def test_section_two_contains_full_required_receipt_class_set() -> None:
    text = _read(DOC_PATH)
    for item in REQUIRED_RECEIPT_CLASSES:
        assert item in text


def test_section_three_contains_full_shared_representation_discipline() -> None:
    text = _read(DOC_PATH)
    for item in REPRESENTATION_DISCIPLINE_ITEMS:
        assert item in text


def test_section_four_contains_full_common_public_authority_field_set() -> None:
    text = _read(DOC_PATH)
    for item in COMMON_FIELD_SET_ITEMS:
        assert item in text


def test_section_six_records_first_class_namespace_authority_receipt_decision() -> None:
    text = _read(DOC_PATH)
    assert 'Public namespace authority carries a first-class receipt surface' in text
    assert 'never float free of the identity activation and settlement-linked legitimacy' in text


def test_section_eight_labels_draft_and_non_equal_canon_receipt_sources_correctly() -> None:
    text = _read(DOC_PATH)
    for item in NON_EQUAL_CANON_ITEMS:
        assert item in text


def test_phase_586_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_586_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_586_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_586_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_586_backfill_commit_touches_expected_paths_only_and_no_adr_cdl_or_ilc_core() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_586_BACKFILL_SUBJECT_TOKEN,
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
