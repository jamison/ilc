# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1566 rehearsal authority plan checks."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "docs/specs/ilc_block6_rehearsal_authority_plan_1566_v0.1.md"


def _plan_text() -> str:
    return PLAN_PATH.read_text(encoding="utf-8")


def test_phase_1566_plan_exists_with_required_sections() -> None:
    text = _plan_text()
    assert "# ILC Block 6 Rehearsal Authority Plan 1566 v0.1" in text
    for section in (
        "## 3. Rehearsal Namespace Definition",
        "## 4. Key Derivation and Separation",
        "## 5. Wipe-Right Scope",
        "## 6. Evidence Collection Format",
        "## 7. Phase 1562 Invitation Provenance Boundary",
        "## 8. OpenClaw Rehearsal Boundary",
        "## 9. Codex Local Harness Boundary",
    ):
        assert section in text


def test_rehearsal_namespace_id_is_well_formed() -> None:
    text = _plan_text()
    match = re.search(r"\*\*Namespace ID:\*\* `([^`]+)`", text)
    assert match, "namespace id must be declared"
    namespace_id = match.group(1)
    assert namespace_id
    assert not re.search(r"\s", namespace_id)
    assert re.fullmatch(r"[a-z0-9_]+", namespace_id)


def test_wipe_scope_covers_harness_configs_and_preserves_global_state() -> None:
    text = _plan_text()
    assert "harness/openclaw/" in text
    assert "harness/codex/" in text
    assert "OpenClaw `ilc-local` namespace config" in text
    assert "Codex local harness temp config" in text
    assert "global OpenClaw CLI installation" in text
    assert "committed docs/sims/ Phase 1568 evidence packages" in text
    assert "production Atlas LMDB" in text


def test_production_key_use_is_prohibited() -> None:
    text = _plan_text()
    assert "production_key_material_used=false" in text
    assert "Production Genesis Agent signing keys are prohibited" in text
    assert "private-key-export" in text
    assert "mnemonic-output" in text


def test_evidence_format_required_fields_are_present() -> None:
    text = _plan_text()
    required_fields = (
        "schema_version",
        "phase",
        "lane_id",
        "rehearsal_namespace_id",
        "executor_agent_id",
        "timestamp_class",
        "created_at_utc",
        "input_refs",
        "commands",
        "artifact_sha256",
        "payload_sha256",
        "result_summary",
        "non_authorization",
    )
    for field in required_fields:
        assert field in text
    assert "sort_keys=True" in text
    assert "allow_nan=False" in text


def test_phase_1562_invitation_boundary_is_explicit() -> None:
    text = _plan_text()
    assert "Phase 1562 production invitation provenance records remain production records" in text
    assert "must not mutate them" in text
    assert "separate rehearsal identities" in text

