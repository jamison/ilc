from __future__ import annotations

import subprocess
from pathlib import Path

SEQ_LOCK_PATH = Path('docs/specs/ilc_phase_585_594_sequence_lock_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_585_window_585_594_sequence_lock.py')
WALKTHROUGH_PATH = Path('docs/phases/phase_585_g8_window_585_594_sequence_lock_walkthrough.md')
STATUS_PATH = Path('docs/phases/STATUS.md')
PHASE_585_SUBJECT_TOKEN = 'phase 585 window 585-594 sequence lock'
PHASE_585_BACKFILL_SUBJECT_TOKEN = 'phase 585 walkthrough and status backfill'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SEQ_LOCK_PATH),
    str(TEST_PATH),
}
EXACT_REQUIRED_BACKFILL_PATHS = {
    str(WALKTHROUGH_PATH),
    str(STATUS_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Window summary',
    '## 2. Hard pass condition',
    '## 3. Mandatory dependency bundle',
    '## 4. Pre-lock blockers',
    '## 5. Phase table',
    '## 6. Locked implementation decisions',
    '## 7. Protected boundaries and anti-pattern exclusions',
    '## 8. Sequence integrity rule',
)
REQUIRED_TOKENS = (
    'rc0_1_plus_public_release_window_585_594_primary_gate',
    'public_release_not_equivalent_to_testnet_closure',
    'receipt_representation_cluster_precedes_public_runtime_integration',
    'genesis_authority_and_sunset_dependency_mandatory',
    'genesis_not_informal_founder_discretion',
    'cdl_v6_extraordinary_authority_only',
    'canonical_public_legitimacy_must_flow_through_genesis_rooted_lineage',
    'canonical_vs_fork_genesis_consequence_explicit',
    'public_namespace_receipt_disposition_must_be_explicit',
    'supporting_context_not_equal_canon',
    'no_public_release_claim_without_receipt_boundary_closure',
    'no_quota_miner_or_onboarding_inside_public_release_constitutional_lane',
)
EXPECTED_PHASE_ROWS = (
    '| 585 | Window 585-594 sequence lock and dependency freeze | `ilc_phase_585_594_sequence_lock_v0.1.md` | No |',
    '| 586 | Receipt representation CDL cluster | receipt-format CDL cluster | YES |',
    '| 587 | Public identity activation and namespace authority boundary | public identity and namespace boundary lock | YES |',
    '| 588 | Public quorum eligibility and Genesis-lineage authority boundary | public quorum authority boundary lock | YES |',
    '| 589 | Settlement-linked public legitimacy and payout traceability | public settlement legitimacy lock | YES |',
    '| 590 | Genesis authority, sunset, and fork-legitimacy coherence lock | Genesis/sunset coherence lock | YES |',
    '| 591 | Public-runtime integration over the receipt boundary | public-runtime integration proof | YES |',
    '| 592 | Public release-claim and operator honesty package | public RC package | YES |',
    '| 593 | Coherence report and public-RC capsule update | report + capsule | No |',
    '| 594 | Window 585-594 closure gate and handoff | gate script + handoff | YES |',
)
REQUIRED_REFERENCES = (
    '`docs/specs/ilc_window_585_594_candidate_phase_grouping_v0.1.md`',
    '`docs/adr/ADR_0006_EVE_Canonical_Capsule_Integrity.md`',
    '`docs/adr/ADR_0026_Protocol_vs_Harness_Product_Boundary.md`',
    '`docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`',
    '`docs/research/ilc_cryptographic_economic_coupling_memo_v0.1.md`',
    '`docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`',
    '`docs/specs/ilc_phase_585_genesis_authority_and_sunset_dependency_note_v0.1.md`',
    '`docs/research/ilc_rc_phase_575_execution_packets_v0.1.md`',
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
REQUIRED_BLOCKERS = (
    'receipt representation CDL cluster required before execution lock',
    'Genesis authority and sunset dependency note required before execution lock',
    'canonical-vs-fork Genesis consequence must be explicit before any public',
    'public operator honesty boundary must be explicit before closure',
    'supporting context may inform the window but may not be treated as equal',
)
LOCKED_DECISION_RULES = (
    'public participation inseparability is the operative architectural target.',
    'Genesis-signed bootstrap artifacts remain the recursive self-anchor for',
    'ordinary governance and `CDL-V6` extraordinary intervention remain distinct.',
    'local/private ILC use remains permitted outside public legitimacy.',
    'non-equal-canon sources may be used only if labeled as supporting context or',
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


def test_sequence_lock_document_exists_and_contains_required_headings() -> None:
    text = _read(SEQ_LOCK_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sequence_lock_document_contains_required_tokens() -> None:
    text = _read(SEQ_LOCK_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_phase_table_contains_exactly_ten_rows_for_phases_585_594_in_order() -> None:
    text = _read(SEQ_LOCK_PATH)
    rows: list[str] = []
    in_phase_table = False
    for line in text.splitlines():
        if line == '| Phase | Description | Primary output | Sensitive? |':
            in_phase_table = True
            continue
        if not in_phase_table:
            continue
        if line in EXPECTED_PHASE_ROWS:
            rows.append(line)
            continue
        if rows:
            break
    assert tuple(rows) == EXPECTED_PHASE_ROWS


def test_dependency_bundle_contains_all_required_references() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_REFERENCES:
        assert item in text


def test_pre_lock_blockers_section_contains_all_required_blockers() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in REQUIRED_BLOCKERS:
        assert item in text


def test_locked_implementation_decisions_record_genesis_rooted_lineage_boundary() -> None:
    text = _read(SEQ_LOCK_PATH)
    for item in LOCKED_DECISION_RULES:
        assert item in text


def test_phase_585_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_585_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_585_main_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_585_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_MAIN_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_585_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_585_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_BACKFILL_PATHS


def test_phase_585_backfill_commit_touches_no_adr_cdl_path_and_no_ilc_core_path() -> None:
    commit_ref = _resolve_commit_ref(
        subject_token=PHASE_585_BACKFILL_SUBJECT_TOKEN,
        expected_paths=EXACT_REQUIRED_BACKFILL_PATHS,
    )
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('docs/adr/') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl_') for path in changed_paths)
    assert not any(path.startswith('docs/specs/ilc_cdl-') for path in changed_paths)
    assert not any('/ilc_cdl_' in path for path in changed_paths)
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
