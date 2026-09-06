"""Phase 1573n public mirror Option C preparation verification."""

from __future__ import annotations

import json
import re
from pathlib import Path


STATUS = Path("docs/phases/STATUS.md").read_text(encoding="utf-8")
MANIFEST = Path("docs/specs/ilc_public_mirror_manifest_1573n_v0.1.json")
SCRIPT = Path("tools/scripts/generate_public_mirror.sh")
CHECKLIST = Path("docs/specs/ilc_phase_1448a_prepublication_review_checklist_v0.1.md")
MANIFEST_MD = Path("docs/specs/ilc_public_mirror_manifest_1573n_v0.1.md")


def test_status_tokens_present() -> None:
    assert "public_mirror_pipeline_rehearsed_phase_1573n" in STATUS
    assert "public_mirror_option_c_supersedes_option_a_phase_1573n" in STATUS
    assert "public_mirror_denylist_scan_pass_phase_1573n" in STATUS
    assert "public_mirror_exclude_scan_pass_phase_1573n" in STATUS
    assert "public_mirror_no_push_phase_1573n" in STATUS
    assert "public_path_remains_blocked_phase_1573n" in STATUS


def test_manifest_json_exists_and_has_required_fields() -> None:
    assert MANIFEST.exists(), "manifest JSON must exist"
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for field in (
        "pipeline_version",
        "source_private_commit",
        "filtered_public_head_sha",
        "canonical_hash",
        "commit_count_before",
        "commit_count_after",
        "commit_count_min_required",
        "excluded_path_count",
        "denylist_scan_result",
        "public_rc_exclude_scan_result",
        "author_rewrite_result",
        "no_push",
    ):
        assert field in data, f"manifest missing field: {field}"
    assert data["denylist_scan_result"] == "pass"
    assert data["public_rc_exclude_scan_result"] == "pass"
    assert data["no_push"] is True
    assert data["commit_count_after"] >= data["commit_count_min_required"]
    assert data["commit_count_after"] > 2000
    assert "ilcops@proton.me" in data["author_rewrite_result"]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", data["canonical_hash"])


def test_pipeline_script_exists_and_has_no_push_command() -> None:
    assert SCRIPT.exists(), "pipeline script must exist"
    content = SCRIPT.read_text(encoding="utf-8")
    assert not re.search(r"(^|[;&|\s])git\s+push(\s|$)", content)
    assert "ilcops@proton.me" in content
    assert "PUBLIC_RC_EXCLUDE detection" in content
    assert "jacobus05" in content  # denylist term, not public identity
    assert "rev-list" in content
    assert "cat-file" in content


def test_pipeline_script_honors_rust_public_rc_exclude_headers() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert "(?:#|//)" in content
    assert "<!--\\s*PUBLIC_RC_EXCLUDE" in content
    assert '".rs"' in content
    assert "shamir_split" in content
    assert "shamir_recover" in content
    assert "shamir_verify" in content
    assert "private Shamir binary declarations" in content


def test_phase_1448a_a4_updated_to_option_c() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "Option C" in text, "Phase 1448a A4 must be amended to Option C"
    assert "1573n" in text, "Phase 1448a A4 must reference Phase 1573n"
    assert "full rewritten history" in text


def test_maintenance_policy_present() -> None:
    assert MANIFEST_MD.exists()
    text = MANIFEST_MD.read_text(encoding="utf-8")
    assert "public_mirror_is_derived_artifact_not_source_of_truth" in text
    assert "no_manual_public_repo_patches_policy" in text
    assert "public_push_requires_clean_denylist_and_exclude_scan" in text
    assert "graph_derived_public_mirror_export_routed_to_window_1576_plus" in text
