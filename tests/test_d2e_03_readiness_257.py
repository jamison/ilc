from __future__ import annotations

import subprocess
from pathlib import Path


READINESS_PATH = Path("docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md")
VECTORS_PATH = Path("docs/specs/ilc_d2_schema_test_vectors_spec_257_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_readiness_doc_exists() -> None:
    assert READINESS_PATH.exists()


def test_vector_spec_exists() -> None:
    assert VECTORS_PATH.exists()


def test_readiness_references_phase_253_cli_surface_lock() -> None:
    text = _read(READINESS_PATH)
    assert "ilc_cli_command_surface_lock_253_v0.1.md" in text


def test_readiness_references_phase_254_output_schemas() -> None:
    text = _read(READINESS_PATH)
    assert "ilc_cli_output_schemas_254_v0.1.md" in text


def test_readiness_references_phase_255_d2_schemas() -> None:
    text = _read(READINESS_PATH)
    assert "ilc_d2_minimal_schema_specification_255_v0.1.md" in text


def test_vectors_reference_phase_255_minimal_schema_spec() -> None:
    text = _read(VECTORS_PATH)
    assert "ilc_d2_minimal_schema_specification_255_v0.1.md" in text


def test_no_ilc_core_files_touched_in_current_worktree() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "ilc_core"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
