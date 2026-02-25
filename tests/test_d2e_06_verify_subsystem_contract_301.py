"""Contract tests for Phase 301 D2e-06 verify subsystem contract."""

from pathlib import Path


ARTIFACT_PATH = Path("docs/specs/ilc_d2e_06_verify_subsystem_contract_301_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Verify command surface contract",
        "## 3. Request/response JSON schema contract",
        "## 4. Error-code and exit-code contract",
        "## 5. Determinism, ordering, and policy-read-only boundary",
        "## 6. Phase-302 handoff entry criteria",
        "## 7. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_verify_command_surface_and_subcommands_are_explicit() -> None:
    text = _read()
    assert "`ilc verify`" in text
    for token in (
        "`ilc verify claim --claim-id <id>`",
        "`ilc verify node --node-id <id>`",
        "`ilc verify lineage --lineage-id <id>`",
    ):
        assert token in text


def test_json_envelope_language_and_schema_tag_are_explicit() -> None:
    text = _read()
    assert '{"ok": true, "data": <object>, "meta": <object>}' in text
    assert '{"ok": false, "error": {"code": <string>, "message": <string>}, "meta": <object>}' in text
    assert "`301.v0.1`" in text
    for token in ("`subject`", "`verdict`", "`checks`", "`check_type`", "`passed`"):
        assert token in text


def test_error_and_exit_code_contract_is_explicit() -> None:
    text = _read()
    for token in (
        "- `0`: success,",
        "- `2`: argument/usage failure,",
        "- `1`: runtime/processing failure.",
        "verify_invalid_input",
        "verify_not_found",
        "verify_signature_mismatch",
        "verify_policy_rejected",
        "verify_backend_unavailable",
        "verify_internal_error",
    ):
        assert token in text


def test_determinism_and_phase302_handoff_gates_are_explicit() -> None:
    text = _read()
    for token in (
        "identical request input over identical backing state must yield byte-equivalent JSON",
        "`checks` list ordering must be stable and explicitly documented per subcommand",
        "`verify lineage` validates against local identity-state surface only",
        "Phase 302 may begin only when:",
        "Phase-300 query regression remains green",
    ):
        assert token in text


def test_no_runtime_no_decision_log_and_policy_constants_boundaries_are_explicit() -> None:
    text = _read()
    assert "no `ilc_core/` runtime implementation in this phase" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
    assert "must not introduce or derive new anti-abuse/reputation scoring constants" in text
