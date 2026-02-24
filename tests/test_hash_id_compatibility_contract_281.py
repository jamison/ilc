from __future__ import annotations

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_hash_id_compatibility_contract_281_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Purpose and scope",
    "## 2. Canonical identifier rule",
    "## 3. Alias compatibility rule",
    "## 4. Dual-field schema contract",
    "## 5. Verification behavior during migration window",
    "## 6. Cutoff criteria and exit conditions",
    "## 7. Non-goals",
    "## 8. Canonical anchors",
]


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for section in REQUIRED_SECTIONS:
        assert section in text, section


def test_required_canonical_terms_present() -> None:
    text = _read()
    for term in ("canonical_fingerprint", "short_alias_id", "key_fingerprint"):
        assert term in text, term


def test_required_invariants_present() -> None:
    text = _read()
    assert "all auth-critical and auth-adjacent equality checks must ultimately bind on `canonical_fingerprint`" in text
    assert "alias match without canonical match cannot authorize acceptance" in text
    assert "alias-only acceptance is not permitted on migrated surfaces" in text


def test_non_goals_include_no_runtime_and_no_decision_log_mutation() -> None:
    text = _read()
    assert "does not" in text
    assert "implement runtime migration in `ilc_core/`" in text
    assert "mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
