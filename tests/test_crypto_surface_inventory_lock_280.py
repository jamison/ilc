from __future__ import annotations

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_crypto_surface_inventory_lock_280_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Purpose and scope",
    "## 2. Surface inventory table",
    "## 3. Security-role classification rubric",
    "## 4. Migration priority and rationale",
    "## 5. Compatibility constraints",
    "## 6. Non-goals",
    "## 7. Canonical anchors",
]

REQUIRED_SURFACES = [
    "ilc_core/ledger/canon_bundle_utils.py",
    "ilc_core/ledger/canon_bundle_key_registry.py",
    "ilc_core/ledger/canon_bundle_key_registry_channel_signing.py",
    "ilc_core/ledger/settlement_verification.py",
    "ilc_core/security/signer_lineage_runtime.py",
    "ilc_core/security/key_compromise_runtime.py",
    "ilc_core/ledger/canon_export_bundle_sign.py",
    "ilc_core/ledger/canon_export_bundle_verify_sig.py",
]


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for section in REQUIRED_SECTIONS:
        assert section in text, section


def test_required_surfaces_present() -> None:
    text = _read()
    for surface in REQUIRED_SURFACES:
        assert surface in text, surface


def test_classification_labels_present() -> None:
    text = _read()
    for label in ("auth_critical", "auth_adjacent", "operational_alias"):
        assert label in text, label


def test_priority_labels_present() -> None:
    text = _read()
    for priority in ("P0", "P1", "P2"):
        assert priority in text, priority


def test_non_goals_include_no_runtime_and_no_decision_log_mutation() -> None:
    text = _read()
    assert "does not" in text
    assert "implement runtime migration changes" in text
    assert "mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
