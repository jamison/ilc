from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from ilc_core.governance import challenge_node_runtime as runtime


SPEC_PATH = Path("docs/specs/ilc_cdl_006_challenge_node_spec_1381_v0.1.md")
REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
RUNTIME_PATH = Path("ilc_core/governance/challenge_node_runtime.py")


def test_phase_1381_required_tokens_and_public_rc_exclude_marker() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")

    for token in (
        "cdl_006_challenge_node_spec_phase_1381",
        "cdl_006_challenge_node_runtime_stub_phase_1381",
        "cdl_006_multi_body_3_body_quorum_spec_committed",
    ):
        assert token in spec
        assert token in runtime_source

    assert "PUBLIC_RC_EXCLUDE: cdl_006_challenge_node_runtime_stub_phase_1381" in runtime_source


def test_cdl_006_register_row_ratifies_multi_body_checks_only() -> None:
    register = REGISTER_PATH.read_text(encoding="utf-8")
    cdl_006_rows = [
        line
        for line in register.splitlines()
        if line.startswith("| CDL-006 |")
    ]
    assert len(cdl_006_rows) == 1
    row = cdl_006_rows[0]
    assert "| ratified |" in row
    assert "| single-body, dual-body, multi-body checks |" in row
    assert "| multi-body checks |" in row


def test_stub_schema_contracts_lock_3_body_quorum_shape() -> None:
    schema = runtime.challenge_record_schema()
    attestation_schema = runtime.challenge_body_attestation_schema()
    audit_schema = runtime.audit_path_record_schema()

    assert schema["required_body_count"] == 3
    assert schema["required_body_roles"] == [
        "constitutional",
        "technical",
        "affected_party",
    ]
    assert "body_attestations" in schema["required_fields"]
    assert "audit_path_ref" in schema["required_fields"]
    assert attestation_schema["body_role_enum"] == schema["required_body_roles"]
    assert "previous_entry_ref" in audit_schema["required_fields"]
    assert audit_schema["hash_link_field"] == "previous_entry_ref"


def test_schema_template_json_is_canonical_and_sorted() -> None:
    first = runtime.canonical_schema_template_json()
    second = runtime.canonical_schema_template_json()
    assert first == second
    assert first == json.dumps(
        json.loads(first),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def test_production_functions_are_signature_locked_and_deferred() -> None:
    verify_signature = inspect.signature(runtime.verify_challenge_quorum)
    write_signature = inspect.signature(runtime.write_challenge_audit_path_record)

    assert list(verify_signature.parameters) == [
        "challenge_record",
        "required_body_roles",
    ]
    assert verify_signature.parameters["required_body_roles"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )
    assert list(write_signature.parameters) == [
        "challenge_record",
        "audit_event",
        "previous_entry_ref",
    ]
    assert write_signature.parameters["previous_entry_ref"].kind is (
        inspect.Parameter.KEYWORD_ONLY
    )

    with pytest.raises(ValueError, match=runtime.CDL006_PRODUCTION_RUNTIME_DEFERRED_TOKEN):
        runtime.verify_challenge_quorum({})
    with pytest.raises(ValueError, match=runtime.CDL006_PRODUCTION_RUNTIME_DEFERRED_TOKEN):
        runtime.write_challenge_audit_path_record({}, {})


def test_spec_rejects_single_and_dual_body_shortcuts() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    assert "Single-body path | Forbidden" in spec
    assert "Dual-body path | Forbidden" in spec
    assert "Phase 1382 must preserve the 3-body-only constraint" in spec
    assert "does not implement production quorum verification" in spec
