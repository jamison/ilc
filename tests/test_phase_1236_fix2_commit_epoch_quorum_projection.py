from __future__ import annotations

import inspect
import re
from decimal import Decimal

import pytest

from ilc_core.protocol.commit_epoch_emission_runtime import (
    COMMIT_EPOCH_QUORUM_PROJECTION_VERSION,
    build_commit_epoch_event,
    build_quorum_proof_projection,
    compute_quorum_proof_ref,
)

STATE_DIGEST = "a" * 64
EVENTS_DIGEST = "b" * 64


def _projection(**overrides: object) -> dict[str, object]:
    kwargs = {
        "epoch_sequence": 12,
        "state_root_cidv1_hex": "ab" * 36,
        "signers": [2, 0, 1],
        "agg_sig_bytes_hex": "cd" * 96,
        "source_record_digest": "sha256:" + "ef" * 32,
    }
    kwargs.update(overrides)
    return build_quorum_proof_projection(**kwargs)


def test_builder_returns_expected_field_set():
    projection = _projection()

    assert projection == {
        "agg_sig_bytes_hex": "cd" * 96,
        "epoch_sequence": 12,
        "signers": [0, 1, 2],
        "source_record_digest": "sha256:" + "ef" * 32,
        "state_root_cidv1_hex": "ab" * 36,
    }


def test_signers_are_sorted_ascending():
    projection = _projection(signers=[9, 3, 7, 0])

    assert projection["signers"] == [0, 3, 7, 9]


def test_duplicate_signers_raise_value_error():
    with pytest.raises(ValueError, match="quorum_projection_signers_must_be_unique"):
        _projection(signers=[0, 1, 1])


def test_empty_signers_raise_value_error():
    with pytest.raises(ValueError, match="quorum_projection_signers_must_be_non_empty"):
        _projection(signers=[])


def test_negative_signer_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_signer_must_be_non_negative_int"):
        _projection(signers=[0, -1])


def test_non_integer_signer_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_signer_must_be_non_negative_int"):
        _projection(signers=[0, "1"])


def test_signer_above_u32_max_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_signer_must_be_non_negative_int"):
        _projection(signers=[0, 2**32])


def test_non_hex_state_root_cidv1_hex_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_state_root_cidv1_hex_invalid"):
        _projection(state_root_cidv1_hex="not-hex")


def test_non_hex_agg_sig_bytes_hex_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_agg_sig_bytes_hex_invalid"):
        _projection(agg_sig_bytes_hex="not-hex")


def test_wrong_length_agg_sig_bytes_hex_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_agg_sig_bytes_hex_invalid"):
        _projection(agg_sig_bytes_hex="cd" * 95)


def test_bad_source_record_digest_raises_value_error():
    with pytest.raises(ValueError, match="quorum_projection_source_record_digest_invalid"):
        _projection(source_record_digest="ef" * 32)


def test_source_record_digest_none_is_accepted():
    projection = _projection(source_record_digest=None)

    assert projection["source_record_digest"] is None


def test_compute_quorum_proof_ref_is_deterministic_for_equivalent_inputs():
    first = _projection(signers=[2, 0, 1])
    second = _projection(signers=[1, 2, 0])

    assert first == second
    assert compute_quorum_proof_ref(first) == compute_quorum_proof_ref(second)


def test_quorum_proof_ref_has_sha256_shape():
    ref = compute_quorum_proof_ref(_projection())

    assert re.fullmatch(r"sha256:[0-9a-f]{64}", ref)


def test_builder_rejects_uppercase_hex():
    with pytest.raises(ValueError, match="quorum_projection_state_root_cidv1_hex_invalid"):
        _projection(state_root_cidv1_hex="AB" * 36)


def test_existing_phase_1236_build_commit_epoch_event_behavior_remains_unchanged():
    event = build_commit_epoch_event(
        epoch_index=12,
        epoch_id="epoch-0012",
        namespace_id="ilc:test",
        finalization_state="committed",
        quorum_records=[
            {
                "block_hash": "block-alpha",
                "epoch_index": 12,
                "quorum_state_digest": "quorum-state-alpha",
                "vote_weight": 1,
            }
        ],
        epoch_state_digest=STATE_DIGEST,
        epoch_events_digest=EVENTS_DIGEST,
        reward_total=Decimal("10"),
        stake_total=Decimal("20"),
        task_count=3,
        agent_count=2,
    )

    assert event.kind == "commit.epoch"
    assert event.payload["checksums"]["epoch_state_cid"] == "sha256:" + STATE_DIGEST


def test_version_token_present():
    assert COMMIT_EPOCH_QUORUM_PROJECTION_VERSION == "commit_epoch_quorum_projection_1236_fix2.v0.1"


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
