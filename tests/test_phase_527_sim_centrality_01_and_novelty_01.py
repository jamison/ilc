from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ilc_core.testing.ratification_mutation_scope_guardrail import parse_decision_register_rows

SIM_DOC_PATH = Path('docs/specs/ilc_sim_centrality_01_and_novelty_01_calibration_527_v0.1.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_527_sim_centrality_01_and_novelty_01.py')
PHASE_527_SUBJECT_TOKEN = 'phase 527 sim-centrality-01 and novelty-01'
EXACT_REQUIRED_MAIN_PATHS = {
    str(SIM_DOC_PATH),
    str(TEST_PATH),
}
REQUIRED_HEADINGS = (
    '## 1. Simulation purpose and scope',
    '## 2. SIM-AESTHETIC-01 baseline constants consumed',
    '## 3. SIM-CENTRALITY-01: incremental centrality convergence',
    '## 4. SIM-NOVELTY-01: novelty bonus calibration',
    '## 5. Multi-hop deferral boundary',
    '## 6. Simulation sufficiency declarations',
)
REQUIRED_TOKENS = (
    'sim_centrality_01_sufficient',
    'sim_novelty_01_sufficient',
    'incremental_centrality_convergence',
    'recommended_u_floor',
    'recommended_alpha',
    'recommended_beta',
    'recommended_gamma',
    'multi_hop_centrality_deferred',
)
NUMERIC_KEYS = ('recommended_u_floor', 'recommended_alpha', 'recommended_beta', 'recommended_gamma')


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


def _resolve_phase_527_commit_ref() -> str:
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
        if PHASE_527_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_527_commit_subject_present_but_no_qualifying_sim_commit')
    raise AssertionError('phase_527_commit_not_present_in_local_history')


def test_sim_document_contains_required_headings() -> None:
    text = _read(SIM_DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_sim_document_contains_required_governance_tokens() -> None:
    text = _read(SIM_DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_sim_document_contains_all_recommended_constants_with_numeric_values() -> None:
    text = _read(SIM_DOC_PATH)
    for key in NUMERIC_KEYS:
        assert re.search(rf'{key}:\s*[0-9]+(?:\.[0-9]+)?', text)


def test_live_decision_log_preserves_required_statuses_and_absences() -> None:
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert rows['CDL-055']['status'] == 'ratified'
    assert rows['CDL-056']['status'] == 'ratified'
    assert rows['CDL-057']['status'] == 'ratified'
    assert rows['CDL-058']['status'] == 'ratified'
    assert 'CDL-053' not in rows
    assert 'CDL-059' not in rows


def test_head_commit_touches_no_ilc_core_runtime_files() -> None:
    changed_paths = {
        path.strip()
        for path in subprocess.run(
            ['git', 'diff', 'HEAD', '--name-only', '--', 'ilc_core/'],
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        if path.strip()
    }
    assert changed_paths == set()


def test_phase_527_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_527_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_527_main_commit_does_not_touch_cdl_log_and_cdl_059_remains_absent() -> None:
    commit_ref = _resolve_phase_527_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    rows = parse_decision_register_rows(_read(DECISION_LOG_PATH))
    assert 'CDL-059' not in rows
