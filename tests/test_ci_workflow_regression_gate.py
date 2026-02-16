from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/test.yml")


def test_ci_workflow_runs_track1_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_track1_closure_guardrails.sh" in workflow


def test_ci_workflow_runs_non_replay_domain_exception_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_non_replay_domain_exception_migration_guardrails.sh" in workflow


def test_ci_workflow_runs_domain_exception_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_domain_exception_migration_guardrails.sh" in workflow


def test_ci_workflow_guardrail_preflight_ordering_contract() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    idx_non_replay = workflow.index("bash tools/check_non_replay_domain_exception_migration_guardrails.sh")
    idx_domain = workflow.index("bash tools/check_domain_exception_migration_guardrails.sh")
    idx_track1 = workflow.index("bash tools/check_track1_closure_guardrails.sh")
    assert idx_non_replay < idx_domain < idx_track1


def test_ci_workflow_runs_runtime_logging_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_runtime_logging_guardrails.sh" in workflow


def test_ci_workflow_runs_main_track_return_preflight_gate() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_main_track_return_preflight_193_199.sh" in workflow


def test_ci_workflow_runs_main_track_return_preflight_203_209_gate() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_main_track_return_preflight_203_209.sh" in workflow


def test_ci_workflow_main_track_preflight_runs_before_full_pytest() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    idx_preflight_193_199 = workflow.index("bash tools/check_main_track_return_preflight_193_199.sh")
    idx_preflight_203_209 = workflow.index("bash tools/check_main_track_return_preflight_203_209.sh")
    idx_full_pytest = workflow.index("python -m pytest -q")
    assert idx_preflight_193_199 < idx_preflight_203_209 < idx_full_pytest


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
