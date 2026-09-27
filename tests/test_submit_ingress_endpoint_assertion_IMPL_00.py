from __future__ import annotations

import hashlib
import inspect
import json

import pytest

from ilc_core.consensus import submit_ingress_endpoint_assertion as endpoint
from ilc_core.consensus.submit_ingress_endpoint_assertion import (
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_DST_PREFIX,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND,
    PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_SCHEMA_VERSION,
    PublicSubmitIngressEndpointAssertion,
    assertion_content_sha256,
    canonical_endpoint_assertion_payload,
    canonical_revocation_payload,
    load_from_atlas,
    parse_endpoint_assertion,
    parse_endpoint_revocation,
    submit_ingress_assertion_candidate_id,
    verify_endpoint_assertion_bls_signature,
)
from ilc_core.epistemic import truth_primitive_submission_runtime as truth_runtime
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError


NETWORK_ID = "ilc-public-rc-01-testnet-harness"
AGENT_ID = "a" * 96
TRANSPORT_KEY = "b" * 96
BLS_KEY = "c" * 96
SIGNATURE = "d" * 192
TLS_FINGERPRINT = "e" * 64


def _assertion_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "node_kind": PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NODE_KIND,
        "schema_version": PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_SCHEMA_VERSION,
        "network_id": NETWORK_ID,
        "service_kind": "public_submit_ingress",
        "serving_agent_id": AGENT_ID,
        "transport_key_kind": "purpose_scoped_public_submit_ingress",
        "transport_public_key_hex": TRANSPORT_KEY,
        "transport_key_scope": "public_submit_ingress",
        "endpoint_uri_hint": "https://example.com/api/v1/truth/submit",
        "tls_cert_sha256_fingerprint": TLS_FINGERPRINT,
        "valid_from_epoch": 0,
        "valid_until_epoch": 0,
        "revocation_policy": {
            "revocation_record_kind": PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND,
            "supersession_required": True,
        },
        "asserted_at_epoch": 0,
        "signing_dst": f"{PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_BLS_DST_PREFIX}:{NETWORK_ID}",
        "bls_public_key_hex": BLS_KEY,
        "bls_signature_hex": SIGNATURE,
    }
    record.update(overrides)
    return record


def _revocation_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "node_kind": PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND,
        "schema_version": PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_SCHEMA_VERSION,
        "network_id": NETWORK_ID,
        "revoked_assertion_sha256": "f" * 64,
        "serving_agent_id": AGENT_ID,
        "revoked_at_epoch": 0,
        "revocation_reason": "superseded by fresh ingress endpoint assertion",
        "supersession_required": True,
        "bls_public_key_hex": BLS_KEY,
        "bls_signature_hex": SIGNATURE,
    }
    record.update(overrides)
    return record


def _valid_envelope(sig: object = "UNSIGNED") -> dict[str, object]:
    return {
        "v": 1,
        "primitive": "assert.truth",
        "agent_id": AGENT_ID,
        "epoch": 0,
        "payload": {
            "content": {"claim": "test claim"},
            "primitive_type": "observation",
            "epistemic_type": "objective",
            "parent_node_ids": [],
        },
        "sig": sig,
    }


