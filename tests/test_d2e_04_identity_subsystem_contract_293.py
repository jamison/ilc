"""Contract checks for Phase 293 D2e-04 identity subsystem contract."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_d2e_04_identity_subsystem_contract_293_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Command surface contract",
        "## 3. Request/response schema contract",
        "## 4. Error-code and exit-code contract",
        "## 5. Persistence and determinism boundaries",
        "## 6. Non-goals and rollout boundary",
        "## 7. Canonical anchors",
    ):
        assert heading in text


def test_command_surface_and_json_envelope_language_present() -> None:
    text = _read().lower()
    assert "ilc identity" in text
    assert '"schema_version": "254.v0.1"' in text
    assert '"command": "identity"' in text
    assert '"ok": true' in text
    assert '"ts_utc":' in text
    assert '"data": {}' in text
    assert '"ok": false' in text
    assert '"error": true' in text
    assert '"code": "1"' in text
    assert '"message":' in text
    assert '"details": {}' in text


def test_error_and_exit_code_contract_present() -> None:
    text = _read().lower()
    assert "exit code contract" in text
    assert "`0`" in text
    assert "`1`" in text
    assert "`2`" in text
    assert "`3`" in text
    assert "machine-readable discriminator" in text
    assert "`message` may include argparse usage text" in text


def test_boundary_statements_present() -> None:
    text = _read().lower()
    assert "no runtime implementation in `ilc_core/`" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
