from __future__ import annotations

import inspect
import re

import pytest

from ilc_core.protocol.commit_epoch_emission_runtime import (
    COMMIT_EPOCH_CAUSAL_FRONTIER_PROJECTION_VERSION,
    COMMIT_EPOCH_CAUSAL_FRONTIER_SCHEMA_VERSION,
    COMMIT_EPOCH_ISSUER,
    COMMIT_EPOCH_TIMESTAMP_POLICY,
    build_commit_epoch_causal_frontier_projection,
    build_quorum_proof_projection,
    compute_causal_frontier_ref,
    compute_quorum_proof_ref,
)

GENESIS_HASH = "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
SHA_REF_A = "sha256:" + "a1" * 32
SHA_REF_B = "sha256:" + "b2" * 32
STATE_ROOT = "ab" * 36


def _genesis_projection(**overrides: object) -> dict[str, object]:
    kwargs = {
        "epoch_sequence": 0,
        "state_root_cidv1_hex": None,
        "causal_predecessor_ref": None,
        "quorum_proof_ref": None,
        "causal_frontier_refs": [f"genesis_root:{GENESIS_HASH}"],
        "genesis_domain_hash": GENESIS_HASH,
    }
    kwargs.update(overrides)
    return build_commit_epoch_causal_frontier_projection(**kwargs)


def _post_genesis_projection(**overrides: object) -> dict[str, object]:
    kwargs = {
        "epoch_sequence": 12,
        "state_root_cidv1_hex": STATE_ROOT,
        "causal_predecessor_ref": SHA_REF_A,
        "quorum_proof_ref": SHA_REF_B,
        "causal_frontier_refs": [SHA_REF_B],
        "genesis_domain_hash": GENESIS_HASH,
    }
    kwargs.update(overrides)
    return build_commit_epoch_causal_frontier_projection(**kwargs)


def test_genesis_epoch_zero_projection_returns_exact_phase_1226_fields():
    projection = _genesis_projection()

    assert projection == {
        "causal_frontier_refs": [f"genesis_root:{GENESIS_HASH}"],
        "causal_predecessor_ref": None,
        "epoch_sequence": 0,
        "event_kind": "commit.epoch",
        "genesis_domain_hash": GENESIS_HASH,
        "issuer": "consensus_layer",
        "quorum_proof_ref": None,
        "schema_version": "commit_epoch_causal_frontier_mapping_1226.v0.1",
        "state_root_cidv1_hex": None,
        "timestamp_policy": "epoch_sequence_only_no_wall_clock",
    }


def test_genesis_epoch_zero_requires_nullable_refs_to_be_none():
    with pytest.raises(ValueError, match="causal_frontier_genesis_state_root_must_be_null"):
        _genesis_projection(state_root_cidv1_hex=STATE_ROOT)
    with pytest.raises(ValueError, match="causal_frontier_genesis_predecessor_must_be_null"):
        _genesis_projection(causal_predecessor_ref=SHA_REF_A)
    with pytest.raises(ValueError, match="causal_frontier_genesis_quorum_proof_must_be_null"):
        _genesis_projection(quorum_proof_ref=SHA_REF_B)


def test_genesis_epoch_zero_requires_frontier_refs_equal_domain_anchor():
    with pytest.raises(ValueError, match="causal_frontier_refs_genesis_must_equal_domain_anchor"):
        _genesis_projection(causal_frontier_refs=[SHA_REF_A])


def test_post_genesis_projection_returns_exact_phase_1226_fields():
    projection = _post_genesis_projection()

    assert projection == {
        "causal_frontier_refs": [SHA_REF_B],
        "causal_predecessor_ref": SHA_REF_A,
        "epoch_sequence": 12,
        "event_kind": "commit.epoch",
        "genesis_domain_hash": GENESIS_HASH,
        "issuer": "consensus_layer",
        "quorum_proof_ref": SHA_REF_B,
        "schema_version": "commit_epoch_causal_frontier_mapping_1226.v0.1",
        "state_root_cidv1_hex": STATE_ROOT,
        "timestamp_policy": "epoch_sequence_only_no_wall_clock",
    }


def test_post_genesis_missing_state_root_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_state_root_required"):
        _post_genesis_projection(state_root_cidv1_hex=None)


def test_post_genesis_missing_causal_predecessor_ref_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_predecessor_ref_invalid"):
        _post_genesis_projection(causal_predecessor_ref=None)


def test_post_genesis_missing_quorum_proof_ref_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_quorum_proof_ref_invalid"):
        _post_genesis_projection(quorum_proof_ref=None)


def test_bad_genesis_domain_hash_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_genesis_domain_hash_invalid"):
        _post_genesis_projection(genesis_domain_hash="abc")


def test_bad_causal_predecessor_ref_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_predecessor_ref_invalid"):
        _post_genesis_projection(causal_predecessor_ref="sha256:abc")


def test_bad_quorum_proof_ref_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_quorum_proof_ref_invalid"):
        _post_genesis_projection(quorum_proof_ref="not-a-sha-ref")


def test_bad_post_genesis_causal_frontier_ref_raises_value_error():
    with pytest.raises(ValueError, match="causal_frontier_ref_invalid"):
        _post_genesis_projection(causal_frontier_refs=["sha256:abc"])


def test_compute_causal_frontier_ref_is_deterministic():
    first = _post_genesis_projection(causal_frontier_refs=[SHA_REF_B, SHA_REF_A])
    second = _post_genesis_projection(causal_frontier_refs=[SHA_REF_B, SHA_REF_A])

    assert compute_causal_frontier_ref(first) == compute_causal_frontier_ref(second)


def test_causal_frontier_ref_has_sha256_shape():
    ref = compute_causal_frontier_ref(_post_genesis_projection())

    assert re.fullmatch(r"sha256:[0-9a-f]{64}", ref)


def test_epoch_sequence_bool_is_rejected():
    with pytest.raises(ValueError, match="causal_frontier_epoch_sequence_must_be_non_negative_int"):
        _post_genesis_projection(epoch_sequence=True)


def test_uppercase_hex_is_rejected():
    with pytest.raises(ValueError, match="causal_frontier_state_root_cidv1_hex_invalid"):
        _post_genesis_projection(state_root_cidv1_hex="AB" * 36)


def test_existing_fix2_quorum_projection_behavior_remains_unchanged():
    quorum_projection = build_quorum_proof_projection(
        epoch_sequence=12,
        state_root_cidv1_hex=STATE_ROOT,
        signers=[2, 0, 1],
        agg_sig_bytes_hex="cd" * 96,
        source_record_digest="sha256:" + "ef" * 32,
    )

    assert quorum_projection["signers"] == [0, 1, 2]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", compute_quorum_proof_ref(quorum_projection))


def test_version_and_constant_tokens_present():
    assert COMMIT_EPOCH_CAUSAL_FRONTIER_PROJECTION_VERSION == (
        "commit_epoch_causal_frontier_projection_1236_fix3.v0.1"
    )
    assert COMMIT_EPOCH_CAUSAL_FRONTIER_SCHEMA_VERSION == "commit_epoch_causal_frontier_mapping_1226.v0.1"
    assert COMMIT_EPOCH_TIMESTAMP_POLICY == "epoch_sequence_only_no_wall_clock"
    assert COMMIT_EPOCH_ISSUER == "consensus_layer"


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