def _native_sig_for(envelope_without_sig: dict[str, object], **overrides: object) -> dict[str, object]:
    canonical = json.dumps(
        envelope_without_sig,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    sig: dict[str, object] = {
        "schema_version": "native_submit_sig.v0.1",
        "dst": f"ILC_NATIVE_TRUTH_SUBMIT_V1:{NETWORK_ID}",
        "verifier_profile": "native_submit_sig_profile.v0.1",
        "key_ref": f"agent:{AGENT_ID}",
        "payload_sha256": hashlib.sha256(canonical).hexdigest(),
        "signature_hex": "ab" * 96,
    }
    sig.update(overrides)
    return sig


class IterNodeAtlas:
    def __init__(
        self,
        nodes: list[dict[str, object]],
        edges: list[dict[str, object]] | None = None,
    ) -> None:
        self.nodes = nodes
        self.edges = edges or []

    def iter_nodes(self) -> list[dict[str, object]]:
        return self.nodes

    def iter_edges(self) -> list[dict[str, object]]:
        return self.edges


def _set_native_sig_guard(monkeypatch: pytest.MonkeyPatch, value: bool) -> None:
    monkeypatch.setattr(
        truth_runtime,
        "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED",
        value,
    )


def _assert_submission_token(exc_info: pytest.ExceptionInfo[EpistemicSubmissionError], token: str) -> None:
    assert exc_info.value.token == token


def test_parse_valid_assertion_epoch_zero_valid_until() -> None:
    parsed = parse_endpoint_assertion(_assertion_record())
    assert parsed.valid_until_epoch == 0


def test_parse_assertion_rejects_wrong_transport_key_scope() -> None:
    with pytest.raises(ValueError, match="submit_ingress_assertion_transport_key_scope_invalid_IMPL_00"):
        parse_endpoint_assertion(_assertion_record(transport_key_scope="validator_grpc"))


def test_parse_assertion_rejects_wrong_node_kind() -> None:
    with pytest.raises(ValueError, match="submit_ingress_assertion_node_kind_invalid_IMPL_00"):
        parse_endpoint_assertion(_assertion_record(node_kind="validator_grpc_endpoint_assertion"))


def test_canonical_payload_excludes_signature_but_includes_bls_public_key() -> None:
    payload = json.loads(canonical_endpoint_assertion_payload(_assertion_record()).decode("utf-8"))
    assert "bls_signature_hex" not in payload
    assert payload["bls_public_key_hex"] == BLS_KEY


def test_bls_verifier_receives_canonical_payload_and_network_id() -> None:
    calls: list[tuple[bytes, str, str, str]] = []

    def verifier(payload: bytes, signature_hex: str, public_key_hex: str, network_id: str) -> bool:
        calls.append((payload, signature_hex, public_key_hex, network_id))
        return True

    assert verify_endpoint_assertion_bls_signature(_assertion_record(), verifier=verifier) is True
    assert len(calls) == 1
    assert calls[0][1:] == (SIGNATURE, BLS_KEY, NETWORK_ID)
    assert b"bls_signature_hex" not in calls[0][0]


def test_select_current_raises_when_all_superseded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        endpoint,
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED",
        False,
    )
    first = PublicSubmitIngressEndpointAssertion.from_dict(_assertion_record(revised_by="next-1"))
    second = PublicSubmitIngressEndpointAssertion.from_dict(
        _assertion_record(endpoint_uri_hint="https://example.org/submit", revised_by="next-2")
    )

    with pytest.raises(ValueError, match="submit_ingress_assertion_all_candidates_superseded_IMPL_00"):
        load_from_atlas(
            IterNodeAtlas([first.to_dict(), second.to_dict()]),
            serving_agent_id=AGENT_ID,
            network_id=NETWORK_ID,
        )


def test_select_current_raises_when_multiple_non_superseded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        endpoint,
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED",
        False,
    )
    first = _assertion_record()
    second = _assertion_record(endpoint_uri_hint="https://example.org/submit")

    with pytest.raises(ValueError, match="submit_ingress_assertion_multiple_current_IMPL_00"):
        load_from_atlas(
            IterNodeAtlas([first, second]),
            serving_agent_id=AGENT_ID,
            network_id=NETWORK_ID,
        )


def test_select_current_uses_revision_edge_to_reject_superseded_candidate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        endpoint,
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED",
        False,
    )
    old = PublicSubmitIngressEndpointAssertion.from_dict(_assertion_record())
    new = PublicSubmitIngressEndpointAssertion.from_dict(
        _assertion_record(endpoint_uri_hint="https://example.org/submit")
    )
    edge = {
        "edge_type": "revised_by",
        "source_candidate_id": submit_ingress_assertion_candidate_id(AGENT_ID, NETWORK_ID),
        "source_assertion_sha256": assertion_content_sha256(old),
        "target_assertion_sha256": assertion_content_sha256(new),
    }

    with pytest.raises(ValueError, match="submit_ingress_assertion_all_candidates_superseded_IMPL_00"):
        load_from_atlas(
            IterNodeAtlas([old.to_dict()], [edge]),
            serving_agent_id=AGENT_ID,
            network_id=NETWORK_ID,
        )


def test_guard_raises_before_activation() -> None:
    with pytest.raises(ValueError, match="public_submit_ingress_endpoint_assertion_not_activated_IMPL_00"):
        load_from_atlas(
            IterNodeAtlas([_assertion_record()]),
            serving_agent_id=AGENT_ID,
            network_id=NETWORK_ID,
        )


