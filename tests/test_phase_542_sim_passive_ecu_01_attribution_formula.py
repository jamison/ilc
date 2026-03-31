from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SIM_DOC_PATH = Path('docs/specs/ilc_sim_passive_ecu_01_attribution_formula_calibration_542_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_542_sim_passive_ecu_01_attribution_formula.py')
PHASE_542_SUBJECT_TOKEN = 'phase 542 sim-passive-ecu-01 passive ecu attribution formula calibration'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SIM_DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Simulation purpose and scope',
    '## 2. Upstream constants consumed',
    '## 3. Attribution formula model',
    '## 4. Calibration results',
    '## 5. Boundary conditions and pathological cases',
    '## 6. Simulation sufficiency declaration',
)
REQUIRED_TOKENS = (
    'sim_passive_ecu_01_sufficient',
    'passive_attribution_formula_calibrated',
    'single_hop_attribution_scope',
    'window_545_runtime_gate',
)
REQUIRED_CONSTANTS = (
    'recommended_passive_attribution_rate',
    'recommended_decay_floor',
    'recommended_attribution_cap',
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


def _resolve_phase_542_commit_ref() -> str:
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
        if PHASE_542_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_542_commit_subject_present_but_no_qualifying_sim_commit')
    raise AssertionError('phase_542_commit_not_present_in_local_history')


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
    passive_rate_match = re.search(r'recommended_passive_attribution_rate:\s*([0-9]+(?:\.[0-9]+)?)', text)
    decay_floor_match = re.search(r'recommended_decay_floor:\s*([0-9]+(?:\.[0-9]+)?)', text)
    attribution_cap_match = re.search(r'recommended_attribution_cap:\s*([0-9]+(?:\.[0-9]+)?)', text)
    assert passive_rate_match is not None
    assert decay_floor_match is not None
    assert attribution_cap_match is not None
    assert float(passive_rate_match.group(1)) == 0.20
    assert float(decay_floor_match.group(1)) == 0.05
    assert float(attribution_cap_match.group(1)) == 0.15


def test_sim_document_consumes_phase_527_upstream_constants() -> None:
    text = _read(SIM_DOC_PATH)
    assert 'recommended_u_floor = 0.05' in text
    assert 'recommended_gamma = 0.15' in text
    assert 'recommended_decay_floor >= recommended_u_floor' in text
    assert 'direct originator reward baseline before passive sharing' in text
    assert 'passive_ecu = min(base_reward * passive_attribution_rate * centrality_score * m_i, base_reward * attribution_cap)' in text


def test_live_cdl_inventory_preserves_cdl_060_and_no_new_rows() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-036']['status'] == 'ratified'
    assert rows['CDL-039']['status'] == 'ratified'
    assert rows['CDL-052']['status'] == 'ratified'
    assert rows['CDL-059']['status'] == 'ratified'
    assert rows['CDL-060']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    # The Phase-542 no-new-CDL-above-060 check will be historicalized when CDL-061 opens.
    def _is_numbered_cdl_above_060(key: str) -> bool:
        match = re.fullmatch(r'CDL-(\d+)', key)
        return bool(match) and int(match.group(1)) >= 61

    assert not any(_is_numbered_cdl_above_060(key) for key in rows)


def test_phase_542_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_542_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_542_main_commit_does_not_touch_cdl_or_ilc_core() -> None:
    commit_ref = _resolve_phase_542_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
