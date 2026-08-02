from __future__ import annotations

import hashlib
import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from ilc_core.consensus import (
    SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
    ConsensusBridgeConfig,
    build_epoch_settlement_proposal_submission,
    spectral_hash_bytes_from_eigenvalues,
    submit_ecu_transfer_via_quic,
)


ROOT = Path(__file__).resolve().parents[1]
TYPES_RS = ROOT / "ilc_consensus/src/types.rs"
NETWORK_RS = ROOT / "ilc_consensus/src/network.rs"
NODE_RS = ROOT / "ilc_consensus/src/node.rs"
APP_INTERFACE_RS = ROOT / "ilc_consensus/src/app_interface.rs"
PROTO = ROOT / "ilc_consensus/proto/ilc_app.proto"
BRIDGE = ROOT / "ilc_core/consensus/production_bridge.py"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
CDL_RATIFICATION = (
    ROOT
    / "docs/specs/ilc_cdl_104_spectral_hash_epoch_commitment_ratification_1582_v0.1.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1582_gap_spectral_01b_cdl104_ratification_rust_impl_walkthrough.md"
)


SPECTRAL_HASH = bytes(range(32))
STATE_ROOT = bytes([7]) * 36
SUBMITTER = bytes([3]) * 48
SETTLEMENT_RECORD = b'{"epoch":1,"root":"canonical"}'


class RecordingRpc:
    def __init__(self, response: object) -> None:
        self.response = response
        self.calls: list[tuple[object, int]] = []

    def __call__(self, request: object, *, timeout: int) -> object:
        self.calls.append((request, timeout))
        return self.response


class FakeProposalStub:
    def __init__(self, response: object) -> None:
        self.SubmitEpochProposal = RecordingRpc(response)


def _struct_body(path: Path, struct_name: str) -> str:
    text = path.read_text()
    match = re.search(rf"pub struct {struct_name} \{{(?P<body>.*?)\n\}}", text, re.S)
    assert match, f"{struct_name} not found in {path}"
    return match.group("body")


def test_epoch_settlement_record_has_cdl104_spectral_hash_field() -> None:
    body = _struct_body(TYPES_RS, "EpochSettlementRecord")
    assert "pub spectral_hash: [u8; 32]," in body
    assert body.index("pub state_root") < body.index("pub spectral_hash")
    assert body.index("pub spectral_hash") < body.index("pub proposal_commitment_sha256")


def test_epoch_proposal_and_grpc_request_carry_spectral_hash() -> None:
    proposal_body = _struct_body(NETWORK_RS, "EpochProposal")
    proto = PROTO.read_text()
    app_interface = APP_INTERFACE_RS.read_text()
    bridge = BRIDGE.read_text()

    assert "pub spectral_hash: [u8; 32]," in proposal_body
    assert "bytes  spectral_hash           = 9;" in proto
    assert "submit_epoch_proposal_invalid_spectral_hash_phase_1582" in app_interface
    assert '("spectral_hash", 9, descriptor_pb2.FieldDescriptorProto.TYPE_BYTES)' in bridge


def test_proposal_commitment_preimage_binds_spectral_hash_before_epoch_data() -> None:
    node = NODE_RS.read_text()
    rust_order = [
        "hasher.update(cid_root_bytes(&proposal.state_root));",
        "hasher.update(proposal.spectral_hash);",
        "hasher.update(&proposal.epoch_data_hash);",
    ]
    bridge = BRIDGE.read_text()
    python_order = [
        "state_root_cidv1,",
        "spectral_hash,",
        "epoch_data_hash,",
    ]
    for first, second in zip(rust_order, rust_order[1:]):
        assert node.index(first) < node.index(second)
    for first, second in zip(python_order, python_order[1:]):
        assert bridge.index(first) < bridge.index(second)


def test_spectral_hash_helper_returns_nonzero_32_bytes() -> None:
    digest = spectral_hash_bytes_from_eigenvalues([0.0, 0.125, 0.5, 1.0])
    assert isinstance(digest, bytes)
    assert len(digest) == 32
    assert digest != bytes(32)


