from __future__ import annotations

import subprocess
from pathlib import Path

import ilc_core.epoch as epoch_pkg
from ilc_core.epoch import epoch_boundary_witness_runtime


ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
RUNTIME = ROOT / "ilc_core/epoch/epoch_boundary_witness_runtime.py"

CDL_COMMIT_SUBJECT = "phase 1364 blocking authority cdl ratification"
RUNTIME_COMMIT_SUBJECT = "phase 1364 flip blocking authority deferred false"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _decision_rows() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in _read(CDL_REGISTER).splitlines():
        if line.startswith("| CDL-"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 4 and cells[0].startswith("CDL-"):
                rows[cells[0]] = line
    return rows


def _commit_for_subject(subject: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, commit_subject = line.split("\t", 1)
        if commit_subject == subject:
            return commit_hash
    return None


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        cwd=ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_cdl_089_is_ratified_with_phase_1364_token() -> None:
    row = _decision_rows()["CDL-089"]
    register = _read(CDL_REGISTER)

    assert "| ratified |" in row
    assert "ratified_phase: 1364" in row
    assert "ratified_date: 2026-05-16" in row
    assert "blocking_authority_ratified_phase_1364.v0.1" in row
    assert "runtime_activation_required_separate_commit" in row
    assert "## Scoped Ratification Record (Phase 1364: CDL-089)" in register
    assert "This CDL record authorizes, but does not itself perform" in register


def test_epoch_boundary_witness_runtime_is_blocking_active() -> None:
    assert (
        epoch_boundary_witness_runtime.EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION
        == "epoch_boundary_witness_blocking_active_phase_1364.v0.1"
    )
    assert epoch_boundary_witness_runtime.BLOCKING_AUTHORITY_DEFERRED is False
    assert epoch_boundary_witness_runtime.is_blocking_authority_active() is True


def test_epoch_package_reexports_blocking_active_runtime_state() -> None:
    assert (
        epoch_pkg.EPOCH_BOUNDARY_WITNESS_RUNTIME_VERSION
        == "epoch_boundary_witness_blocking_active_phase_1364.v0.1"
    )
    assert epoch_pkg.BLOCKING_AUTHORITY_DEFERRED is False
    assert epoch_pkg.is_blocking_authority_active() is True


def test_witness_payload_remains_batch_scoped_after_activation() -> None:
    assert epoch_boundary_witness_runtime.record_epoch_boundary_witness("validator-1", 42, "cid-1") == {
        "status": "witnessed",
        "batch_cid": "cid-1",
        "provenance_tag": "validator-1@epoch_42",
    }


def test_phase_1364_cdl_and_runtime_commits_are_separate_when_present() -> None:
    cdl_commit = _commit_for_subject(CDL_COMMIT_SUBJECT)
    runtime_commit = _commit_for_subject(RUNTIME_COMMIT_SUBJECT)

    assert cdl_commit is not None
    assert _changed_paths_for_commit(cdl_commit) == {
        "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    }

    if runtime_commit is None:
        return

    runtime_paths = _changed_paths_for_commit(runtime_commit)
    assert "docs/specs/ilc_constitutional_decision_log_v0.1.md" not in runtime_paths
    assert "ilc_core/epoch/epoch_boundary_witness_runtime.py" in runtime_paths
