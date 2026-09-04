from __future__ import annotations

import json
from pathlib import Path

import pytest

from ilc_core.rc.source_allowlist_export_rehearsal import (
    LEGACY_UNTAGGED_REVIEW_RESULTS_TOKEN,
    PHASE_1320_NEXT_TOKEN,
    PUBLIC_RC_EXCLUDE_MARKER_SCAN_ZERO_TOKEN,
    PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1319_TOKEN,
    SOURCE_ALLOWLIST_EXPORT_REHEARSAL_VERSION,
    SOURCE_EXPORT_REHEARSAL_NO_PUBLICATION_TOKEN,
    STRIPPED_HELPER_IMPORT_SCAN_ZERO_TOKEN,
    build_source_allowlist_export_rehearsal,
    canonical_source_allowlist_export_rehearsal_json,
    manifest_hash,
    phase_1319_required_tokens,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = (
    ROOT / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.json"
)
REPORT_MD = (
    ROOT / "docs/specs/ilc_deterministic_source_allowlist_export_rehearsal_1319_v0.1.md"
)
WALKTHROUGH = (
    ROOT / "docs/phases/phase_1319_deterministic_source_allowlist_export_rehearsal_walkthrough.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _load_report() -> dict:
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def test_phase_1319_current_repo_rehearsal_passes_and_is_canonical() -> None:
    manifest = build_source_allowlist_export_rehearsal(repo_root=ROOT)
    encoded_once = canonical_source_allowlist_export_rehearsal_json(manifest)
    encoded_twice = canonical_source_allowlist_export_rehearsal_json(
        build_source_allowlist_export_rehearsal(repo_root=ROOT)
    )

    assert encoded_once == encoded_twice
    assert encoded_once == json.dumps(
        json.loads(encoded_once),
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    assert manifest["schema_version"] == SOURCE_ALLOWLIST_EXPORT_REHEARSAL_VERSION
    assert manifest["required_tokens"] == phase_1319_required_tokens()
    assert manifest["result"] == "pass"
    assert manifest["marker_scan"]["hit_count"] == 0
    assert manifest["dependency_scan"]["stripped_helper_hit_count"] == 0
    assert manifest["legacy_untagged_review"]["ambiguity_count"] == 0
    assert manifest["public_rc_remains_blocked"] is True
    assert "no_public_source_export" in manifest["non_claims"]
    assert "no_package_publication" in manifest["non_claims"]
    assert manifest["rerun"]["expected_manifest_hash"] == manifest["rerun"][
        "expected_manifest_hash"
    ]
    assert manifest_hash(manifest) != manifest["rerun"]["expected_manifest_hash"]


def test_phase_1319_checked_in_report_matches_current_rehearsal() -> None:
    report = _load_report()
    current = build_source_allowlist_export_rehearsal(repo_root=ROOT)

    assert report == current
    assert REPORT_MD.read_text(encoding="utf-8").startswith(
        "# ILC Deterministic Source Allowlist Export Rehearsal 1319 v0.1"
    )


def test_phase_1319_force_included_public_rc_exclude_marker_fails_closed(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "src/marked.py", "# PUBLIC_RC_EXCLUDE: synthetic\nVALUE = 1\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
        force_include_paths=("src/marked.py",),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["marker_scan"]["hit_count"] == 1
    assert manifest["marker_scan"]["hits"] == [
        {"marker": "PUBLIC_RC_EXCLUDE", "path": "src/marked.py"}
    ]


def test_phase_1319_public_rc_exclude_prose_reference_is_not_marker(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "src/prose.md",
        "# Public release notes\n\n"
        "This document explains that `PUBLIC_RC_EXCLUDE` is a deny marker.\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
        reviewed_legacy_paths=("src/prose.md",),
    )

    assert manifest["result"] == "pass"
    assert manifest["marker_scan"]["hit_count"] == 0
    assert [record["path"] for record in manifest["included_files"]] == ["src/prose.md"]


def test_phase_1319_required_included_paths_pass_when_marker_free(tmp_path: Path) -> None:
    _write(tmp_path / "src/runtime.py", "VALUE = 1\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
        required_included_paths=("src/runtime.py",),
    )

    assert manifest["result"] == "pass"
    assert manifest["required_included_paths"] == {
        "checked_count": 1,
        "missing": [],
        "present": [{"marker_status": "absent", "path": "src/runtime.py"}],
        "result": "pass",
    }


def test_phase_1319_optional_sidecar_include_roots_may_be_absent(tmp_path: Path) -> None:
    _write(tmp_path / "src/runtime.py", "VALUE = 1\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src", "ilc-ccss-sidecar"),
        excluded_roots=(),
    )

    assert manifest["result"] == "pass"
    assert {
        "allowlist_reason": "explicit_allowlist_candidate_phase_1319",
        "exists": False,
        "root": "ilc-ccss-sidecar",
    } in manifest["candidate_roots"]
    assert [record["path"] for record in manifest["included_files"]] == ["src/runtime.py"]


def test_phase_1319_non_optional_missing_include_root_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase_1319_include_root_missing"):
        build_source_allowlist_export_rehearsal(
            repo_root=tmp_path,
            include_roots=("missing-runtime-root",),
            excluded_roots=(),
        )


def test_phase_1319_required_included_paths_fail_closed_when_excluded(tmp_path: Path) -> None:
    _write(tmp_path / "src/runtime.py", "# PUBLIC_RC_EXCLUDE: synthetic\nVALUE = 1\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
        required_included_paths=("src/runtime.py",),
    )

    assert manifest["result"] == "pass"
    assert manifest["required_included_paths"] == {
        "checked_count": 1,
        "missing": [
            {
                "path": "src/runtime.py",
                "reason": "public_rc_exclude_marker_default_excluded",
            }
        ],
        "present": [],
        "result": "fail_closed",
    }


def test_phase_1319_required_included_paths_reject_traversal(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="phase_1319_required_included_path_traversal_rejected"):
        build_source_allowlist_export_rehearsal(
            repo_root=tmp_path,
            include_roots=("src",),
            excluded_roots=(),
            required_included_paths=("../secret.py",),
        )


def test_phase_1319_public_rc_exclude_late_comment_is_not_header_marker(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "src/script.sh",
        "#!/usr/bin/env bash\n"
        "# Usage: script\n"
        "# Line 3\n"
        "# Line 4\n"
        "# Line 5\n"
        "# Line 6\n"
        "# Line 7\n"
        "# Line 8\n"
        "# PUBLIC_RC_EXCLUDE: prose_reference_not_header\n"
        "echo ok\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
    )

    assert manifest["result"] == "pass"
    assert manifest["marker_scan"]["hit_count"] == 0
    assert [record["path"] for record in manifest["included_files"]] == ["src/script.sh"]


def test_phase_1319_force_included_generated_cache_file_fails_closed(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "src/__pycache__/cache.pyc", "generated\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
        force_include_paths=("src/__pycache__/cache.pyc",),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["blocked_ambiguities"] == [
        {
            "path": "src/__pycache__/cache.pyc",
            "reason": "generated_or_local_cache_path_default_excluded",
        }
    ]


def test_phase_1319_direct_stripped_helper_import_fails_closed(tmp_path: Path) -> None:
    _write(
        tmp_path / "src/main.py",
        "from ilc_core.ledger.claimability_proof_binding_runtime import X\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["dependency_scan"]["stripped_helper_hit_count"] >= 1
    assert any(
        hit["edge_type"] == "python_ast_import"
        for hit in manifest["dependency_scan"]["stripped_helper_hits"]
    )


def test_phase_1319_transitive_stripped_helper_import_fails_closed(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "src/__init__.py", "")
    _write(tmp_path / "src/main.py", "import src.bridge\n")
    _write(
        tmp_path / "src/bridge.py",
        "import ilc_core.network.d2d.transport_principal_public_path_preflight\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
    )

    assert manifest["result"] == "fail_closed"
    assert any(
        hit["edge_type"] == "python_ast_transitive_import"
        for hit in manifest["dependency_scan"]["stripped_helper_hits"]
    )


def test_phase_1319_metadata_reference_to_stripped_helper_fails_closed(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "package/profile.toml",
        "helper = 'ilc_core/graph/sidecar_public_path_preflight.py'\n",
    )

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("package/profile.toml",),
        excluded_roots=(),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["dependency_scan"]["stripped_helper_hits"] == [
        {
            "edge_type": "text_dependency_reference",
            "source": "package/profile.toml",
            "target": "ilc_core/graph/sidecar_public_path_preflight.py",
        }
    ]


def test_phase_1319_path_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="include_root_traversal_rejected"):
        build_source_allowlist_export_rehearsal(
            repo_root=tmp_path,
            include_roots=("../escape",),
            excluded_roots=(),
        )


def test_phase_1319_symlink_escape_fails_closed(tmp_path: Path) -> None:
    external = tmp_path.parent / f"{tmp_path.name}_outside_secret.txt"
    external.write_text("secret\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/link.txt").symlink_to(external)

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src",),
        excluded_roots=(),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["excluded_files"] == [
        {
            "blocked": True,
            "exclusion_rule": "symlink_escape_rejected",
            "marker_status": "not_scanned_symlink_rejected",
            "path": "src/link.txt",
            "review_required_before_public_export": True,
        }
    ]


def test_phase_1319_default_excludes_private_phase_out_and_patent_material(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "docs/phases/phase.md", "private phase note\n")
    _write(tmp_path / "docs/antigravity_tasks/prompt.md", "prompt\n")
    _write(tmp_path / "docs/research/patent.md", "patent pending\n")
    _write(tmp_path / "out/cache.json", "{}\n")
    _write(tmp_path / "src/main.py", "VALUE = 1\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("src", "docs/phases", "docs/antigravity_tasks", "docs/research", "out"),
    )

    assert manifest["result"] == "pass"
    assert sorted(record["root"] for record in manifest["excluded_roots"]) == [
        "Z_Past_Chats",
        "docs/antigravity_tasks",
        "docs/phases",
        "docs/research",
        "ilc_consensus/target",
        "local_monitoring",
        "monitoring",
        "out",
        "tests",
    ]
    assert sorted(record["path"] for record in manifest["included_files"]) == ["src/main.py"]


def test_phase_1319_legacy_untagged_required_file_blocks(tmp_path: Path) -> None:
    _write(tmp_path / "public_notes/claim.md", "Internal patent launch claim draft\n")

    manifest = build_source_allowlist_export_rehearsal(
        repo_root=tmp_path,
        include_roots=("public_notes",),
        excluded_roots=(),
    )

    assert manifest["result"] == "fail_closed"
    assert manifest["legacy_untagged_review"]["review_required_blocked_files"] == [
        {
            "path": "public_notes/claim.md",
            "reason": "legacy_untagged_review_required_terms_detected",
        }
    ]


def test_phase_1319_status_planning_and_walkthrough_record_required_tokens() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPORT_MD, WALKTHROUGH, STATUS, PLANNING)
    )
    for token in (
        SOURCE_ALLOWLIST_EXPORT_REHEARSAL_VERSION,
        PUBLIC_RC_EXCLUDE_MARKER_SCAN_ZERO_TOKEN,
        STRIPPED_HELPER_IMPORT_SCAN_ZERO_TOKEN,
        LEGACY_UNTAGGED_REVIEW_RESULTS_TOKEN,
        SOURCE_EXPORT_REHEARSAL_NO_PUBLICATION_TOKEN,
        PHASE_1320_NEXT_TOKEN,
        PUBLIC_RC_REMAINS_BLOCKED_AFTER_PHASE_1319_TOKEN,
    ):
        assert token in text
