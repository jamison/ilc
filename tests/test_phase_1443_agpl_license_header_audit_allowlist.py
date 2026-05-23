# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from pathlib import Path

from ilc_core.rc.license_header_audit_phase_1443 import (
    AGPL_3_OR_LATER_LICENSE_HEADER_PRESENT_TOKEN,
    AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN,
    PHASE_1443_LICENSE_AUDIT_TOKENS,
    PUBLIC_RC_NOT_PUBLISHED_PHASE_1443_TOKEN,
    PUBLIC_SOURCE_ALLOWLIST_EXECUTION_COMPLETE_PHASE_1443_TOKEN,
)
from ilc_core.rc.source_allowlist_export_execution_gate import (
    build_source_allowlist_export_execution_gate,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TREE = ROOT / "out/public_rc/source_allowlist_export_phase_1333/tree"
SPDX_HEADER = "SPDX-License-Identifier: AGPL-3.0-or-later"


def _allowlisted_python_paths() -> list[Path]:
    return sorted(path.relative_to(PUBLIC_TREE) for path in PUBLIC_TREE.rglob("*.py"))


def test_phase_1443_every_allowlisted_python_file_has_agpl_spdx_header() -> None:
    allowlisted = _allowlisted_python_paths()

    assert len(allowlisted) == 281
    missing = []
    for rel_path in allowlisted:
        repo_text = (ROOT / rel_path).read_text(encoding="utf-8")
        tree_text = (PUBLIC_TREE / rel_path).read_text(encoding="utf-8")
        if SPDX_HEADER not in "\n".join(repo_text.splitlines()[:6]):
            missing.append(rel_path.as_posix())
        if SPDX_HEADER not in "\n".join(tree_text.splitlines()[:6]):
            missing.append(f"tree:{rel_path.as_posix()}")

    assert missing == []


def test_phase_1443_no_allowlisted_file_has_unresolved_include_requires() -> None:
    unresolved = []
    for rel_path in _allowlisted_python_paths():
        text = (ROOT / rel_path).read_text(encoding="utf-8")
        if "PUBLIC_RC_INCLUDE_REQUIRES:" in text:
            unresolved.append(rel_path.as_posix())

    assert unresolved == []


def test_phase_1443_allowlist_execution_gate_remains_non_publishing() -> None:
    manifest = build_source_allowlist_export_execution_gate(materialize=False)

    assert manifest["source_publication_authorized"] is False
    assert manifest["public_rc_remains_blocked"] is True
    assert manifest["source_allowlist_export_execution_gate_verdict"] in {
        "source_allowlist_export_execution_gate_verdict=pass",
        "source_allowlist_export_execution_gate_verdict=block",
    }


def test_phase_1443_completion_tokens_are_recorded() -> None:
    assert AGPL_LICENSE_HEADER_AUDIT_COMPLETE_PHASE_1443_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
    assert (
        PUBLIC_SOURCE_ALLOWLIST_EXECUTION_COMPLETE_PHASE_1443_TOKEN
        in PHASE_1443_LICENSE_AUDIT_TOKENS
    )
    assert AGPL_3_OR_LATER_LICENSE_HEADER_PRESENT_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
    assert PUBLIC_RC_NOT_PUBLISHED_PHASE_1443_TOKEN in PHASE_1443_LICENSE_AUDIT_TOKENS