def test_bridge_rejects_malformed_spectral_hash() -> None:
    with pytest.raises(
        ValueError,
        match="submit_epoch_proposal_spectral_hash_invalid_phase_1582",
    ):
        build_epoch_settlement_proposal_submission(
            submitter_agent_id=SUBMITTER,
            epoch_number=1,
            state_root_cidv1=STATE_ROOT,
            spectral_hash=b"short",
            settlement_record_bytes=SETTLEMENT_RECORD,
            not_before_unix_ms=123456789,
            network_id="ilc-mainnet-rc01",
        )


def test_bridge_idempotency_key_changes_with_spectral_hash() -> None:
    base = build_epoch_settlement_proposal_submission(
        submitter_agent_id=SUBMITTER,
        epoch_number=1,
        state_root_cidv1=STATE_ROOT,
        spectral_hash=SPECTRAL_HASH,
        settlement_record_bytes=SETTLEMENT_RECORD,
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )
    changed = build_epoch_settlement_proposal_submission(
        submitter_agent_id=SUBMITTER,
        epoch_number=1,
        state_root_cidv1=STATE_ROOT,
        spectral_hash=bytes(reversed(SPECTRAL_HASH)),
        settlement_record_bytes=SETTLEMENT_RECORD,
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )
    assert base.idempotency_key != changed.idempotency_key


def test_bridge_submit_request_includes_spectral_hash() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=SUBMITTER,
        epoch_number=1,
        state_root_cidv1=STATE_ROOT,
        spectral_hash=SPECTRAL_HASH,
        settlement_record_bytes=SETTLEMENT_RECORD,
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )
    fake_stub = FakeProposalStub(
        SimpleNamespace(
            status_token=SUBMIT_EPOCH_PROPOSAL_ACCEPTED_TOKEN,
            error_code="",
            accepted_epoch_number=1,
            accepted_state_root_cidv1=STATE_ROOT,
            proposal_id=submission.idempotency_key,
        )
    )

    submit_ecu_transfer_via_quic(
        submission,
        config=ConsensusBridgeConfig(target="validator.example:443"),
        stub=fake_stub,
    )

    request, _timeout = fake_stub.SubmitEpochProposal.calls[0]
    assert request.spectral_hash == SPECTRAL_HASH


def test_readback_response_exposes_spectral_hash() -> None:
    proto = PROTO.read_text()
    bridge = BRIDGE.read_text()
    app_interface = APP_INTERFACE_RS.read_text()

    assert "bytes  spectral_hash = 5;" in proto
    assert "spectral_hash: stored.record.spectral_hash.to_vec()" in app_interface
    assert "spectral_hash=_require_exact_bytes" in bridge


def test_cdl104_ratification_register_status_and_walkthrough_tokens() -> None:
    ratification = CDL_RATIFICATION.read_text()
    register = CDL_REGISTER.read_text()
    status = STATUS.read_text()
    walkthrough = WALKTHROUGH.read_text()

    assert "CDL-104" in ratification
    assert "spectral_hash: [u8; 32]" in ratification
    assert "spectral_hash_fixed_point_int64_le" in ratification
    assert "ratified" in register
    assert "cdl_104_ratified_phase_1582" in register
    assert "spectral_hash_rust_field_committed_phase_1582" in status
    assert "cdl_104_ratified_phase_1582" in status
    assert "GO Phase 1582 GAP-SPECTRAL-01b CDL-104-RATIFY" in walkthrough


def test_ccss_spectral_namespace_does_not_replace_cdl104_epoch_field() -> None:
    consensus_text = "\n".join(path.read_text() for path in ROOT.glob("ilc_consensus/src/*.rs"))
    assert "SpectralRouteToken" not in consensus_text
    assert "ccss" not in TYPES_RS.read_text().lower()


def test_known_golden_idempotency_vector_binds_spectral_hash() -> None:
    submission = build_epoch_settlement_proposal_submission(
        submitter_agent_id=SUBMITTER,
        epoch_number=1,
        state_root_cidv1=STATE_ROOT,
        spectral_hash=SPECTRAL_HASH,
        settlement_record_bytes=SETTLEMENT_RECORD,
        not_before_unix_ms=123456789,
        network_id="ilc-mainnet-rc01",
    )
    assert hashlib.sha256(SETTLEMENT_RECORD).hexdigest() == (
        "d9bb4e98479cdabbd9acce0b9df6fe1941d78666190038d83082a60ff4789aaf"
    )
    assert submission.idempotency_key == (
        "22133479c10086745f1dc90e159906696541a4720a8c604c6b472f8a71f95be7"
    )
