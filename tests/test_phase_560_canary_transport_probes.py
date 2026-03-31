from __future__ import annotations

import subprocess
from pathlib import Path

CANARY_PATH = Path('tools/run_mutation_canary_phase_297.py')
TEST_PATH = Path('tests/test_phase_560_canary_transport_probes.py')
DECISION_LOG_PATH = Path('docs/specs/ilc_constitutional_decision_log_v0.1.md')
PHASE_560_SUBJECT_TOKEN = 'phase 560 gossip transport version canary probe'
EXACT_REQUIRED_MAIN_PATHS = {
    str(CANARY_PATH),
    str(TEST_PATH),
}
EXPECTED_PROBES = (
    'lineage_rotated_authority_guard',
    'compromise_containment_sequence_order_guard',
    'non_target_phase_stamp_poisoning_guard',
    'centrality_delta_gossip_version_guard',
    'centrality_delta_gossip_d2d_dependency_guard',
    'gossip_transport_cdl_039_forbidden_key_guard',
    'gossip_transport_version_guard',
)


def _dry_run_output() -> str:
    result = subprocess.run(
        ['python3', str(CANARY_PATH), '--dry-run'],
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


def _resolve_phase_560_commit_ref() -> str:
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
        lowered = subject.lower()
        if 'phase 560' not in lowered or 'canary' not in lowered:
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_560_commit_subject_present_but_no_qualifying_canary_commit')
    raise AssertionError('phase_560_commit_not_present_in_local_history')


def test_canary_dry_run_lists_exactly_seven_probes() -> None:
    lines = [line for line in _dry_run_output().splitlines() if line.startswith('[')]
    assert len(lines) == 7


def test_canary_dry_run_contains_gossip_transport_version_guard() -> None:
    assert 'gossip_transport_version_guard' in _dry_run_output()


def test_canary_dry_run_retains_probe_6_transport_forbidden_key_guard() -> None:
    assert 'gossip_transport_cdl_039_forbidden_key_guard' in _dry_run_output()


def test_canary_dry_run_contains_all_prior_probes() -> None:
    output = _dry_run_output()
    for probe in EXPECTED_PROBES[:-1]:
        assert probe in output


def test_phase_560_main_commit_touches_expected_paths_only() -> None:
    commit_ref = _resolve_phase_560_commit_ref()
    assert _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS


def test_phase_560_main_commit_does_not_touch_cdl_or_ilc_core() -> None:
    commit_ref = _resolve_phase_560_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith('ilc_core/') for path in changed_paths)
