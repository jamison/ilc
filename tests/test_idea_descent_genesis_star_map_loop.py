"""Idea-descent loop over the Genesis star-map candidate graph.

This test targets the intended ILC use case: evaluating a Genesis node/star-map
candidate against the v0.2/v0.3 manifest lineage and producing actionable
refutations before any signing, graph mutation, or public RC step.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from ilc_core.sidecars.idea_descent_rehearsal import (
    VERDICT_ACCEPTED,
    VERDICT_REJECTED,
    build_descent_step,
    build_descent_trace,
    build_evaluation_result,
    build_refutation_report,
    validate_descent_trace,
)

_ROOT = Path(__file__).resolve().parent.parent
_CURRENT_V03 = _ROOT / "out" / "genesis_core_star_map_v0.3_candidate.json"
_OBJECTIVE = (
    _ROOT / "docs" / "specs" / "ilc_idea_descent_genesis_star_map_objective_v0.1.md"
)
_EVALUATOR_PATH = _ROOT / "tools" / "evaluators" / "genesis_star_map_evaluator.py"

_spec = importlib.util.spec_from_file_location(
    "genesis_star_map_evaluator",
    _EVALUATOR_PATH,
)
_evaluator = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_evaluator)


def _evaluate(candidate_path: str) -> dict:
    return _evaluator.run_evaluation(
        candidate_path,
        _OBJECTIVE.read_text(encoding="utf-8"),
    )


def _write_bad_candidate(path: Path) -> None:
    data = json.loads(_CURRENT_V03.read_text(encoding="utf-8"))
    removed = {"genesis_agent:01", "truth_primitive:commit.epoch"}
    data["nodes"] = [
        node for node in data["nodes"] if node.get("candidate_id") not in removed
    ]
    data["metadata"]["transition_basis"] = [
        "truth_primitive:assert.truth",
    ]
    data["metadata"].pop("expansion_phase", None)
    data["nodes"][0]["confidence"] = "not-a-number"
    data["edges"].append(
        {
            "edge_id": "edge:test_missing_endpoint",
            "edge_type": "LINKS",
            "source": "artifact:genesis_agent1_pubkey_record_838a",
            "target": "missing:node",
            "decomposition_recipe": {},
        }
    )
    path.write_text(
        json.dumps(data, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _make_step(step_index: int, candidate_path: str, result: dict) -> dict:
    replay_command = _evaluator.REPLAY_COMMAND_TEMPLATE.format(candidate=candidate_path)
    eval_result = build_evaluation_result(
        evaluator_type=_evaluator.EVALUATOR_TYPE,
        replay_command=replay_command,
        passed=result["passed"],
        failure_count=result["failure_count"],
        summary=result["summary"],
    )
    refutations = [build_refutation_report(**r) for r in result["refutation_reports"]]
    verdict = VERDICT_ACCEPTED if result["passed"] else VERDICT_REJECTED
    revision_plan = None
    if refutations:
        revision_plan = "Fix: " + "; ".join(
            r["correction_direction"] for r in result["refutation_reports"]
        )
    return build_descent_step(
        step_index=step_index,
        objective=_OBJECTIVE.read_text(encoding="utf-8"),
        candidate_description=Path(candidate_path).name,
        candidate_artifact_path=candidate_path,
        evaluators_run=[_evaluator.EVALUATOR_TYPE],
        evaluation_results=[eval_result],
        refutation_reports=refutations,
        revision_plan=revision_plan,
        verdict=verdict,
    )


def test_current_v03_genesis_star_map_candidate_passes() -> None:
    result = _evaluate("out/genesis_core_star_map_v0.3_candidate.json")
    assert result["passed"] is True
    assert result["failure_count"] == 0
    assert result["refutation_reports"] == []
    assert "54 nodes" in result["summary"]


def test_mutated_candidate_fails_with_actionable_refutations(tmp_path: Path) -> None:
    bad_candidate = tmp_path / "bad_genesis_star_map_candidate.json"
    _write_bad_candidate(bad_candidate)

    result = _evaluate(str(bad_candidate))

    assert result["passed"] is False
    assert result["failure_count"] >= 6
    invariants = {r["failed_invariant"] for r in result["refutation_reports"]}
    assert "transition_basis_mismatch" in invariants
    assert "missing_v03_expansion_phase" in invariants
    assert "required_node_missing:genesis_agent:01" in invariants
    assert "required_node_missing:truth_primitive:commit.epoch" in invariants
    assert "node_confidence_invalid:truth_primitive:assert.truth" in invariants
    assert "edge_target_missing:edge:test_missing_endpoint" in invariants
    assert "edge_missing_decomposition_recipe:edge:test_missing_endpoint" in invariants
    for report in result["refutation_reports"]:
        assert report["correction_direction"]
        assert report["replay_command"]


def test_two_step_trace_records_genesis_candidate_improvement(tmp_path: Path) -> None:
    bad_candidate = tmp_path / "bad_genesis_star_map_candidate.json"
    _write_bad_candidate(bad_candidate)

    rejected = _evaluate(str(bad_candidate))
    accepted = _evaluate("out/genesis_core_star_map_v0.3_candidate.json")
    step0 = _make_step(0, str(bad_candidate), rejected)
    step1 = _make_step(1, "out/genesis_core_star_map_v0.3_candidate.json", accepted)

    trace = build_descent_trace(
        trace_id="genesis_star_map_candidate_descent",
        objective=_OBJECTIVE.read_text(encoding="utf-8"),
        steps=[step0, step1],
    )
    validated = validate_descent_trace(trace)

    assert step0["verdict"] == VERDICT_REJECTED
    assert step1["verdict"] == VERDICT_ACCEPTED
    assert rejected["failure_count"] > accepted["failure_count"]
    assert accepted["failure_count"] == 0
    assert validated["final_verdict"] == VERDICT_ACCEPTED
    assert validated["accepted_step_index"] == 1


def test_runner_appends_genesis_trace_atomically(tmp_path: Path) -> None:
    bad_candidate = tmp_path / "bad_genesis_star_map_candidate.json"
    trace_path = tmp_path / "trace.json"
    _write_bad_candidate(bad_candidate)

    first = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "tools" / "idea_descent_runner.py"),
            "--objective",
            str(_OBJECTIVE),
            "--candidate",
            str(bad_candidate),
            "--evaluator",
            str(_EVALUATOR_PATH),
            "--trace-out",
            str(trace_path),
        ],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert first.returncode == 1, first.stdout + first.stderr

    second = subprocess.run(
        [
            sys.executable,
            str(_ROOT / "tools" / "idea_descent_runner.py"),
            "--objective",
            str(_OBJECTIVE),
            "--candidate",
            "out/genesis_core_star_map_v0.3_candidate.json",
            "--evaluator",
            str(_EVALUATOR_PATH),
            "--trace-out",
            str(trace_path),
        ],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert second.returncode == 0, second.stdout + second.stderr

    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    validated = validate_descent_trace(trace)
    assert validated["total_steps"] == 2
    assert validated["final_verdict"] == VERDICT_ACCEPTED
    assert validated["steps"][0]["verdict"] == VERDICT_REJECTED
    assert validated["steps"][1]["verdict"] == VERDICT_ACCEPTED
