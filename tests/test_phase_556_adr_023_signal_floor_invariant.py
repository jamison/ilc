from __future__ import annotations

import subprocess
from pathlib import Path

ADR_PATH = Path('docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
TEST_PATH = Path('tests/test_phase_556_adr_023_signal_floor_invariant.py')
PHASE_556_SUBJECT_PREFIX = 'phase 556'
EXACT_REQUIRED_MAIN_PATHS = {
    str(ADR_PATH),
    str(TEST_PATH),
}
SECTION_HEADING = '## Signal Floor Cross-Module Invariant (Phase 556 addition)'


def _read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def _section_text(text: str) -> str:
    start = text.index(SECTION_HEADING)
    return text[start:]


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_556_commit_ref() -> str:
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
        normalized = subject.lower()
        if PHASE_556_SUBJECT_PREFIX not in normalized:
            continue
        if 'adr' not in normalized and 'signal floor' not in normalized:
            continue
        matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    raise AssertionError('phase_556_commit_not_present_in_local_history')


def test_adr_0023_contains_the_exact_new_section_heading() -> None:
    assert SECTION_HEADING in _read(ADR_PATH)


def test_adr_0023_new_section_contains_the_invariant_statement() -> None:
    section = _section_text(_read(ADR_PATH))
    assert '`recommended_decay_floor >= recommended_u_floor`' in section


def test_adr_0023_new_section_contains_governance_tokens() -> None:
    section = _section_text(_read(ADR_PATH))
    assert 'signal_floor_governance_adm_only' in section
    assert 'signal_floor_cross_module_invariant_documented_phase_556' in section


def test_adr_0023_new_section_contains_current_floor_values_and_source_references() -> None:
    section = _section_text(_read(ADR_PATH))
    assert 'recommended_decay_floor = 0.05' in section
    assert 'recommended_u_floor = 0.05' in section
    assert 'ilc_core/economics/passive_ecu_attribution_runtime.py' in section
    assert 'ilc_core/network/d2d/centrality_delta_gossip_runtime.py' in section


def test_phase_556_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_556_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_556_commit_leaves_cdl_log_and_ilc_core_untouched() -> None:
    commit_ref = _resolve_phase_556_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
