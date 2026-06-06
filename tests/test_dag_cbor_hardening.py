"""DAG-CBOR decoder and encoder hardening tests.

Covers:
- Recursion depth limit (recursion bomb prevention)
- OOB negative integer rejection in decoder
- Float rejection in validate_ilc_object_encodable
- Layer 2/3 builder CIDv1 format validation

PUBLIC_RC_EXCLUDE: dag_cbor_hardening_selftest
PUBLIC_RC_EXCLUDE_REASON: Internal hardening tests. Not a public RC artifact.
"""

from __future__ import annotations

import struct

import pytest

from ilc_core.encoding.dag_cbor import (
    _MAX_NESTING_DEPTH,
    decode_dag_cbor,
    encode_dag_cbor,
    validate_canonical_ilc_dag_cbor,
    validate_ilc_object_encodable,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nested_array_cbor(depth: int) -> bytes:
    """Build b'\\x81' * depth + b'\\xf6' — depth-nested single-element arrays
    wrapping a null. Each \\x81 = CBOR array of length 1 (major 4, additional 1)."""
    return b"\x81" * depth + b"\xf6"


def _oob_negative_cbor() -> bytes:
    """Encode CBOR negative integer -2^64 (out of signed 64-bit range).

    CBOR negative: major type 1, additional 27 (8-byte extended), value 0xffffffffffffffff
    which decodes as -1 - 2^64-1 = -2^64, below the -(2^63) floor.
    """
    # 0x3b = (1 << 5) | 27 = major 1 (negative), 8-byte extended length
    return b"\x3b" + b"\xff" * 8


# ---------------------------------------------------------------------------
# Recursion depth limit
# ---------------------------------------------------------------------------

class TestRecursionDepthLimit:
    def test_max_nesting_depth_constant_is_sane(self) -> None:
        assert 16 <= _MAX_NESTING_DEPTH <= 256

    def test_payload_at_limit_decodes(self) -> None:
        payload = _nested_array_cbor(_MAX_NESTING_DEPTH)
        value = decode_dag_cbor(payload)
        # unwrap all layers — should be None at the centre
        current = value
        for _ in range(_MAX_NESTING_DEPTH):
            assert isinstance(current, list) and len(current) == 1
            current = current[0]
        assert current is None

    def test_payload_one_beyond_limit_raises(self) -> None:
        payload = _nested_array_cbor(_MAX_NESTING_DEPTH + 1)
        with pytest.raises(ValueError, match="dag_cbor_max_nesting_depth_exceeded"):
            decode_dag_cbor(payload)

    def test_deeply_nested_map_raises(self) -> None:
        # Build a deeply nested map: {"a": {"a": ... {"a": null}}}
        # Each level: 0xa1 (map of 1) + 0x61 0x61 (text "a") + value
        inner = b"\xf6"  # null
        for _ in range(_MAX_NESTING_DEPTH + 2):
            inner = b"\xa1\x61\x61" + inner  # {a: inner}
        with pytest.raises(ValueError, match="dag_cbor_max_nesting_depth_exceeded"):
            decode_dag_cbor(inner)

    def test_recursion_bomb_under_cbor_size_cap_raises(self) -> None:
        """2001-byte payload — well under 1 MB — must not cause RecursionError."""
        payload = _nested_array_cbor(2000)
        with pytest.raises(ValueError, match="dag_cbor_max_nesting_depth_exceeded"):
            validate_canonical_ilc_dag_cbor(payload)


# ---------------------------------------------------------------------------
# OOB negative integer
# ---------------------------------------------------------------------------

class TestNegativeIntegerRange:
    def test_max_valid_negative(self) -> None:
        # -(2^63) is valid — CBOR: 0x3b 0x7f 0xff 0xff 0xff 0xff 0xff 0xff 0xff
        # val = 2^63 - 1, n = -1 - (2^63 - 1) = -2^63
        val_bytes = struct.pack(">Q", 2**63 - 1)
        cbor = b"\x3b" + val_bytes
        assert decode_dag_cbor(cbor) == -(2**63)

    def test_oob_negative_raises_in_decoder(self) -> None:
        with pytest.raises(ValueError, match="dag_cbor_integer_out_of_signed_64bit_range"):
            decode_dag_cbor(_oob_negative_cbor())

    def test_oob_negative_does_not_reach_encoder(self) -> None:
        """Confirm the fix is in the decoder, not caught only by re-encode check."""
        with pytest.raises(ValueError, match="dag_cbor_integer_out_of_signed_64bit_range"):
            decode_dag_cbor(_oob_negative_cbor())


# ---------------------------------------------------------------------------
# Float rejection in validate_ilc_object_encodable
# ---------------------------------------------------------------------------

class TestFloatRejection:
    def test_top_level_float_rejected(self) -> None:
        with pytest.raises(ValueError, match="float"):
            validate_ilc_object_encodable(3.14)

    def test_float_in_dict_value_rejected(self) -> None:
        with pytest.raises(ValueError, match="float"):
            validate_ilc_object_encodable({"score": 0.5})

    def test_float_in_nested_list_rejected(self) -> None:
        with pytest.raises(ValueError, match="float"):
            validate_ilc_object_encodable({"items": [1, 2, 1.5]})

    def test_float_zero_rejected(self) -> None:
        with pytest.raises(ValueError, match="float"):
            validate_ilc_object_encodable(0.0)

    def test_integer_accepted(self) -> None:
        validate_ilc_object_encodable({"score": 5, "items": [1, 2, 3]})

    def test_encoder_still_rejects_float_directly(self) -> None:
        with pytest.raises(TypeError, match="float"):
            encode_dag_cbor({"x": 1.0})


# ---------------------------------------------------------------------------
# Layer 2 / Layer 3 builder CIDv1 validation
# ---------------------------------------------------------------------------

class TestBuilderCidv1Validation:
    def _valid_sha256(self) -> str:
        return "a" * 64

    def _valid_digest(self, prefix: str) -> str:
        return f"{prefix}:" + "b" * 64

    def test_layer2_accepts_empty_cidv1_sentinel(self) -> None:
        from ilc_core.bundle.layer2_epoch_snapshot import generate_layer2_epoch_snapshot

        # Empty string is permitted (caller has not yet derived the CIDv1)
        snap = generate_layer2_epoch_snapshot(
            epoch_number=1,
            previous_snapshot_sha256="",
            layer0_sha256=self._valid_sha256(),
            graph_state_digest=self._valid_digest("graph"),
            agent_state_digest=self._valid_digest("agent"),
            active_contract_digest=self._valid_digest("contract"),
        )
        assert snap.layer0_protocol_bundle_cidv1 == ""
        assert snap.layer1_genesis_bundle_cidv1 == ""

    def test_layer2_rejects_malformed_layer0_cidv1(self) -> None:
        from ilc_core.bundle.layer2_epoch_snapshot import generate_layer2_epoch_snapshot

        with pytest.raises(ValueError, match="layer2_epoch_snapshot_invalid_layer0_cidv1"):
            generate_layer2_epoch_snapshot(
                epoch_number=1,
                previous_snapshot_sha256="",
                layer0_sha256=self._valid_sha256(),
                graph_state_digest=self._valid_digest("graph"),
                agent_state_digest=self._valid_digest("agent"),
                active_contract_digest=self._valid_digest("contract"),
                layer0_cidv1="not-a-real-cidv1",
            )

    def test_layer2_rejects_malformed_layer1_cidv1(self) -> None:
        from ilc_core.bundle.layer2_epoch_snapshot import generate_layer2_epoch_snapshot

        with pytest.raises(ValueError, match="layer2_epoch_snapshot_invalid_layer1_cidv1"):
            generate_layer2_epoch_snapshot(
                epoch_number=1,
                previous_snapshot_sha256="",
                layer0_sha256=self._valid_sha256(),
                graph_state_digest=self._valid_digest("graph"),
                agent_state_digest=self._valid_digest("agent"),
                active_contract_digest=self._valid_digest("contract"),
                layer1_cidv1="not-a-real-cidv1",
            )

    def test_layer3_accepts_empty_cidv1_sentinel(self) -> None:
        from ilc_core.bundle.layer3_wire_binding import generate_layer3_wire_binding

        binding = generate_layer3_wire_binding(
            message_type="claim.submit",
            layer0_schema_ref="layer0:schema:Node",
            sender_agent_id="agent-a",
            epoch_number=1,
            payload_digest=self._valid_digest("payload"),
            signature_ref="sig:abc",
        )
        assert binding.layer2_epoch_snapshot_cidv1 == ""

    def test_layer3_rejects_malformed_layer2_cidv1(self) -> None:
        from ilc_core.bundle.layer3_wire_binding import generate_layer3_wire_binding

        with pytest.raises(ValueError, match="layer3_wire_binding_invalid_layer2_cidv1"):
            generate_layer3_wire_binding(
                message_type="claim.submit",
                layer0_schema_ref="layer0:schema:Node",
                sender_agent_id="agent-a",
                epoch_number=1,
                payload_digest=self._valid_digest("payload"),
                signature_ref="sig:abc",
                layer2_cidv1="not-a-real-cidv1",
            )
