from __future__ import annotations

import subprocess
from pathlib import Path

from ilc_core.epistemic.node_submission_runtime import (
    CDL_052_DEPENDENCY,
    EPISTEMIC_RUNTIME_PART1_VERSION,
    EpistemicSubmissionError,
    route_epistemic_mode,
)

HANDOFF_PATH = Path('docs/specs/ilc_cdl_052_epistemic_node_submission_runtime_handoff_477_v0.1.md')
TEST_PATH = Path('tests/test_phase_477_cdl_052_epistemic_node_submission_runtime.py')
PHASE_477_SUBJECT_TOKEN = 'phase 477 cdl-052 epistemic node submission runtime part 1'
EXACT_REQUIRED_MAIN_PATHS = {
    'ilc_core/epistemic/__init__.py',
    'ilc_core/epistemic/node_submission_runtime.py',
    str(HANDOFF_PATH),
    str(TEST_PATH),
}


def _valid_submission() -> dict:
    return {
        'cid': 'cid-alpha',
        'agent_id': 'agent-alpha',
        'authored_envelope': {},
        'protocol_envelope': {},
        'transport_envelope': {},
    }


def _valid_refutation_criterion() -> dict:
    return {
        'claim': 'claim-alpha',
        'evidence_type': 'empirical',
        'scope_boundary': 'scope-alpha',
        'claim_form': 'singular',
        'has_falsifiable_test': True,
        'is_inadmissible_counterexample': False,
        'agreement_score': 0.95,
    }


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ['git', 'show', '--name-only', '--pretty=', commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_477_commit_ref() -> str:
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
        if PHASE_477_SUBJECT_TOKEN not in subject.lower():
            continue
        matching.append(commit_hash)
    for commit_ref in matching:
        if _changed_paths_for_commit(commit_ref) == EXACT_REQUIRED_MAIN_PATHS:
            return commit_ref
    if matching:
        raise AssertionError('phase_477_commit_subject_present_but_no_qualifying_runtime_commit')
    raise AssertionError('phase_477_commit_not_present_in_local_history')


def test_version_and_dependency_tokens_exist() -> None:
    assert EPISTEMIC_RUNTIME_PART1_VERSION == 'epistemic_node_submission_runtime_477.v0.1'
    assert CDL_052_DEPENDENCY == 'cdl_052_ratified_466.v0.1'


def test_mode_1_routing_returns_mode_1_without_refutation_criterion() -> None:
    assert route_epistemic_mode(_valid_submission()) == 'mode_1'


def test_mode_2_routing_returns_mode_2_for_valid_refutation_criterion() -> None:
    submission = _valid_submission()
    submission['authored_envelope']['refutation_criterion'] = _valid_refutation_criterion()
    assert route_epistemic_mode(submission) == 'mode_2'


def test_normative_refutation_collision_raises() -> None:
    submission = _valid_submission()
    submission['normative'] = True
    submission['authored_envelope']['refutation_criterion'] = _valid_refutation_criterion()
    try:
        route_epistemic_mode(submission)
    except EpistemicSubmissionError as exc:
        assert exc.token == 'NORMATIVE_REFUTATION_COLLISION'
    else:
        raise AssertionError('expected_collision_error')


def test_authored_envelope_violation_raises_for_top_level_refutation_criterion() -> None:
    submission = _valid_submission()
    submission['refutation_criterion'] = _valid_refutation_criterion()
    try:
        route_epistemic_mode(submission)
    except EpistemicSubmissionError as exc:
        assert exc.token == 'AUTHORED_ENVELOPE_VIOLATION'
    else:
        raise AssertionError('expected_authored_envelope_violation')


def test_mode_3_boundary_detection_returns_explicit_route_tag() -> None:
    submission = _valid_submission()
    submission['anomaly_signal'] = True
    assert route_epistemic_mode(submission) == 'mode_3_boundary_detected'


def test_phase_477_main_commit_touches_expected_paths_and_no_forbidden_paths() -> None:
    commit_ref = _resolve_phase_477_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == EXACT_REQUIRED_MAIN_PATHS


def test_phase_477_main_commit_does_not_touch_decision_log_or_non_epistemic_ilc_core() -> None:
    commit_ref = _resolve_phase_477_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert 'docs/specs/ilc_constitutional_decision_log_v0.1.md' not in changed_paths
    assert all(path.startswith('ilc_core/epistemic/') or not path.startswith('ilc_core/') for path in changed_paths)