def test_pre_signer_binding_advisory_trust_annotation_in_docstring() -> None:
    assert "Pre-signer-binding advisory trust" in (endpoint.__doc__ or "")
    assert "serving_agent_id is self-declared" in (endpoint.__doc__ or "")
    source = inspect.getsource(parse_endpoint_assertion)
    assert "serving_agent_id is self-declared" in source
    assert "Phase 1578d deferred signer binding" in source


def test_native_sig_wiring_rejects_unsigned_when_guard_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(_valid_envelope("UNSIGNED"))
    _assert_submission_token(exc_info, "native_submit_sig_unsigned_placeholder_rejected")


def test_native_sig_wiring_rejects_none_sig_when_guard_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    envelope = _valid_envelope()
    envelope.pop("sig")
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(envelope)
    _assert_submission_token(exc_info, "native_submit_sig_unsigned_placeholder_rejected")


def test_native_sig_wiring_rejects_non_object_sig_when_guard_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(_valid_envelope(123))
    _assert_submission_token(exc_info, "native_submit_sig_not_object_IMPL_00")


@pytest.mark.parametrize(
    ("override", "token"),
    (
        ({"schema_version": "wrong"}, "native_submit_sig_schema_version_invalid_IMPL_00"),
        ({"verifier_profile": "wrong"}, "native_submit_sig_verifier_profile_invalid_IMPL_00"),
        ({"dst": "WRONG"}, "native_submit_sig_dst_invalid_IMPL_00"),
        ({"payload_sha256": "not-hex"}, "native_submit_sig_payload_sha256_format_invalid_IMPL_00"),
        ({"signature_hex": "abc"}, "native_submit_sig_signature_hex_invalid_IMPL_00"),
        ({"key_ref": ""}, "native_submit_sig_key_ref_missing_IMPL_00"),
    ),
)
def test_native_sig_wiring_rejects_malformed_sig_fields(
    monkeypatch: pytest.MonkeyPatch,
    override: dict[str, object],
    token: str,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    envelope = _valid_envelope()
    envelope_without_sig = {key: value for key, value in envelope.items() if key != "sig"}
    envelope["sig"] = _native_sig_for(envelope_without_sig, **override)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(envelope)
    _assert_submission_token(exc_info, token)


def test_native_sig_wiring_rejects_payload_sha256_mismatch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    envelope = _valid_envelope()
    envelope_without_sig = {key: value for key, value in envelope.items() if key != "sig"}
    envelope["sig"] = _native_sig_for(envelope_without_sig, payload_sha256="0" * 64)
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime.validate_truth_primitive_submission(envelope)
    _assert_submission_token(exc_info, "native_submit_sig_payload_sha256_mismatch_IMPL_00")


def test_native_sig_wiring_accepts_correct_payload_sha256(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    envelope = _valid_envelope()
    envelope_without_sig = {key: value for key, value in envelope.items() if key != "sig"}
    envelope["sig"] = _native_sig_for(envelope_without_sig)
    result = truth_runtime.validate_truth_primitive_submission(envelope)
    assert result.primitive == "assert.truth"


def test_outer_envelope_rejects_dict_sig_while_guard_is_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, True)
    envelope = _valid_envelope({"schema_version": "native_submit_sig.v0.1"})
    with pytest.raises(EpistemicSubmissionError) as exc_info:
        truth_runtime._validate_outer_envelope(envelope)
    _assert_submission_token(exc_info, "sig_invalid_pre_native_ingress_activation")


def test_outer_envelope_allows_dict_sig_while_guard_is_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _set_native_sig_guard(monkeypatch, False)
    envelope = _valid_envelope({"schema_version": "native_submit_sig.v0.1"})
    assert truth_runtime._validate_outer_envelope(envelope) == envelope


def test_revocation_schema_parses_valid_record() -> None:
    parsed = parse_endpoint_revocation(_revocation_record())
    assert parsed.node_kind == PUBLIC_SUBMIT_INGRESS_ENDPOINT_REVOCATION_NODE_KIND


def test_revocation_schema_requires_supersession_required_true() -> None:
    with pytest.raises(ValueError, match="submit_ingress_revocation_supersession_required_invalid_IMPL_00"):
        parse_endpoint_revocation(_revocation_record(supersession_required=False))


def test_revocation_canonical_payload_excludes_signature() -> None:
    payload = json.loads(canonical_revocation_payload(_revocation_record()).decode("utf-8"))
    assert "bls_signature_hex" not in payload
    assert payload["bls_public_key_hex"] == BLS_KEY
