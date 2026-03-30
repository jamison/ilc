from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SIM_DOC_PATH = Path('docs/specs/ilc_sim_centrality_02_gossip_propagation_calibration_538_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_538_sim_centrality_02_gossip_propagation.py')
PHASE_538_SUBJECT_TOKEN = 'phase 538 sim-centrality-02 gossip propagation'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SIM_DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Simulation purpose and scope',
    '## 2. CDL-039 privacy constraint baseline consumed',
    '## 3. Gossip propagation model',
    '## 4. Calibration results',
    '## 5. CDL-039 compliance verification',
    '## 6. Simulation sufficiency declaration',
)
REQUIRED_TOKENS = (
    'sim_centrality_02_sufficient',
    'cdl_039_privacy_preserved_in_gossip',
    'single_hop_propagation_scope',
    'cluster_membership_not_inferrable_from_delta_messages',
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


def _commit_text(path: str, commit_ref: str) -> str:
    result = subprocess.run(
        ['git', 'show', f'{commit_ref}:{path}'],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout


def _resolve_phase_538_commit_ref() -> str:
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
        if PHASE_538_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_538_commit_subject_present_but_no_qualifying_sim_commit')
    raise AssertionError('phase_538_commit_not_present_in_local_history')


def test_sim_document_contains_required_headings() -> None:
    text = _read(SIM_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sim_document_contains_required_governance_tokens() -> None:
    text = _read(SIM_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sim_document_contains_all_calibration_constants() -> None:
    text = _read(SIM_DOC_PATH)
    fanout_match = re.search(r'recommended_fanout:\s*(\d+)', text)
    convergence_match = re.search(r'recommended_convergence_epochs:\s*(\d+)', text)
    privacy_match = re.search(r'recommended_privacy_budget_fraction:\s*([0-9]+(?:\.[0-9]+)?)', text)
    assert fanout_match is not None
    assert convergence_match is not None
    assert privacy_match is not None
    assert int(fanout_match.group(1)) == 3
    assert int(convergence_match.group(1)) == 4
    assert float(privacy_match.group(1)) == 0.25


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    commit_ref = _resolve_phase_538_commit_ref()
    # The Phase-538 CDL-060 absent check is a historical prelock reference.
    rows = parse_decision_register_rows(_commit_text(str(DECISION_LOG_PATH), commit_ref))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-060' not in rows


def test_exact_required_main_paths_contain_no_ilc_core_path() -> None:
    assert not any(path.startswith('ilc_core/') for path in EXACT_REQUIRED_MAIN_PATHS)


def test_phase_538_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_538_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_538_main_commit_does_not_touch_cdl_log_or_any_ilc_core_path() -> None:
    commit_ref = _resolve_phase_538_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
