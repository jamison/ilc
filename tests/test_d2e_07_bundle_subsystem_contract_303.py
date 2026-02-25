"""Contract tests for Phase 303 D2e-07 bundle subsystem contract."""

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_d2e_07_bundle_subsystem_contract_303_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Bundle command surface contract",
        "## 3. Request/response JSON schema contract",
        "## 4. Error-code and exit-code contract",
        "## 5. Determinism and ordering contract",
        "## 6. Provider boundary contract",
        "## 7. Phase-304 handoff entry criteria",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_bundle_command_surface_and_subcommands_are_explicit() -> None:
    text = _read()
    assert "`ilc bundle`" in text
    for token in (
        "`ilc bundle inspect --bundle-cid <cid>`",
        "`ilc bundle verify --bundle-cid <cid>`",
        "`ilc bundle validate-local --bundle-cid <cid> --graph-state <path>`",
        "subcommand `--graph-state` is authoritative",
    ):
        assert token in text


def test_json_envelope_schema_and_checks_fields_are_explicit() -> None:
    text = _read()
    assert '{"ok": true, "data": <object>, "meta": <object>}' in text
    assert '{"ok": false, "error": {"code": <string>, "message": <string>}, "meta": <object>}' in text
    assert "`303.v0.1`" in text
    for token in ("`subject`", "`result`", "`checks`", "`check_type`", "`passed`"):
        assert token in text
    assert "bundle lane uses `result` (not `verdict`) intentionally" in text
    assert "`validate-local`: `graph_state_path`" in text


def test_error_and_exit_code_contract_is_explicit() -> None:
    text = _read()
    for token in (
        "- `0`: success,",
        "- `2`: argument/usage failure,",
        "- `1`: runtime/processing failure.",
        "bundle_invalid_input",
        "bundle_not_found",
        "bundle_manifest_invalid",
        "bundle_provider_blocked",
        "bundle_backend_unavailable",
        "bundle_internal_error",
    ):
        assert token in text


def test_determinism_and_phase304_handoff_gates_are_explicit() -> None:
    text = _read()
    for token in (
        "identical request input over identical backing state must yield byte-equivalent JSON",
        "`checks` ordering must be stable and explicitly documented per subcommand",
        "Phase 304 may begin only when:",
        "Phase-302 verify regression remains green",
    ):
        assert token in text


def test_provider_boundary_and_non_goals_are_explicit() -> None:
    text = _read()
    for token in (
        "local provider path is mandatory baseline",
        "external provider adapters are optional",
        "protocol core must not require a third-party facilitator service",
        "no `ilc_core/` runtime implementation in this phase",
        "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`",
    ):
        assert token in text
