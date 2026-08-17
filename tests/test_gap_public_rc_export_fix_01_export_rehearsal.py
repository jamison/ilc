from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc import source_allowlist_export_rehearsal as rehearsal
from ilc_core.rc.source_allowlist_export_rehearsal import (
    build_source_allowlist_export_rehearsal,
    canonical_source_allowlist_export_rehearsal_json,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json"
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _paths(records: list[dict[str, object]]) -> set[str]:
    return {str(record["path"]) for record in records}


@pytest.fixture(scope="module")
def current_manifest() -> dict[str, object]:
    return build_source_allowlist_export_rehearsal(repo_root=ROOT)


def test_gap_public_rc_export_fix_01_current_repo_rehearsal_passes(
    current_manifest: dict[str, object],
) -> None:
    manifest = current_manifest

    assert manifest["result"] == "pass"
    assert manifest["counts"]["blocked_ambiguities"] == 0
    assert manifest["counts"]["dependency_hits"] == 0
    assert manifest["counts"]["marker_hits"] == 0
    assert manifest["dependency_scan"]["result"] == "pass"
    assert manifest["marker_scan"]["result"] == "pass"


def test_gap_public_rc_export_fix_01_checked_in_report_matches_current_repo(
    current_manifest: dict[str, object],
) -> None:
    report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))

    assert report == current_manifest
    assert canonical_source_allowlist_export_rehearsal_json(report) == json.dumps(
        report,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def test_gap_public_rc_export_fix_01_included_and_excluded_sets_are_disjoint(
    current_manifest: dict[str, object],
) -> None:
    assert _paths(current_manifest["included_files"]).isdisjoint(
        _paths(current_manifest["excluded_files"])
    )


def test_gap_public_rc_export_fix_01_html_public_rc_exclude_header_excluded(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "docs/blocked.md",
        "<!-- PUBLIC_RC_EXCLUDE: private launch note -->\n\n# Internal\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("docs",),
        excluded_roots=(),
    )

    assert manifest["result"] == "pass"
    assert manifest["marker_scan"]["hit_count"] == 0
    assert manifest["included_files"] == []
    assert manifest["excluded_files"] == [
        {
            "blocked": False,
            "exclusion_rule": "public_rc_exclude_marker_default_excluded",
            "marker_status": "hit",
            "path": "docs/blocked.md",
            "review_required_before_public_export": True,
        }
    ]


def test_gap_public_rc_export_fix_01_indented_slash_header_excluded(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "ilc_core/private.rs",
        "  // PUBLIC_RC_EXCLUDE private generated adapter\npub const VALUE: u8 = 1;\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("ilc_core",),
        excluded_roots=(),
    )

    assert manifest["result"] == "pass"
    assert manifest["included_files"] == []
    assert manifest["excluded_files"][0]["path"] == "ilc_core/private.rs"
    assert manifest["excluded_files"][0]["marker_status"] == "hit"


def test_gap_public_rc_export_fix_01_dependency_scan_rejects_oversized_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write(tmp_path / "README.md", "x" * 32)
    monkeypatch.setattr(rehearsal, "MAX_DEPENDENCY_SCAN_FILE_BYTES", 8)

    with pytest.raises(ValueError, match="phase_1319_dependency_scan_file_too_large"):
        build_source_allowlist_export_rehearsal(
            repo_root=tmp_path,
            include_roots=("README.md",),
            excluded_roots=(),
            reviewed_legacy_paths=("README.md",),
        )


def test_gap_public_rc_export_fix_01_broad_docs_default_excluded_but_reviewed_force_included(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "docs/internal_plan.md", "private public rc launch notes\n")
    _write(tmp_path / "docs/GETTING_STARTED.md", "# Getting Started\npublic guide\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("docs",),
    )

    assert manifest["result"] == "pass"
    assert _paths(manifest["included_files"]) == {"docs/GETTING_STARTED.md"}
    assert manifest["blocked_ambiguities"] == []
    assert manifest["legacy_untagged_review"]["review_required_blocked_files"] == []
    assert manifest["legacy_untagged_review"]["default_excluded_files"] == [
        {
            "path": "docs/internal_plan.md",
            "reason": "docs_tree_default_excluded_pending_public_manifest_review",
        }
    ]


def test_gap_public_rc_export_fix_01_broad_tools_default_excluded_but_reviewed_force_included(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "tools/internal_ops.py", "VALUE = 'private'\n")
    _write(tmp_path / "tools/demo_walkthrough.py", "VALUE = 'public demo'\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("tools",),
    )

    assert manifest["result"] == "pass"
    assert _paths(manifest["included_files"]) == {"tools/demo_walkthrough.py"}
    assert manifest["blocked_ambiguities"] == []
    assert manifest["legacy_untagged_review"]["default_excluded_files"] == [
        {
            "path": "tools/internal_ops.py",
            "reason": "tools_tree_default_excluded_pending_public_manifest_review",
        }
    ]


def test_gap_public_rc_export_fix_01_private_sidecar_repos_default_excluded(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "ilc-ccss-sidecar/README.md", "# CCSS private local\n")
    _write(tmp_path / "ilc-timecapsule-sidecar/README.md", "# TimeCapsule pre-CDL\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("ilc-ccss-sidecar", "ilc-timecapsule-sidecar"),
    )

    assert manifest["result"] == "pass"
    assert manifest["included_files"] == []
    assert _paths(manifest["excluded_files"]) == {
        "ilc-ccss-sidecar/README.md",
        "ilc-timecapsule-sidecar/README.md",
    }


def test_gap_public_rc_export_fix_01_wallet_sidecar_readme_is_reviewed_public_doc(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "ilc-wallet-sidecar/README.md",
        "# Wallet Sidecar\nread-only public wallet visibility\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("ilc-wallet-sidecar",),
    )

    assert manifest["result"] == "pass"
    assert _paths(manifest["included_files"]) == {"ilc-wallet-sidecar/README.md"}
    assert manifest["legacy_untagged_review"]["included_reviewed_files"] == [
        {
            "path": "ilc-wallet-sidecar/README.md",
            "reason": "explicitly_reviewed_metadata_phase_1319",
        }
    ]


def test_gap_public_rc_export_fix_01_internal_stripped_helper_metadata_is_excluded(
    current_manifest: dict[str, object],
) -> None:
    assert "tools/cdl048_production_conversion_rehearsal_1575r.py" not in _paths(
        current_manifest["included_files"]
    )
    assert current_manifest["dependency_scan"]["stripped_helper_hit_count"] == 0
