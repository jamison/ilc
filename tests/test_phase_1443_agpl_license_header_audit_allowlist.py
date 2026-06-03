# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

from ilc_core.rc.license_header_audit_phase_1443 import (
    AGPL_3_ONLY_LICENSE_HEADER_PRESENT_TOKEN,
    AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN,
    PHASE_1443_LICENSE_AUDIT_TOKENS,
    PUBLIC_RC_NOT_PUBLISHED_PHASE_1443_TOKEN,
    PUBLIC_SOURCE_ALLOWLIST_EXECUTION_COMPLETE_PHASE_1443_TOKEN,
)
from ilc_core.rc.source_allowlist_export_execution_gate import (
    build_source_allowlist_export_execution_gate,
)


ROOT = Path(__file__).resolve().parents[1]
SPDX_HEADER = "SPDX-License-Identifier: AGPL-3.0-only"


def _allowlisted_python_paths() -> list[Path]:
    manifest = build_source_allowlist_export_execution_gate(materialize=False)
    return sorted(
        Path(record["path"])
        for record in manifest["candidate_scan"]["included_files"]
        if str(record["path"]).endswith(".py")
    )


def test_phase_1443_every_allowlisted_python_file_has_agpl_spdx_header() -> None:
    allowlisted = _allowlisted_python_paths()

    assert allowlisted
    missing = []
    for rel_path in allowlisted:
        repo_text = (ROOT / rel_path).read_text(encoding="utf-8")
        if SPDX_HEADER not in "\n".join(repo_text.splitlines()[:6]):
            missing.append(rel_path.as_posix())

    assert missing == []


def test_phase_1443_no_allowlisted_file_has_unresolved_include_requires() -> None:
    unresolved = []
    for rel_path in _allowlisted_python_paths():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        if "PUBLIC_RC_INCLUDE_REQUIRES:" in text:
            unresolved.append(rel_path.as_posix())

    assert unresolved == []


def test_phase_1443_allowlist_execution_gate_remains_non_publishing() -> None:
    manifest = build_source_allowlist_export_execution_gate()

    assert manifest["source_publication_authorized"] is False
    assert manifest["public_rc_remains_blocked"] is True
    verdict = manifest["source_allowlist_export_execution_gate_verdict"]
    assert verdict in {
        "source_allowlist_export_execution_gate_verdict=pass",
        "source_allowlist_export_execution_gate_verdict=block",
    }
    if verdict == "source_allowlist_export_execution_gate_verdict=block":
        assert manifest["dirty_worktree_policy"]["dirty_included_files"]


def test_phase_1443_completion_tokens_are_recorded() -> None:
    assert AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
    assert (
        PUBLIC_SOURCE_ALLOWLIST_EXECUTION_COMPLETE_PHASE_1443_TOKEN
        in PHASE_1443_LICENSE_AUDIT_TOKENS
    )
    assert AGPL_3_ONLY_LICENSE_HEADER_PRESENT_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
    assert PUBLIC_RC_NOT_PUBLISHED_PHASE_1443_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
