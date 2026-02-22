from __future__ import annotations

from pathlib import Path


SIGNING_SPEC = Path("docs/specs/ilc_signing_provider_interface_262_v0.1.md")
SDK_BOUNDARY = Path("docs/specs/ilc_sdk_boundary_contract_234_v0.1.md")
ADM_002 = Path("docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md")
LINEAGE_V01 = Path("docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md")
LINEAGE_V02 = Path("docs/specs/ilc_lineage_lifecycle_event_schema_v0.2.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_target_files_exist() -> None:
    for path in [SIGNING_SPEC, SDK_BOUNDARY, ADM_002, LINEAGE_V01, LINEAGE_V02]:
        assert path.exists(), f"missing file: {path}"


def test_signing_spec_has_required_sections() -> None:
    text = _read(SIGNING_SPEC)
    headings = [
        "## 1. Purpose and scope",
        "## 2. Provider types",
        "## 3. Interface contract",
        "## 4. Algorithm bridge statement",
        "## 5. Privacy invariant for COSE `kid`",
        "## 6. Non-goals",
        "## 7. Canonical anchors",
    ]
    for heading in headings:
        assert heading in text


def test_signing_spec_contains_required_kid_privacy_invariant() -> None:
    text = _read(SIGNING_SPEC)
    assert "must be a protocol-internal opaque identifier" in text
    assert "must not be raw public key material" in text
    assert "must not be raw public key bytes" in text
    assert "must not be a direct hash of public key material" in text


def test_sdk_boundary_contains_provider_wording_and_non_local_example() -> None:
    text = _read(SDK_BOUNDARY)
    assert "--key` selects a signing provider" in text
    assert "hardware wallet/HSM" in text
    assert "external wallet SDK callback" in text
    assert "coinbase://agent-wallet-id" in text


def test_adm_002_uses_signing_provider_credential_handling_wording() -> None:
    text = _read(ADM_002)
    assert "Signing provider credential handling must avoid unsafe transcript leakage." in text


def test_lineage_schema_v02_contains_external_provider_coordination_section() -> None:
    text = _read(LINEAGE_V02)
    assert "## 3. Lifecycle coordination with external signing providers" in text
    assert "explicit ILC `rotate` lifecycle event emission" in text
    assert "explicit ILC `revoke` lifecycle event emission" in text
    assert "explicit ILC `recover` lifecycle event emission" in text


def test_lineage_schema_v01_remains_present() -> None:
    assert LINEAGE_V01.exists()
