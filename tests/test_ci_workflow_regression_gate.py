from pathlib import Path


WORKFLOW_PATH = Path(".github/workflows/test.yml")


def test_ci_workflow_runs_track1_guardrail_preflight() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "bash tools/check_track1_closure_guardrails.sh" in workflow


def test_ci_workflow_runs_full_pytest_suite() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "python -m pytest -q" in workflow
