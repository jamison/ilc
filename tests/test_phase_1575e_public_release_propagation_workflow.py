from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs/specs/ilc_public_release_propagation_workflow_1575e_v0.1.md"
TOOL_PATH = REPO_ROOT / "tools/public_release_prepare_update.py"
MIRROR_GENERATOR_PATH = REPO_ROOT / "tools/scripts/generate_public_mirror.sh"


@pytest.fixture(scope="module")
def release_receipt(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict[str, object], bytes]:
    receipt_path = tmp_path_factory.mktemp("phase_1575e") / "release_receipt.json"
    subprocess.run(
        [sys.executable, str(TOOL_PATH), "--json-out", str(receipt_path)],
        cwd=REPO_ROOT,
        check=True,
    )
    raw = receipt_path.read_bytes()
    return json.loads(raw), raw


def test_spec_exists_and_contains_all_required_sections() -> None:
    text = SPEC_PATH.read_text(encoding="utf-8")
    required_sections = [
        "## 1. Purpose and Post-1575c Boundary",
        "## 2. Three-Lane Model",
        "## 3. Private Development Lane",
        "## 4. Current Public Release Lane",
        "## 5. Future Graph-Native Homoiconic Release Lane",
        "## 6. Release Propagation Receipt Schema",
        "## 7. Graph Accounting Requirements",
        "## 8. No-Push / Push-Gate Separation",
        "## 9. Failure Modes and Named Blockers",
        "## 10. Migration Plan From Interim Mirror Lane to Homoiconic Exporter",
    ]
    for section in required_sections:
        assert section in text


def test_spec_names_all_three_release_lanes() -> None:
    text = SPEC_PATH.read_text(encoding="utf-8")
    assert "Private development lane" in text
    assert "Current public release lane" in text
    assert "Future graph-native homoiconic release lane" in text


def test_tool_receipt_includes_future_homoiconic_fields(
    release_receipt: tuple[dict[str, object], bytes],
) -> None:
    receipt, _raw = release_receipt
    forward_fields = receipt["homoiconic_forward_fields"]
    assert forward_fields == {
        "atlas_lmdb_root": None,
        "atlas_slice_manifest_id": None,
        "content_availability_layer_status": "post_rc_target",
        "graph_native_exporter_status": "not_activated",
        "package_profile_id": None,
    }


def test_receipt_json_serialization_is_deterministic(
    release_receipt: tuple[dict[str, object], bytes],
) -> None:
    receipt, raw = release_receipt
    expected = (
        json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")
    assert raw == expected


def test_tool_refuses_public_push_authorization() -> None:
    source = TOOL_PATH.read_text(encoding="utf-8")
    assert '"public_push_authorized": False' in source
    assert 'receipt.get("public_push_authorized") is not False' in source
    assert "public_push_authorized_must_be_false" in source


def test_tool_output_records_source_export_status(
    release_receipt: tuple[dict[str, object], bytes],
) -> None:
    receipt, _raw = release_receipt
    source_export = receipt["source_export"]
    assert source_export["result"] in {"pass", "fail"}
    assert isinstance(source_export["included_files"], int)
    assert isinstance(source_export["excluded_files"], int)
    assert isinstance(source_export["blocked_ambiguities"], int)
    assert isinstance(source_export["manifest_sha256"], str)
    assert len(source_export["manifest_sha256"]) == 64


def test_tool_output_records_private_worktree_status(
    release_receipt: tuple[dict[str, object], bytes],
) -> None:
    receipt, _raw = release_receipt
    assert receipt["source_private_branch"]
    assert isinstance(receipt["private_worktree_clean"], bool)
    assert receipt["changed_file_baseline_status"] in {
        "requires_explicit_baseline_commit",
        "baseline_commit_not_found",
        "computed_from_explicit_baseline_commit",
    }


def test_tool_has_no_push_or_visibility_mutation() -> None:
    source = TOOL_PATH.read_text(encoding="utf-8")
    assert "git push" not in source
    assert '"push"' not in source
    assert "gh repo edit" not in source
    assert "--visibility" not in source


def test_current_sanitized_mirror_generator_is_named() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    source = TOOL_PATH.read_text(encoding="utf-8")
    assert MIRROR_GENERATOR_PATH.exists()
    assert "tools/scripts/generate_public_mirror.sh" in spec
    assert "tools/scripts/generate_public_mirror.sh" in source


def test_future_graph_native_exporter_is_not_active(
    release_receipt: tuple[dict[str, object], bytes],
) -> None:
    receipt, _raw = release_receipt
    forward_fields = receipt["homoiconic_forward_fields"]
    assert forward_fields["graph_native_exporter_status"] == "not_activated"
    assert forward_fields["content_availability_layer_status"] == "post_rc_target"
    assert "active" not in {
        forward_fields["graph_native_exporter_status"],
        forward_fields["content_availability_layer_status"],
    }
