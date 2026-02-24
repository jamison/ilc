from __future__ import annotations

import subprocess
from pathlib import Path
import re

from ilc_core.testing.phase_commit_manifest import (
    load_phase_commit_manifest,
    resolve_phase_commit_ref_or_skip,
)


MANIFEST_PATH = Path("docs/specs/ilc_phase_commit_manifest_296_v0.1.json")

REQUIRED_PHASE_IDS = {
    "phase_257",
    "phase_258",
    "phase_267",
    "phase_268",
    "phase_271",
    "phase_272",
    "phase_273",
    "phase_274",
    "phase_274_fix1",
    "phase_275",
    "phase_276",
    "phase_277_pre1",
    "phase_277",
    "phase_278",
    "phase_283",
    "phase_288",
    "phase_291",
    "phase_294",
}

MIGRATED_TEST_FILES = [
    "tests/test_cdl_019_ratification_268.py",
    "tests/test_cdl_025_ratification_267.py",
    "tests/test_cdl_026_ratification_273.py",
    "tests/test_cdl_027_ratification_276.py",
    "tests/test_cdl_028_fee_burn_candidate_lock_274_fix1.py",
    "tests/test_cdl_028_ratification_274.py",
    "tests/test_cdl_029_ratification_272.py",
    "tests/test_cdl_030_price_clamp_candidate_lock_277_pre1.py",
    "tests/test_cdl_030_ratification_277.py",
    "tests/test_cdl_031_ratification_288.py",
    "tests/test_cdl_033_ratification_291.py",
    "tests/test_crypto_migration_initial_tranche_283.py",
    "tests/test_d2e_03_readiness_257.py",
    "tests/test_d2e_04_identity_subsystem_294.py",
    "tests/test_integration_coherence_258.py",
    "tests/test_integration_coherence_278.py",
    "tests/test_issuance_evidence_closure_b_271.py",
    "tests/test_issuance_evidence_closure_c_275.py",
]


def test_manifest_file_exists() -> None:
    assert MANIFEST_PATH.exists()


def test_manifest_schema_and_required_phases() -> None:
    payload = load_phase_commit_manifest()
    assert payload["version"] == "v0.1"
    assert payload.get("generated_date") == "2026-02-24"
    phases = payload["phases"]
    assert REQUIRED_PHASE_IDS.issubset(set(phases.keys()))


def test_manifest_recorded_commits_resolve_in_local_git_history() -> None:
    payload = load_phase_commit_manifest()
    phases = payload["phases"]

    for phase_id in REQUIRED_PHASE_IDS:
        entry = phases[phase_id]
        commit_ref = entry.get("commit")
        status = entry.get("status")
        if not commit_ref:
            assert status == "unrecorded_consolidated"
            continue

        result = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{commit_ref}^{{commit}}"],
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{phase_id}:{commit_ref} missing from local history"


def test_resolver_returns_commit_for_recorded_phase() -> None:
    commit_ref = resolve_phase_commit_ref_or_skip("phase_277")
    assert re.fullmatch(r"[0-9a-f]{7,40}", commit_ref) is not None


def test_migrated_tests_no_longer_use_commit_subject_grep() -> None:
    for path_str in MIGRATED_TEST_FILES:
        path = Path(path_str)
        text = path.read_text(encoding="utf-8")
        assert "COMMIT_SUBJECT" not in text, path_str
        assert "--format=%H%x09%s" not in text, path_str
        assert "phase_commit_subject_not_found" not in text, path_str
