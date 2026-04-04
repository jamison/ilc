from __future__ import annotations

import subprocess
from pathlib import Path

DOC_PATH = Path('docs/specs/ilc_public_identity_activation_and_namespace_boundary_lock_587_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_587_public_identity_activation_and_namespace_boundary_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_587_g8_public_identity_activation_namespace_boundary_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_587_SUBJECT_TOKEN = 'phase 587 public identity activation boundary lock'
PHASE_587_BACKFILL_SUBJECT_TOKEN = 'phase 587 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(DOC_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Public identity boundary target',
    '## 2. Dependency and inherited canon',
    '## 3. Public identity activation boundary',
    '## 4. Public namespace authority boundary',
    '## 5. Lineage, signer-root, and admission binding',
    '## 6. Forbidden interpretations and exclusions',
    '## 7. Explicit deferrals to later phases',
)
REQUIRED_TOKENS = (
    'public_agent_id_remains_key_derived',
    'public_identity_activation_requires_settled_admission_or_stake_binding_receipt',
    'public_write_path_requires_activation_receipt',
    'unbound_key_is_not_canonical_public_participant',
    'public_namespace_authority_is_first_class_receipt_surface',
    'namespace_authority_must_bind_to_admitted_identity_lineage',
    'canonical_root_key_lineage_not_transaction_hash_identity',
    'cdl_040_admission_scope_not_claim_acceptance',
    'display_aliases_are_derivative_not_authoritative',
    'local_private_identity_remains_permitted_outside_public_legitimacy',
    'namespace_authority_must_not_float_free_of_activation_lineage',
    'namespace_authority_must_remain_compatible_with_settlement_linked_legitimacy',
    'cdl_042_ratification_anchor_prelock_reference_only',
)
DEPENDENCY_ITEMS = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md`',
    '`docs/specs/ilc_public_receipt_representation_cluster_lock_586_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/adr/ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`',
    '`docs/specs/ilc_cdl_040_admission_control_and_identity_envelope_ratification_evidence_393_v0.1.md`',
    '`docs/specs/ilc_cdl_042_agent_identity_namespace_ratification_evidence_407_v0.1.md`',
    '`docs/specs/ilc_cdl_042_agent_identity_namespace_prelock_hardening_403_v0.1.md`',
    '`docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md`',
)
ACTIVATION_RULES = (
    'Canonical public identity remains derived from canonical key material',
    'A canonical public participant requires a settled admission or stake binding',
    'Public write-path authority requires an activation receipt',
    'A local key or local agent_id may exist without public activation, but it is',
)
NAMESPACE_RULES = (
    'Public namespace authority is a first-class receipt surface',
    'A namespace authority receipt must bind handles, usernames, or public labels to',
    'Namespace authority must not float free of the activation receipt lineage.',
    'Namespace authority must preserve the reference slot needed for the later',
    'Display aliases, local labels, and operator-friendly naming layers are',
)
LINEAGE_RULES = (
    'Canonical public agent identity continuity follows the CDL-001 signer-lineage',
    'Operational signer rotation does not create a new public agent identity.',
    'CDL-040 admission control and identity-envelope scope remains distinct from',
)
FORBIDDEN_RULES = (
    '- deriving canonical public identity from transaction hashes',
    '- treating operator labels or display aliases as canonical public authority',
    '- treating local/private agent existence as equivalent to canonical public',
    '- treating namespace authority as a free-floating alias system',
    '- reopening the protocol-vs-harness boundary through identity UX work',
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


def test_section_two_carries_mandatory_dependency_bundle() -> None:
    text = _read(DOC_PATH)
    for item in DEPENDENCY_ITEMS:
        assert item in text


def test_section_three_contains_public_identity_activation_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for item in ACTIVATION_RULES:
        assert item in text


def test_section_four_contains_first_class_namespace_authority_boundary_rules() -> None:
    text = _read(DOC_PATH)
    for item in NAMESPACE_RULES:
        assert item in text


def test_section_five_contains_lineage_signer_root_and_admission_binding_rules() -> None:
    text = _read(DOC_PATH)
    for item in LINEAGE_RULES:
        assert item in text


def test_section_six_contains_all_forbidden_interpretation_exclusions() -> None:
    text = _read(DOC_PATH)
    for item in FORBIDDEN_RULES:
        assert item in text


def test_phase_587_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_587_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_587_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_587_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_587_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_587_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_587_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_587_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
