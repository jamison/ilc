from __future__ import annotations

import hashlib
import json
import sys
from types import SimpleNamespace

import pytest

from ilc_core.consensus.production_bridge import (
    MAX_PROPOSAL_GRPC_OVERHEAD_BYTES,
    SUBMIT_ATTRIBUTION_BATCH_ACCEPTED_TOKEN,
    AttributionBatchSubmission,
    ConsensusBridgeConfig,
    build_attribution_batch_submission,
    build_secure_grpc_attribution_ingress_stub,
    submit_attribution_batch_via_grpc,
)


AGENT_ID_BYTES = bytes.fromhex("a" * 96)
BACKWARD_ROOT = "b" * 64


class RecordingRpc:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[object, int]] = []

    def __call__(self, request: object, *, timeout: int) -> object:
        self.calls.append((request, timeout))
        return self.response


class FakeAttributionStub:
    def __init__(self, response: object) -> None:
        self.SubmitAttributionBatch = RecordingRpc(response)


def _batch(root: str = BACKWARD_ROOT) -> dict[str, object]:
    return {
        "attributions": [],
        "backward_attribution_batch_root": root,
        "backward_attribution_entries": [
            {
                "credit_amount": "0.05",
                "event_id": "event-1",
                "recipient_agent_id": "c" * 96,
                "upstream_artifact_id": "artifact-1",
            }
        ],
        "epoch": 7,
    }


