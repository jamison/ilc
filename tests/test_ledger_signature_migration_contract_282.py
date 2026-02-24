from __future__ import annotations

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_ledger_signature_migration_contract_282_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Purpose and scope",
    "## 2. Surface migration map",
    "## 3. Dual-verify window contract",
    "## 4. Cutoff criteria and enforcement trigger",
    "## 5. Backward-compatibility and rollback boundary",
    "## 6. Security invariants",
    "## 7. Non-goals",
    "## 8. Canonical anchors",
]

REQUIRED_MAP_ENTRIES = [
    "Bundle signing/verification",
    "Registry signing/verification",
    "Channel signing/verification",
]


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for section in REQUIRED_SECTIONS:
        assert section in text, section


def test_required_migration_map_entries_present() -> None:
    text = _read()
    for entry in REQUIRED_MAP_ENTRIES:
        assert entry in text, entry


def test_required_invariants_present() -> None:
    text = _read()
    assert "No silent fallback from asymmetric-required mode to HMAC-only acceptance after cutoff." in text
    assert "Canonical fingerprint must bind signer identity during migration." in text
    assert "Compatibility mode must be explicitly bounded by window/gate conditions." in text


def test_non_goals_include_no_runtime_and_no_decision_log_mutation() -> None:
    text = _read()
    assert "does not" in text
    assert "implement runtime migration changes in `ilc_core/`" in text
    assert "mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
