from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

EVIDENCE_PATH = Path('docs/specs/ilc_cdl_060_gossip_centrality_extension_ratification_evidence_541_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_540_TEST_PATH = Path('tests/test_phase_540_cdl_060_prelock_hardening.py')
PHASE_536_DOC_PATH = Path('docs/specs/ilc_cdl_060_gossip_centrality_extension_scoping_536_v0.1.md')
PHASE_538_DOC_PATH = Path('docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md')
TEST_PATH = Path('tests/test_phase_541_cdl_060_ratification_evidence.py')
PHASE_536_SUBJECT_TOKEN = 'phase 536 cdl-060 gossip extension scoping'
PHASE_538_SUBJECT_TOKEN = 'phase 538 sim-centrality-02 gossip propagation'
PHASE_541_SUBJECT_TOKEN = 'phase 541 cdl-060 gossip centrality extension ratification'
PHASE_536_REQUIRED_PATHS = {
    str(PHASE_536_DOC_PATH),
    'tests/test_phase_536_cdl_060_gossip_extension_scoping.py',
}
PHASE_538_REQUIRED_PATHS = {
    str(PHASE_538_DOC_PATH),
    'tests/test_phase_538_sim_centrality_02_gossip_propagation.py',
}
EXACT_REQUIRED_MAIN_PATHS = {
    str(EVIDENCE_PATH),
    str(DECISION_LOG_PATH),
    str(PHASE_540_TEST_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Lane identity and ratification summary',
    '## 2. Constitutional necessity case',
    '## 3. Simulation evidence chain',
    '## 4. Selected option confirmation',
    '## 5. Governance token inventory',
    '## 6. Section-5 ratification readiness evidence checklist satisfaction',
    '## 7. Rejected scope expansions',
    '## 8. Forward obligations',
)
REQUIRED_TOKENS = (
    'cdl_060_governs_centrality_delta_gossip',
    'cdl_039_privacy_preserved',
    'single_hop_scope_locked',
    'cdl_036_related_clause',
    'sim_centrality_02_evidence_anchored',
)


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(
    subject_token: str,
    *,
    required_paths: set[str] | None = None,
    must_touch: str | None = None,
    present_error: str,
    missing_error: str,
) -> str:
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
        if subject_token not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths is not None and changed != required_paths:
            continue
        if must_touch is not None and must_touch not in changed:
            continue
        return commit_ref
    if matching:
        raise AssertionError(present_error)
    raise AssertionError(missing_error)


def _resolve_phase_536_commit_ref() -> str:
    return _resolve_commit_ref(
        PHASE_536_SUBJECT_TOKEN,
        required_paths=PHASE_536_REQUIRED_PATHS,
        must_touch=str(PHASE_536_DOC_PATH),
        present_error='phase_536_commit_subject_present_but_no_qualifying_scoping_commit',
        missing_error='phase_536_commit_not_present_in_local_history',
    )


def _resolve_phase_538_commit_ref() -> str:
    return _resolve_commit_ref(
        PHASE_538_SUBJECT_TOKEN,
        required_paths=PHASE_538_REQUIRED_PATHS,
        must_touch=str(PHASE_538_DOC_PATH),
        present_error='phase_538_commit_subject_present_but_no_qualifying_sim_commit',
        missing_error='phase_538_commit_not_present_in_local_history',
    )


def _resolve_phase_541_commit_ref() -> str:
    return _resolve_commit_ref(
        PHASE_541_SUBJECT_TOKEN,
        required_paths=EXACT_REQUIRED_MAIN_PATHS,
        must_touch=str(DECISION_LOG_PATH),
        present_error='phase_541_commit_subject_present_but_no_qualifying_ratification_commit',
        missing_error='phase_541_commit_not_present_in_local_history',
    )


def test_evidence_artifact_contains_required_headings() -> None:
    text = _read(EVIDENCE_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_evidence_artifact_contains_required_governance_tokens_and_upstream_chain() -> None:
    text = _read(EVIDENCE_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    phase_536_text = _commit_text(str(PHASE_536_DOC_PATH), _resolve_phase_536_commit_ref())
    phase_538_text = _commit_text(str(PHASE_538_DOC_PATH), _resolve_phase_538_commit_ref())
    assert 'cdl_060_scoping_complete' in phase_536_text
    assert 'sim_centrality_02_sufficient' in phase_538_text


def test_phase_540_test_historicalization_patch_is_active() -> None:
    text = _read(PHASE_540_TEST_PATH)
    assert '# The Phase-540 CDL-060 open-state check is a historical prelock reference.' in text


def test_live_decision_log_shows_cdl_060_ratified_and_preserves_other_rows() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert rows['CDL-060']['ratified_phase'] == '541'
    assert rows['CDL-060']['ratified_date'] == '2026-03-30'
    assert 'CDL-053' not in rows


def test_evidence_artifact_section_6_heading_is_exact() -> None:
    text = _read(EVIDENCE_PATH)
    assert '## 6. Section-5 ratification readiness evidence checklist satisfaction' in text


def test_phase_541_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_541_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_cdl_log_at_commit_shows_cdl_060_ratified_and_preserved_priors() -> None:
    commit_ref = _resolve_phase_541_commit_ref()
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert rows['CDL-060']['ratified_phase'] == '541'
    assert rows['CDL-060']['ratified_date'] == '2026-03-30'
    assert 'CDL-053' not in rows
