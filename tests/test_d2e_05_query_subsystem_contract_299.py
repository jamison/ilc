"""Contract tests for Phase 299 D2e-05 query subsystem contract."""

from pathlib import Path

ARTIFACT_PATH = Path("docs/specs/ilc_d2e_05_query_subsystem_contract_299_v0.1.md")


def _read() -> str:
    return ARTIFACT_PATH.read_text(encoding="utf-8")


def test_artifact_exists() -> None:
    assert ARTIFACT_PATH.exists()


def test_required_sections_present() -> None:
    text = _read()
    for heading in (
        "## 1. Purpose and scope",
        "## 2. Query command surface contract",
        "## 3. Request/response JSON schema contract",
        "## 4. Error-code and exit-code contract",
        "## 5. Determinism and ordering contract",
        "## 6. Phase-300 handoff entry criteria",
        "## 7. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_query_command_surface_and_subcommands_are_explicit() -> None:
    text = _read()
    assert "`ilc query`" in text
    for token in (
        "`ilc query node --node-id <id>`",
        "`ilc query epoch --epoch <n>`",
        "`ilc query claim --claim-id <id>`",
    ):
        assert token in text


def test_json_envelope_language_is_explicit() -> None:
    text = _read()
    assert '{"ok": true, "data": <object>, "meta": <object>}' in text
    assert '{"ok": false, "error": {"code": <string>, "message": <string>}, "meta": <object>}' in text


def test_error_and_exit_code_contract_is_explicit() -> None:
    text = _read()
    for token in (
        "- `0`: success,",
        "- `2`: argument/usage failure,",
        "- `1`: runtime/processing failure.",
        "query_invalid_input",
        "query_not_found",
        "query_backend_unavailable",
        "query_internal_error",
    ):
        assert token in text


def test_determinism_ordering_and_phase300_handoff_are_explicit() -> None:
    text = _read()
    for token in (
        "identical request input over identical backing state must yield byte-equivalent JSON",
        "map/object keys in emitted JSON must be sorted lexicographically",
        "Phase 300 may begin only when:",
        "this Phase-299 contract artifact exists and contract tests pass",
        "command surface and error/exit code semantics are unchanged",
    ):
        assert token in text


def test_no_runtime_and_no_decision_log_mutation_boundaries_are_explicit() -> None:
    text = _read()
    assert "no `ilc_core/` runtime implementation in this phase" in text
    assert "no mutation of `docs/specs/ilc_constitutional_decision_log_v0.1.md`" in text
