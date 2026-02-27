"""Contract checks for Phase 292 ADM-003 architecture lock artifact."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Architecture layers and responsibilities",
        "## 3. Signing and key-isolation boundaries",
        "## 4. Protocol/SDK/runtime dependency map",
        "## 5. Security and privacy invariants",
        "## 6. Non-goals and phased rollout",
        "## 7. Canonical anchors",
    ):
        assert heading in text


def test_wallet_agnostic_signing_is_explicit() -> None:
    text = _read().lower()
    assert "wallet-agnostic signing" in text


def test_key_isolation_and_kid_privacy_boundaries_present() -> None:
    text = _read().lower()
    assert "key-isolation boundary" in text
    assert "kid" in text
    assert "must not contain raw public key material" in text


def test_runtime_and_decision_log_boundaries_present() -> None:
    text = _read().lower()
    assert "no runtime changes in `ilc_core/`" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
