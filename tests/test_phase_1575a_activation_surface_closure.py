# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1575a public-RC exclusion closure tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ilc_core.ledger import conversion_candidate_runtime


REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_MODULES = {
    "ilc_core/economics/productive_ecu_expansion_bounty_runtime.py",
    "ilc_core/epoch/canonical_economic_event.py",
    "ilc_core/epoch/ejected_stake_distribution_production_path.py",
    "ilc_core/epoch/epoch_emission_production_path.py",
    "ilc_core/epoch/treasury_validator_reward_production_path.py",
    "ilc_core/ledger/conversion_candidate_runtime.py",
    "ilc_core/validator/validator_admission_ejection_production_path.py",
}


def test_phase_1575a_exclusion_headers_are_near_file_top() -> None:
    for rel_path in EXCLUDED_MODULES:
        header = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()[:8]
        assert any("PUBLIC_RC_EXCLUDE: economic_activation_pending_1575b" in line for line in header)


def test_phase_1575a_import_closure_scanner_has_no_top_level_violations() -> None:
    result = subprocess.run(
        [sys.executable, "tools/check_public_rc_exclude_imports.py", "ilc_core/", "--json"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    manifest = json.loads(result.stdout)
    assert manifest["ok"] is True
    assert manifest["top_level_violation_count"] == 0


def test_phase_1575a_source_export_manifest_excludes_activation_surfaces(tmp_path: Path) -> None:
    export_manifest = tmp_path / "source_export.json"
    subprocess.run(
        [
            sys.executable,
            "ilc_core/rc/source_allowlist_export_rehearsal.py",
            "--json-out",
            str(export_manifest),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    manifest = json.loads(export_manifest.read_text(encoding="utf-8"))
    included = {record["path"] for record in manifest["included_files"]}
    assert not (EXCLUDED_MODULES & included)


def test_phase_1575a_build_candidates_helper_stays_private() -> None:
    assert hasattr(conversion_candidate_runtime, "_build_candidates")
    assert "_build_candidates" not in conversion_candidate_runtime.__all__
