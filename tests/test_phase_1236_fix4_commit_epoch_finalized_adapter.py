from __future__ import annotations

import inspect
from decimal import Decimal

import pytest

from ilc_core.protocol.commit_epoch_emission_runtime import (
    COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION,
    adapt_finalized_epoch_to_connector_inputs,
    build_commit_epoch_causal_frontier_projection,
    build_quorum_proof_projection,
    compute_quorum_proof_ref,
)
from ilc_core.protocol.event_log import ProtocolEvent

GENESIS_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
STATE_ROOT = "ab" * 36
AGG_SIG = "cd" * 96
SOURCE_DIGEST = "sha256:" + "ef" * 32
PREDECESSOR_REF = "sha256:" + "a1" * 32


def _quorum_records(finalization_state: str = "committed") -> list[dict[str, object]]:
    return [
        {
            "block_hash": "block-alpha",
            "epoch_index": 12,
            "finalization_state": finalization_state,
            "quorum_state_digest": "quorum-state-alpha",
            "vote_weight": 1,
        }
    ]


def _adapter(**overrides: object) -> dict[str, object]:
    quorum_ref = compute_quorum_proof_ref(
        build_quorum_proof_projection(
            epoch_sequence=12,
            state_root_cidv1_hex=STATE_ROOT,
            signers=[2, 0, 1],
            agg_sig_bytes_hex=AGG_SIG,
            source_record_digest=SOURCE_DIGEST,
        )
    )
    kwargs = {
        "epoch_index": 12,
        "epoch_id": "epoch-0012",
        "namespace_id": "ilc:test",
        "finalization_state": "committed",
        "quorum_records": _quorum_records(),
        "state_root_cidv1_hex": STATE_ROOT,
        "agg_sig_bytes_hex": AGG_SIG,
        "signers": [2, 0, 1],
        "source_record_digest": SOURCE_DIGEST,
        "causal_predecessor_ref": PREDECESSOR_REF,
        "causal_frontier_refs": [quorum_ref],
        "genesis_domain_hash": GENESIS_HASH,
        "reward_total": Decimal("10.50"),
        "stake_total": Decimal("20"),
        "task_count": 3,
        "agent_count": 2,
    }
    kwargs.update(overrides)
    return adapt_finalized_epoch_to_connector_inputs(**kwargs)


def test_adapter_composes_quorum_causal_frontier_and_event_layers():
    result = _adapter()

    assert result["adapter_version"] == COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION
    assert result["quorum_proof_projection"]["signers"] == [0, 1, 2]
    assert result["causal_frontier_projection"]["quorum_proof_ref"] == result["quorum_proof_ref"]
    assert isinstance(result["commit_epoch_event"], ProtocolEvent)
    assert result["commit_epoch_event"].kind == "commit.epoch"


def test_adapter_event_checksums_are_projection_refs():
    result = _adapter()
    event = result["commit_epoch_event"]

    assert event.payload["checksums"]["epoch_state_cid"] == result["causal_frontier_ref"]
    assert event.payload["checksums"]["epoch_events_cid"] == result["quorum_proof_ref"]


def test_state_root_cidv1_hex_length_enforced_in_quorum_projection():
    with pytest.raises(ValueError, match="quorum_projection_state_root_cidv1_hex_invalid"):
        build_quorum_proof_projection(
            epoch_sequence=12,
            state_root_cidv1_hex="ab",
            signers=[0, 1],
            agg_sig_bytes_hex=AGG_SIG,
        )


def test_state_root_cidv1_hex_length_enforced_in_causal_frontier_projection():
    with pytest.raises(ValueError, match="causal_frontier_state_root_cidv1_hex_invalid"):
        build_commit_epoch_causal_frontier_projection(
            epoch_sequence=12,
            state_root_cidv1_hex="ab",
            causal_predecessor_ref=PREDECESSOR_REF,
            quorum_proof_ref="sha256:" + "b2" * 32,
            causal_frontier_refs=["sha256:" + "b2" * 32],
            genesis_domain_hash=GENESIS_HASH,
        )


def test_adapter_rejects_empty_quorum_records_for_post_genesis_epoch():
    with pytest.raises(ValueError, match="finalized_epoch_adapter_quorum_records_empty"):
        _adapter(quorum_records=[])


def test_adapter_rejects_missing_causal_predecessor_for_post_genesis_epoch():
    with pytest.raises(ValueError, match="causal_frontier_predecessor_ref_invalid"):
        _adapter(causal_predecessor_ref=None)


def test_adapter_rejects_frontier_refs_without_computed_quorum_ref():
    with pytest.raises(ValueError, match="finalized_epoch_adapter_quorum_proof_ref_missing_from_frontier"):
        _adapter(causal_frontier_refs=["sha256:" + "b2" * 32])


def test_adapter_rejects_conflicting_finalization_state_in_quorum_record():
    with pytest.raises(ValueError, match="finalized_epoch_adapter_conflicting_finalization_state"):
        _adapter(quorum_records=_quorum_records(finalization_state="rolled_back"))


def test_adapter_rejects_quorum_record_epoch_mismatch():
    bad_record = _quorum_records()
    bad_record[0]["epoch_index"] = 11

    with pytest.raises(ValueError, match="quorum_record_epoch_index_mismatch"):
        _adapter(quorum_records=bad_record)


def test_adapter_rejects_float_reward_total():
    with pytest.raises(ValueError, match="reward_total_must_be_non_negative_finite_decimal"):
        _adapter(reward_total=1.5)


def test_adapter_rejects_missing_rust_state_root_material():
    with pytest.raises(ValueError, match="quorum_projection_state_root_cidv1_hex_invalid"):
        _adapter(state_root_cidv1_hex=None)


def test_adapter_rejects_bad_signers_through_projection_layer():
    with pytest.raises(ValueError, match="quorum_projection_signers_must_be_unique"):
        _adapter(signers=[0, 0])


def test_adapter_rejects_genesis_epoch_zero():
    with pytest.raises(ValueError, match="finalized_epoch_adapter_genesis_epoch_zero_unsupported"):
        _adapter(epoch_index=0)


def test_version_token_present():
    assert COMMIT_EPOCH_FINALIZED_ADAPTER_VERSION == "commit_epoch_finalized_adapter_1236_fix4.v0.1"


def test_module_does_not_use_wall_clock_random_io_network_or_legacy_constructor():
    import ilc_core.protocol.commit_epoch_emission_runtime as runtime

    source = inspect.getsource(runtime)
    assert "datetime.now" not in source
    assert "time.time" not in source
    assert "import random" not in source
    assert "random." not in source
    assert ".open(" not in source
    assert "requests" not in source
    assert "make_commit_epoch_event" not in source
