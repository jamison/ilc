from __future__ import annotations

import subprocess
from pathlib import Path

ARTIFACT_PATH = Path('docs/specs/ilc_genesis_validator_bootstrap_specification_479_v0.1.md')
TEST_PATH = Path('tests/test_phase_479_genesis_validator_bootstrap_specification.py')
PHASE_479_SUBJECT_TOKEN = 'phase 479 genesis validator bootstrap specification'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ARTIFACT_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Signing key format',
    '## 2. Enrollment record structure',
    '## 3. Epoch-zero state record format',
    '## 4. Key-loading ceremony protocol',
    '## 5. Admission-control pre-population bundle format',
    '## 6. Key material preparation checklist',
    '## 7. Out-of-scope items and Phase 480 pointer',
)
REQUIRED_TOKENS = (
    'validator_id is derived from the public key using the CDL-042 key-derivation method.',
    'Ed25519 is the required signing algorithm for genesis validator identity.',
    'The key-loading ceremony protocol defines the human-operator procedure for genesis validator enrollment.',
    'Private key management, hardware security module integration, and threshold signatures are out of scope for Phase 479.',
    'Validator network join and recovery flow is out of scope for this bootstrap specification.',
    'No ilc_core/ implementation occurs in Phase 479.',
    'No decision-log mutation occurs in Phase 479.',
    'Phase 480 is the next authorized phase.',
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


def _resolve_phase_479_commit_ref() -> str:
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
        if PHASE_479_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_479_commit_subject_present_but_no_qualifying_bootstrap_spec_commit')
    raise AssertionError('phase_479_commit_not_present_in_local_history')


def test_bootstrap_specification_artifact_exists_and_contains_required_headings() -> None:
    text = _read(ARTIFACT_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_bootstrap_specification_contains_required_tokens() -> None:
    text = _read(ARTIFACT_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_4_records_ceremony_tooling_placement_decision() -> None:
    text = _read(ARTIFACT_PATH)
    assert 'Human-facing ceremony tooling is planned for tools/' in text
    assert 'deterministic verification runtime lives under ilc_core/genesis/' in text


def test_section_6_key_material_checklist_contains_at_least_five_items() -> None:
    checklist_items = [
        line for line in _read(ARTIFACT_PATH).splitlines() if line.strip().startswith('- [ ]')
    ]
    assert len(checklist_items) >= 5


def test_phase_479_main_commit_touches_expected_paths_and_no_ilc_core_changes() -> None:
    commit_ref = _resolve_phase_479_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS
    assert not any(path.startswith('ilc_core/') for path in changed_paths)


def test_phase_479_main_commit_does_not_touch_decision_log() -> None:
    commit_ref = _resolve_phase_479_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
