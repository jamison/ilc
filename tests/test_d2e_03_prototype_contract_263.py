from __future__ import annotations

from pathlib import Path


CONTRACT_PATH = Path("docs/specs/ilc_d2e_03_prototype_contract_263_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_exists() -> None:
    assert CONTRACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read(CONTRACT_PATH)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Locked command surface constraints (Phase-253 anchor)",
        "## 3. Output schema conformance constraints (Phase-254 anchor)",
        "## 4. Data model and persistence boundary (JSON-first local graph)",
        "## 5. Explicit DAG-CBOR deferral statement",
        "## 6. Acceptance checklist for Phase 264",
        "## 7. Non-goals",
        "## 8. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_all_primitive_commands_present() -> None:
    text = _read(CONTRACT_PATH)
    for command in ["assert", "validate", "contradict", "refute", "revise", "link", "epoch"]:
        assert f"`{command}`" in text


def test_all_operational_commands_present() -> None:
    text = _read(CONTRACT_PATH)
    for command in [
        "query",
        "verify",
        "balance",
        "identity",
        "bundle",
        "shard",
        "capproof",
        "config",
    ]:
        assert f"`{command}`" in text


def test_json_first_local_state_language_present() -> None:
    text = _read(CONTRACT_PATH)
    assert "local JSON-backed graph state" in text


def test_dag_cbor_deferral_language_present() -> None:
    text = _read(CONTRACT_PATH)
    assert "DAG-CBOR" in text
    assert "deferred" in text


def test_phase_264_acceptance_checklist_present() -> None:
    text = _read(CONTRACT_PATH)
    assert "## 6. Acceptance checklist for Phase 264" in text
    assert "- [ ]" in text


def test_contract_does_not_claim_runtime_implementation_complete() -> None:
    text = _read(CONTRACT_PATH).lower()
    assert "implementation complete" not in text
