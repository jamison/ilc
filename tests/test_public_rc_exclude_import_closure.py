from __future__ import annotations

import subprocess
import sys

from tools.check_public_rc_exclude_imports import scan_import_closure


def test_public_rc_exclude_import_closure_has_no_top_level_violations() -> None:
    result = scan_import_closure("ilc_core")

    assert result["ok"] is True
    assert result["top_level_violation_count"] == 0
    assert result["token"] == "public_rc_exclude_import_closure_clean_phase_1573al"


def test_public_rc_exclude_import_closure_lazy_violations_are_named_allowances() -> None:
    result = scan_import_closure("ilc_core")

    lazy = {
        (
            row["importer"],
            row["imported_path"],
            row["severity"],
        )
        for row in result["violations"]
    }
    assert lazy == {
        (
            "ilc_core/cli/main.py",
            "ilc_core/cli/atlas_lmdb_cli.py",
            "lazy",
        ),
        (
            "ilc_core/cli/main.py",
            "ilc_core/distribution/materialization.py",
            "lazy",
        ),
        (
            "ilc_core/epistemic/jury_assignment_runtime.py",
            "ilc_core/epistemic/vrf_proof_verifier.py",
            "lazy",
        ),
    }


def test_public_rc_exclude_import_closure_cli_exits_zero_when_clean() -> None:
    completed = subprocess.run(
        [sys.executable, "tools/check_public_rc_exclude_imports.py", "ilc_core"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "top_level_violation_count=0" in completed.stdout
    assert "public_rc_exclude_import_closure_clean_phase_1573al" in completed.stdout
    assert completed.stderr == ""
