from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ilc_core.testing.phase_commit_manifest import resolve_phase_commit_ref_or_skip

from ilc_core.testing.ratification_mutation_scope_guardrail import (
    assert_head_commit_touched_no_runtime_files,
)


CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.6.md")
REPORT_PATH = Path("docs/specs/ilc_integration_coherence_report_278_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _resolve_phase_278_commit_ref() -> str:
    return resolve_phase_commit_ref_or_skip("phase_278")


def test_coherence_report_exists_with_required_sections() -> None:
    text = _read(REPORT_PATH)
    assert REPORT_PATH.exists()
    required = [
        "## 1. Scope",
        "## 2. Capsule alignment check (v0.6 versus 270-277 artifacts)",
        "## 3. CDL log alignment check",
        "## 4. Cross-reference integrity",
        "## 5. Non-goal boundaries",
    ]
    for section in required:
        assert section in text


def test_capsule_v0_6_exists_and_supersedes_v0_5() -> None:
    text = _read(CAPSULE_PATH)
    assert CAPSULE_PATH.exists()
    assert "# ILC Antigravity Context Capsule v0.6" in text
    assert "Supersedes: `ilc_antigravity_context_capsule_v0.5.md`" in text


def test_coherence_report_confirms_issuance_ratification_set() -> None:
    text = _read(REPORT_PATH)
    assert "`CDL-029 status = ratified`, `ratified_phase = 272`" in text
    assert "`CDL-026 status = ratified`, `ratified_phase = 273`" in text
    assert "`CDL-028 status = ratified`, `ratified_phase = 274`" in text
    assert "`CDL-027 status = ratified`, `ratified_phase = 276`" in text
    assert "`CDL-030 status = ratified`, `ratified_phase = 277`" in text


def test_coherence_report_confirms_cdl_031_open() -> None:
    text = _read(REPORT_PATH)
    assert "`CDL-031 status = open`" in text


def test_coherence_report_confirms_prior_ratified_set() -> None:
    text = _read(REPORT_PATH)
    assert "`CDL-001 status = ratified`" in text
    assert "`CDL-002 status = ratified`" in text
    assert "`CDL-007 status = ratified`" in text
    assert "`CDL-025 status = ratified`" in text
    assert "`CDL-019 status = ratified`" in text
    assert "`CDL-032 status = ratified`" in text


def test_capsule_v0_6_contains_required_new_sections() -> None:
    text = _read(CAPSULE_PATH)
    assert "## 26. Issuance Governance Closure State (NEW in v0.6)" in text
    assert "## 27. CDL-031 Status (NEW in v0.6)" in text


def test_phase_278_commit_touched_no_runtime_files() -> None:
    commit_ref = _resolve_phase_278_commit_ref()
    assert_head_commit_touched_no_runtime_files(commit_ref=commit_ref)
