"""
Tests for Phase 1573d: ADR-0035 type registry public RC activation posture decision.

Non-SENSITIVE phase: no guard clearance. Posture: default_off_at_public_rc.
"""
import importlib
import os
import re


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTURE_DOC = os.path.join(
    REPO_ROOT,
    "docs/specs/ilc_adr_0035_public_rc_activation_posture_1573d_v0.1.md",
)
STATUS_MD = os.path.join(REPO_ROOT, "docs/phases/STATUS.md")
POST_RC_TARGETS = os.path.join(
    REPO_ROOT,
    "docs/specs/ilc_post_rc_architectural_targets_v0.1.md",
)
TYPE_REGISTRY_PY = os.path.join(
    REPO_ROOT,
    "ilc_core/bundle/type_registry.py",
)


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def test_posture_doc_exists():
    assert os.path.isfile(POSTURE_DOC), f"Posture doc missing: {POSTURE_DOC}"


def test_posture_doc_contains_exactly_one_posture_token():
    content = _read(POSTURE_DOC)
    tokens = [
        "adr_0035_posture_default_off_at_public_rc",
        "adr_0035_posture_public_rc_live_reference_metadata_only",
        "adr_0035_posture_public_rc_live_full_activation",
    ]
    found = [t for t in tokens if t in content]
    assert len(found) == 1, (
        f"Expected exactly one posture token in posture doc; found: {found}"
    )
    assert found[0] == "adr_0035_posture_default_off_at_public_rc", (
        f"Expected default_off posture; found: {found[0]}"
    )


def test_adr_0035_type_registry_not_activated_is_true():
    assert os.path.isfile(TYPE_REGISTRY_PY), (
        f"type_registry.py not found at {TYPE_REGISTRY_PY}"
    )
    content = _read(TYPE_REGISTRY_PY)
    # Confirm guard is True (posture 1: not cleared)
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in content, (
        "Guard ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED must be True in type_registry.py"
    )
    # Confirm guard was not cleared
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = False" not in content, (
        "Guard must NOT be False in type_registry.py — guard clearance is out of scope for Phase 1573d"
    )


def test_status_md_contains_posture_locked_token():
    content = _read(STATUS_MD)
    assert "adr_0035_public_rc_activation_posture_locked" in content, (
        "adr_0035_public_rc_activation_posture_locked token missing from STATUS.md"
    )


def test_status_md_contains_posture_token():
    content = _read(STATUS_MD)
    assert "adr_0035_posture_default_off_at_public_rc" in content, (
        "adr_0035_posture_default_off_at_public_rc token missing from STATUS.md"
    )


def test_status_md_contains_public_path_blocked_token():
    content = _read(STATUS_MD)
    assert "public_path_remains_blocked_phase_1573d" in content, (
        "public_path_remains_blocked_phase_1573d token missing from STATUS.md"
    )


def test_posture_doc_references_cdl_099_ratification():
    content = _read(POSTURE_DOC)
    assert "cdl_099_ratified" in content or "CDL-099" in content, (
        "Posture doc must reference CDL-099 ratification"
    )


def test_posture_doc_references_cdl_100_ratification():
    content = _read(POSTURE_DOC)
    assert "cdl_100_ratified" in content or "CDL-100" in content, (
        "Posture doc must reference CDL-100 ratification"
    )


def test_post_rc_targets_updated_with_phase_1573d_note():
    content = _read(POST_RC_TARGETS)
    assert "Phase 1573d" in content and "default_off_at_public_rc" in content, (
        "ilc_post_rc_architectural_targets_v0.1.md must contain Phase 1573d posture note"
    )