def _response(
    *,
    status_token: str = SUBMIT_ATTRIBUTION_BATCH_ACCEPTED_TOKEN,
    accepted_epoch_number: int = 7,
    accepted_backward_root: str = BACKWARD_ROOT,
    error_code: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(
        accepted_backward_root=accepted_backward_root,
        accepted_epoch_number=accepted_epoch_number,
        error_code=error_code,
        status_token=status_token,
    )


def _config(**kwargs: object) -> ConsensusBridgeConfig:
    return ConsensusBridgeConfig(
        target="read.example:443",
        grpc_timeout_seconds=11,
        proposal_client_private_key=b"client-key",
        proposal_client_certificate_chain=b"client-cert",
        proposal_tls_root_certificates=b"proposal-root-ca",
        **kwargs,
    )


def test_build_attribution_batch_submission_hashes_canonical_entries() -> None:
    batch = _batch()

    submission = build_attribution_batch_submission(
        batch,
        submitter_agent_id=AGENT_ID_BYTES,
        not_before_unix_ms=123,
        network_id="ilc-rc01",
    )

    expected_entries_hash = hashlib.sha256(
        json.dumps(
            {"entries": batch["backward_attribution_entries"]},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8"),
    ).digest()
    expected_key = hashlib.sha256(
        f"attribution:7:ilc-rc01:{BACKWARD_ROOT}".encode("utf-8"),
    ).hexdigest()
    assert submission == AttributionBatchSubmission(
        submitter_agent_id=AGENT_ID_BYTES,
        epoch_number=7,
        backward_attribution_batch_root=BACKWARD_ROOT,
        attribution_entries_hash=expected_entries_hash,
        idempotency_key=expected_key,
        not_before_unix_ms=123,
        network_id="ilc-rc01",
        production_bridge_active=True,
        activation_token="production_bridge_activated_phase_1587",
    )


def test_build_attribution_batch_submission_rejects_bad_payloads() -> None:
    with pytest.raises(ValueError, match="submit_attribution_batch_backward_root_invalid"):
        build_attribution_batch_submission(
            _batch("B" * 64),
            submitter_agent_id=AGENT_ID_BYTES,
            not_before_unix_ms=0,
            network_id="ilc-rc01",
        )
    with pytest.raises(ValueError, match="submit_attribution_batch_entries_invalid"):
        build_attribution_batch_submission(
            {"epoch": 1, "backward_attribution_batch_root": BACKWARD_ROOT},
            submitter_agent_id=AGENT_ID_BYTES,
            not_before_unix_ms=0,
            network_id="ilc-rc01",
        )
    with pytest.raises(ValueError, match="submit_attribution_batch_idempotency_preimage"):
        build_attribution_batch_submission(
            _batch(),
            submitter_agent_id=AGENT_ID_BYTES,
            not_before_unix_ms=0,
            network_id="ilc-rc01",
            idempotency_key="d" * 64,
        )


def test_submit_attribution_batch_via_grpc_sends_exact_request_fields() -> None:
    submission = build_attribution_batch_submission(
        _batch(),
        submitter_agent_id=AGENT_ID_BYTES,
        not_before_unix_ms=123,
        network_id="ilc-rc01",
    )
    stub = FakeAttributionStub(_response())

    result = submit_attribution_batch_via_grpc(
        submission,
        config=_config(),
        stub=stub,
    )

    request, timeout = stub.SubmitAttributionBatch.calls[0]
    assert timeout == 11
    assert request.epoch_number == 7
    assert request.submitter_agent_id == AGENT_ID_BYTES
    assert request.backward_attribution_batch_root == BACKWARD_ROOT
    assert request.idempotency_key == submission.idempotency_key
    assert request.network_id == "ilc-rc01"
    assert request.not_before_unix_ms == 123
    assert request.attribution_entries_hash == submission.attribution_entries_hash
    assert result.status_token == SUBMIT_ATTRIBUTION_BATCH_ACCEPTED_TOKEN
    assert result.accepted_epoch_number == 7
    assert result.accepted_backward_root == BACKWARD_ROOT
    assert result.production_bridge_active is True


def test_submit_attribution_batch_via_grpc_rejects_error_and_mismatched_echo() -> None:
    submission = build_attribution_batch_submission(
        _batch(),
        submitter_agent_id=AGENT_ID_BYTES,
        not_before_unix_ms=0,
        network_id="ilc-rc01",
    )

    with pytest.raises(ValueError, match="submit_attribution_batch_rejected"):
        submit_attribution_batch_via_grpc(
            submission,
            config=_config(),
            stub=FakeAttributionStub(_response(error_code="submit_attribution_batch_rejected")),
        )
    with pytest.raises(ValueError, match="submit_attribution_batch_accepted_epoch_mismatch"):
        submit_attribution_batch_via_grpc(
            submission,
            config=_config(),
            stub=FakeAttributionStub(_response(accepted_epoch_number=8)),
        )
    with pytest.raises(ValueError, match="submit_attribution_batch_accepted_root_mismatch"):
        submit_attribution_batch_via_grpc(
            submission,
            config=_config(),
            stub=FakeAttributionStub(_response(accepted_backward_root="c" * 64)),
        )


def test_secure_grpc_attribution_stub_uses_mtls_and_attribution_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: dict[str, object] = {}

    class FakeChannel:
        def unary_unary(self, path: str, **kwargs: object) -> RecordingRpc:
            calls["path"] = path
            assert "request_serializer" in kwargs
            assert "response_deserializer" in kwargs
            return RecordingRpc(SimpleNamespace())

    class FakeGrpcModule:
        @staticmethod
        def ssl_channel_credentials(
            root_certificates: bytes | None = None,
            private_key: bytes | None = None,
            certificate_chain: bytes | None = None,
        ) -> str:
            calls["roots"] = root_certificates
            calls["private_key"] = private_key
            calls["certificate_chain"] = certificate_chain
            return "attribution-tls-creds"

        @staticmethod
        def secure_channel(
            target: str,
            credentials: str,
            options: tuple[tuple[str, int], ...] = (),
        ) -> FakeChannel:
            calls["target"] = target
            calls["credentials"] = credentials
            calls["options"] = options
            return FakeChannel()

    monkeypatch.setitem(sys.modules, "grpc", FakeGrpcModule)
    with pytest.raises(
        ValueError,
        match="proposal_client_certificate_pair_required_phase_1587_fix1",
    ):
        build_secure_grpc_attribution_ingress_stub(
            ConsensusBridgeConfig(
                target="read.example:443",
                attribution_ingress_endpoint="attr.example:443",
            ),
        )

    stub = build_secure_grpc_attribution_ingress_stub(
        _config(attribution_ingress_endpoint="attr.example:443"),
    )

    assert stub.SubmitAttributionBatch is not None
    assert calls["roots"] == b"proposal-root-ca"
    assert calls["private_key"] == b"client-key"
    assert calls["certificate_chain"] == b"client-cert"
    assert calls["target"] == "attr.example:443"
    assert calls["credentials"] == "attribution-tls-creds"
    assert (
        "grpc.max_send_message_length",
        MAX_PROPOSAL_GRPC_OVERHEAD_BYTES + 1024,
    ) in calls["options"]
    assert ("grpc.max_receive_message_length", 1_048_576) in calls["options"]
    assert calls["path"] == "/ilc_app.ILCAppAttributionIngressService/SubmitAttributionBatch"
    assert not hasattr(FakeGrpcModule, "insecure_channel")
