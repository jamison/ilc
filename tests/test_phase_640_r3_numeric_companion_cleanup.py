from __future__ import annotations

import hashlib
import json
import subprocess
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.ledger.canon_export_validate import validate_canon_export_v0_1
from ilc_core.ledger.canon_export_bundle_validate import validate_canon_export_bundle
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
from ilc_core.ledger.canon_export_format import export_canon_format_v0_1

SPEC_PATH = Path("docs/specs/ilc_r3_numeric_companion_cleanup_640_v0.1.md")
TEST_PATH = Path("tests/test_phase_640_r3_numeric_companion_cleanup.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_640_g8_r3_numeric_companion_cleanup_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_640_SUBJECT_TOKEN = "phase 640 r3 numeric companion cleanup"
PHASE_640_BACKFILL_SUBJECT_TOKEN = "phase 640 walkthrough and status backfill"
REQUIRED_HEADINGS = (
    "## 1. Ratified dependency and cleanup target",
    "## 2. Companion files migrated",
    "## 3. Canon-export companion contract changes",
    "## 4. Validation and scalar contract cleanup",
    "## 5. Verification and residual defers",
)
REQUIRED_TOKENS = (
    "r3_numeric_companion_cleanup_640_locked",
    "cdl_064_dependency_consumed_in_phase_640",
    "canon_export_companion_float_scalar_contract_removed",
    "canon_export_companion_validators_aligned_to_exact_numeric",
    "canon_export_companion_non_finite_rejection_aligned",
    "r3_numeric_companion_cleanup_verification_defined",
    "window_637_641_moves_to_residual_numeric_hardening_gate",
)
REQUIRED_TARGETS = (
    "- `ilc_core/ledger/canon_export_validate.py`",
    "- `ilc_core/ledger/canon_export_bundle_validate.py`",
    "- `ilc_core/ledger/canon_export_bundle.py`",
    "- `ilc_core/ledger/canon_export_format.py`",
    "- `ilc_core/ledger/canon_bundle_audit_artifact.py`",
)
COMPANION_FILES = (
    Path("ilc_core/ledger/canon_export_validate.py"),
    Path("ilc_core/ledger/canon_export_bundle_validate.py"),
    Path("ilc_core/ledger/canon_export_bundle.py"),
    Path("ilc_core/ledger/canon_export_format.py"),
    Path("ilc_core/ledger/canon_bundle_audit_artifact.py"),
)
ALLOWED_MAIN_PREFIXES = (
    "ilc_core/ledger/canon_export_validate.py",
    "ilc_core/ledger/canon_export_bundle_validate.py",
    "ilc_core/ledger/canon_export_bundle.py",
    "ilc_core/ledger/canon_export_format.py",
    "ilc_core/ledger/canon_bundle_audit_artifact.py",
    "tests/test_canon_export_validate.py",
    "tests/test_canon_export_bundle_validate.py",
    "tests/test_canon_export_bundle.py",
    "tests/test_canon_export_format.py",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def test_cleanup_doc_exists_and_contains_required_headings() -> None:
    text = _read(SPEC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_cleanup_doc_contains_all_required_tokens() -> None:
    text = _read(SPEC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_section_two_names_all_five_target_companion_files() -> None:
    text = _read(SPEC_PATH)
    for item in REQUIRED_TARGETS:
        assert item in text


def test_section_three_records_companion_scalar_contract_cleanup() -> None:
    text = _read(SPEC_PATH)
    assert "JsonScalar" in text
    assert "no longer declare `float`" in text
    assert "canonical decimal strings" in text


def test_section_four_records_validation_cleanup() -> None:
    text = _read(SPEC_PATH)
    assert "`NaN`, `Infinity`, and `-Infinity`" in text
    assert "full canon-export schema validation when" in text


def test_target_companion_files_remove_float_scalar_contract_and_reject_non_finite_numeric_inputs(tmp_path) -> None:
    for path in COMPANION_FILES:
        text = _read(path)
        assert "TypeAlias = str | int | float | bool | None" not in text

    validate_result = validate_canon_export_v0_1(
        {
            "canon_export_format": "v0.1",
            "canon_hash": "h",
            "exported_at": "2026-02-05T00:00:00Z",
            "meta": {
                "canon_export_version": "v",
                "epoch_count": 0,
                "snapshot_count": 1,
                "balance_count": 1,
            },
            "epochs": [],
            "snapshots": [{"epoch_id": "e1", "balances": {"alice": "Infinity"}}],
        }
    )
    assert validate_result["ok"] is False
    assert any("exact numeric value" in error for error in validate_result["errors"])

    export = {
        "canon_export_format": "v0.1",
        "canon_hash": "h1",
        "exported_at": "2026-02-05T00:00:00Z",
        "meta": {
            "canon_export_version": "v",
            "epoch_count": 0,
            "snapshot_count": 1,
            "balance_count": 1,
        },
        "epochs": [],
        "snapshots": [{"epoch_id": "e1", "balances": {"alice": "1.25"}}],
    }
    validation = {"ok": True, "score": "1"}
    bundle_dir = tmp_path / "bundle"
    write_canon_export_bundle(export, validation, bundle_dir)

    export_content = b'{"canon_export_format":"v0.1","canon_hash":"h1","exported_at":"2026-02-05T00:00:00Z","meta":{"canon_export_version":"v","epoch_count":0,"snapshot_count":1,"balance_count":1},"epochs":[],"snapshots":[{"epoch_id":"e1","balances":{"alice":NaN}}]}'
    (bundle_dir / "export.json").write_bytes(export_content + b"\n")
    manifest_path = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["export_hash"] = hashlib.sha256(export_content).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    bundle_result = validate_canon_export_bundle(bundle_dir)
    assert bundle_result["ok"] is False
    assert "non_finite_json_numeric_literal:NaN" in bundle_result["errors"]

    export_payload = export_canon_format_v0_1(
        {
            "canon_hash": "hash_abc",
            "canon_export_version": "v0.0.1",
            "epochs": [{"epoch_id": "e1"}],
            "snapshots": [{"epoch_id": "e1", "balances": {"alice": Decimal("1.25")}}],
            "balances": {"alice": Decimal("1.25")},
        },
        exported_at="2026-02-05T00:00:00+00:00",
    )
    assert export_payload["snapshots"][0]["balances"]["alice"] == "1.25"

    with pytest.raises(ValueError, match="invalid_numeric_scalar_in_canon_export"):
        export_canon_format_v0_1(
            {
                "canon_hash": "hash_abc",
                "canon_export_version": "v0.0.1",
                "epochs": [{"epoch_id": "e1"}],
                "snapshots": [{"epoch_id": "e1", "balances": {"alice": 1.25}}],
                "balances": {"alice": Decimal("1.25")},
            },
            exported_at="2026-02-05T00:00:00+00:00",
        )


def test_phase_640_main_commit_touches_spec_test_and_bounded_companion_paths_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_640_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_640_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(SPEC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    unexpected = {
        path
        for path in changed_paths
        if path not in {str(SPEC_PATH), str(TEST_PATH)}
        and path not in ALLOWED_MAIN_PREFIXES
    }
    assert not unexpected


def test_phase_640_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_640_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_640_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}
