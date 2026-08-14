# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.cli.d2e_submit_cli import (
    GraphSubmitAdvisoryEnvelope,
    SubmitCommandError,
    build_graph_submit_envelope,
    build_refutation_primitive,
    check_graph_mutation_allowed,
    handle_submit,
)
from ilc_core.epistemic.truth_primitive_sig_verifier import verify_truth_primitive_sig
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)


AGENT_ID_HEX = "a" * 64
TARGET_NODE_ID = "cid_" + "b" * 59
EVIDENCE_NODE_ID = "cid_" + "c" * 59


def _private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


def _assert_truth_submission() -> dict[str, object]:
    return {
        "agent_id": AGENT_ID_HEX,
        "epoch": 4,
        "payload": {
            "content": {"body": "04b graph submit envelope"},
            "epistemic_type": "objective",
            "parent_node_ids": [],
            "primitive_type": "observation",
        },
        "primitive": "assert.truth",
        "v": 1,
    }


def _signed_record(envelope: GraphSubmitAdvisoryEnvelope) -> dict[str, object]:
    record = dict(envelope.truth_primitive)
    record["sig"] = envelope.sig
    record["sig_pubkey_hex"] = envelope.sig_pubkey_hex
    record["sig_pubkey_fingerprint"] = envelope.sig_pubkey_fingerprint
    record["sig_scheme"] = envelope.sig_scheme
    return record


def test_build_graph_submit_envelope_happy_path_verifies() -> None:
    envelope = build_graph_submit_envelope(
        _assert_truth_submission(),
        AGENT_ID_HEX,
        4,
        _private_key(),
    )

    assert isinstance(envelope, GraphSubmitAdvisoryEnvelope)
    assert envelope.agent_id_hex == AGENT_ID_HEX
    assert envelope.epoch == 4
    assert len(envelope.sig) == 128
    assert len(envelope.sig_pubkey_hex) == 64
    assert verify_truth_primitive_sig(_signed_record(envelope)) is True


@pytest.mark.parametrize("bad_agent_id", ["a" * 63, "g" * 64, "A" * 64])
def test_build_graph_submit_envelope_rejects_invalid_agent_id_hex(
    bad_agent_id: str,
) -> None:
    with pytest.raises(ValueError, match="invalid_agent_id_hex"):
        build_graph_submit_envelope(
            _assert_truth_submission(),
            bad_agent_id,
            4,
            _private_key(),
        )


def test_build_graph_submit_envelope_rejects_bool_epoch() -> None:
    with pytest.raises(ValueError, match="invalid_epoch"):
        build_graph_submit_envelope(
            _assert_truth_submission(),
            AGENT_ID_HEX,
            True,
            _private_key(),
        )


def test_build_graph_submit_envelope_rejects_negative_epoch() -> None:
    with pytest.raises(ValueError, match="invalid_epoch"):
        build_graph_submit_envelope(
            _assert_truth_submission(),
            AGENT_ID_HEX,
            -1,
            _private_key(),
        )


def test_graph_submit_comment_keeps_advisory_type_out_of_value_dispatch() -> None:
    source = Path("ilc_core/cli/d2e_submit_cli.py").read_text(encoding="utf-8")

    assert "GRAPH_SUBMIT type is advisory pending CDL-111 ratification" in source
    assert "do not wire to AgentActionEnvelope dispatch until ratified" in source


def test_build_refutation_primitive_happy_path_passes_runtime_validator() -> None:
    submission = build_refutation_primitive(
        TARGET_NODE_ID,
        "The target claim is falsified by the cited evidence.",
        [EVIDENCE_NODE_ID],
        AGENT_ID_HEX,
        5,
    )

    result = validate_truth_primitive_submission(submission)
    assert result.primitive == "refute.claim"
    assert result.creates_node is False
    assert submission["primitive"] == "refute.claim"
    assert "node_type" not in submission


def test_build_refutation_primitive_rejects_empty_target_node_id() -> None:
    with pytest.raises(ValueError, match="invalid_refutation_target_empty"):
        build_refutation_primitive("", "reason", [], AGENT_ID_HEX, 5)


def test_build_refutation_primitive_rejects_reason_over_500_utf8_bytes() -> None:
    with pytest.raises(ValueError, match="invalid_refutation_reason_too_long"):
        build_refutation_primitive(TARGET_NODE_ID, "é" * 251, [], AGENT_ID_HEX, 5)


def test_build_refutation_primitive_accepts_reason_exactly_500_utf8_bytes() -> None:
    submission = build_refutation_primitive(
        TARGET_NODE_ID,
        "x" * 500,
        [],
        AGENT_ID_HEX,
        5,
    )

    validate_truth_primitive_submission(submission)


def test_build_refutation_primitive_rejects_empty_evidence_node_id() -> None:
    with pytest.raises(ValueError, match="invalid_evidence_node_id"):
        build_refutation_primitive(TARGET_NODE_ID, "reason", [""], AGENT_ID_HEX, 5)


def test_check_graph_mutation_allowed_true_raises() -> None:
    with pytest.raises(ValueError, match="graph_mutation_blocked_public_path_not_cleared"):
        check_graph_mutation_allowed(True)


def test_check_graph_mutation_allowed_false_noop() -> None:
    assert check_graph_mutation_allowed(False) is None


def test_check_graph_mutation_allowed_rejects_non_bool_int() -> None:
    with pytest.raises(TypeError, match="invalid_guard_value_not_bool"):
        check_graph_mutation_allowed(1)  # type: ignore[arg-type]


def test_handle_submit_rejects_bool_epoch() -> None:
    args = type(
        "Args",
        (),
        {
            "agent_id": AGENT_ID_HEX,
            "epoch": True,
            "payload_file": None,
            "payload_json": "{}",
            "primitive": "assert.truth",
            "sig": "UNSIGNED",
            "signing_key": None,
        },
    )()

    with pytest.raises(SubmitCommandError) as exc_info:
        handle_submit(args)
    assert exc_info.value.token == "submit_epoch_invalid"


def test_handle_submit_calls_graph_mutation_gate_before_lmdb_write(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store_path = tmp_path / "truth-store"
    monkeypatch.setenv("ILC_TRUTH_GRAPH_STORE_PATH", str(store_path))
    args = type(
        "Args",
        (),
        {
            "agent_id": AGENT_ID_HEX,
            "epoch": 1,
            "payload_file": None,
            "payload_json": (
                '{"content":{"body":"blocked"},"epistemic_type":"objective",'
                '"parent_node_ids":[],"primitive_type":"observation"}'
            ),
            "primitive": "assert.truth",
            "public_path_guard_value": True,
            "sig": "UNSIGNED",
            "signing_key": None,
        },
    )()

    with pytest.raises(ValueError, match="graph_mutation_blocked_public_path_not_cleared"):
        handle_submit(args)
    assert not store_path.exists()
