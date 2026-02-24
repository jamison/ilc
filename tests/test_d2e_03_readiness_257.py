from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip


READINESS_PATH = Path("docs/specs/ilc_d2e_03_readiness_assessment_257_v0.1.md")
VECTORS_PATH = Path("docs/specs/ilc_d2_schema_test_vectors_spec_257_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phase_commit_hash() -> str:
    return resolve_phase_commit_ref_or_skip("phase_257")


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


def test_no_ilc_core_files_touched_in_phase_257_commit() -> None:
    commit_hash = _phase_commit_hash()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", commit_hash],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    touched_files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    ilc_core_touches = [path for path in touched_files if path.startswith("ilc_core/")]
    assert ilc_core_touches == []
