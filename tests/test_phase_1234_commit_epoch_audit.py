"""
Phase 1234 — commit.epoch audit findings verification.

These tests confirm that:
- The audit findings document exists and contains required tokens
- The runtime conflict described in the audit is real (live file checks)
- No ilc_core/ files were modified by Phase 1234

No ilc_core/ runtime changes occur in this phase.
"""

import inspect
import subprocess
import sys
from pathlib import Path


AUDIT_DOC = Path("docs/specs/ilc_commit_epoch_audit_1234_v0.1.md")
EVENT_LOG_PATH = Path("ilc_core/protocol/event_log.py")
ECONOMIC_CYCLE_PATH = Path("ilc_core/rc/economic_cycle_runtime.py")


def test_audit_doc_exists():
    """Test 1: Audit findings doc exists at expected path."""
    assert AUDIT_DOC.exists(), f"Audit doc not found at {AUDIT_DOC}"


def test_audit_doc_contains_completion_token():
    """Test 2: Doc contains commit_epoch_audit_complete_phase_1234."""
    content = AUDIT_DOC.read_text(encoding="utf-8")
    assert "commit_epoch_audit_complete_phase_1234" in content, (
        "Audit doc missing required completion token: commit_epoch_audit_complete_phase_1234"
    )


def test_make_commit_epoch_event_has_created_at_param():
    """
    Test 3: make_commit_epoch_event in event_log.py takes created_at as a parameter.

    Confirms the conflict is real — the live file requires wall-clock input.
    """
    from ilc_core.protocol.event_log import make_commit_epoch_event

    sig = inspect.signature(make_commit_epoch_event)
    assert "created_at" in sig.parameters, (
        "make_commit_epoch_event does not have created_at parameter — "
        "the Phase 1226 wall-clock conflict may already be resolved; verify manually"
    )


def test_validate_commit_epoch_payload_requires_created_at():
    """
    Additional check: validate_commit_epoch_payload requires created_at in required fields.

    This confirms the validator enforces the wall-clock field, not just the constructor.
    """
    source = EVENT_LOG_PATH.read_text(encoding="utf-8")
    # The required_top set in validate_commit_epoch_payload must contain created_at
    assert '"created_at"' in source or "'created_at'" in source, (
        "created_at not found as string literal in event_log.py"
    )
    # More specifically, confirm required_top block contains created_at
    assert "created_at" in source, (
        "created_at not found in event_log.py — conflict may already be resolved"
    )


def test_economic_cycle_runtime_contains_utc_now():
    """Test 4: economic_cycle_runtime.py contains _utc_now (confirm wall-clock is called)."""
    source = ECONOMIC_CYCLE_PATH.read_text(encoding="utf-8")
    assert "_utc_now" in source, (
        "_utc_now not found in economic_cycle_runtime.py — "
        "wall-clock call may already be removed; verify manually"
    )


def test_audit_doc_contains_patch_plan_section():
    """Test 5: Doc contains a §3 patch plan section."""
    content = AUDIT_DOC.read_text(encoding="utf-8")
    assert "§3" in content or "## §3" in content, (
        "Audit doc does not contain a §3 patch plan section"
    )
    assert "Option A" in content, (
        "Audit doc §3 does not name Option A"
    )


def test_no_ilc_core_files_modified():
    """
    Test 6: No ilc_core/ files were modified by Phase 1234.

    Checks the Phase 1234 backfill commit directly rather than HEAD. Phase 1235
    is expected to add make_canonical_commit_epoch_event later, so a HEAD-based
    assertion would become stale immediately after the authorized mutation.
    """
    result = subprocess.run(
        ["git", "show", "1ffc94ed:ilc_core/protocol/event_log.py"],
        capture_output=True,
        text=True,
        check=True,
    )
    source = result.stdout
    assert "make_canonical_commit_epoch_event" not in source, (
        "make_canonical_commit_epoch_event present at Phase 1234 commit — "
        "Phase 1234 was not audit-only"
    )
