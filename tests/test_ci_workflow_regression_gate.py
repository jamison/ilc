from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/test.yml")


def test_ci_workflow_runs_track1_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_track1_closure_guardrails.sh" in workflow


def test_ci_workflow_runs_domain_exception_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_domain_exception_migration_guardrails.sh" in workflow


def test_ci_workflow_runs_runtime_logging_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_runtime_logging_guardrails.sh" in workflow


def test_ci_workflow_runs_full_pytest_suite() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "python -m pytest -q" in workflow


def test_ci_workflow_runs_replay_proof_release_gate() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_cluster_a_replay_proof_release_gate.sh" in workflow


def test_ci_workflow_test_job_depends_on_release_gate_job() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "replay-proof-release-gate:" in workflow
    assert "needs: replay-proof-release-gate" in workflow
