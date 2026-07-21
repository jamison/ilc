# SPDX-License-Identifier: AGPL-3.0-only
"""Epoch-state CIDv1Root bridge for Phase 1575h-Fix3.

Rust consensus stores ``CIDv1Root`` as raw 36 bytes. Python bundle code normally
surfaces the same CID as a base32 NodeID string. This module is the explicit
bridge: derive raw dag-cbor/sha2-256 CIDv1 bytes from Layer2EpochSnapshotV2
DAG-CBOR and expose their 72-character lowercase hex form for Rust CLI input.
"""

from __future__ import annotations

from ilc_core.bundle.layer2_epoch_snapshot import Layer2EpochSnapshotV2
from ilc_core.encoding.cidv1 import CODEC_DAG_CBOR, cidv1_bytes, sha2_256_multihash
from ilc_core.protocol.commit_epoch_emission_runtime import _require_state_root_cidv1_hex

DAG_CBOR_SHA2_256_CIDV1_PREFIX_HEX = "01711220"
STATE_ROOT_CIDV1_HEX_LENGTH = 72


def state_root_cidv1_bytes_from_layer2_v2(snapshot: Layer2EpochSnapshotV2) -> bytes:
    if not isinstance(snapshot, Layer2EpochSnapshotV2):
        raise ValueError("layer2_epoch_snapshot_v2_required")
    return cidv1_bytes(CODEC_DAG_CBOR, sha2_256_multihash(snapshot.dag_cbor))


def layer2_v2_to_state_root_cidv1_hex(snapshot: Layer2EpochSnapshotV2) -> str:
    return validate_state_root_cidv1_hex(
        state_root_cidv1_bytes_from_layer2_v2(snapshot).hex()
    )


def validate_state_root_cidv1_hex(value: str) -> str:
    normalized = _require_state_root_cidv1_hex(
        value,
        "epoch_state_root_cidv1_hex_invalid_phase_1575h_fix3",
    )
    if normalized == "0" * STATE_ROOT_CIDV1_HEX_LENGTH:
        raise ValueError("epoch_state_root_cidv1_hex_all_zero_phase_1575h_fix3")
    if not normalized.startswith(DAG_CBOR_SHA2_256_CIDV1_PREFIX_HEX):
        raise ValueError("epoch_state_root_cidv1_hex_not_dag_cbor_sha2_256_phase_1575h_fix3")
    return normalized


__all__ = [
    "DAG_CBOR_SHA2_256_CIDV1_PREFIX_HEX",
    "STATE_ROOT_CIDV1_HEX_LENGTH",
    "layer2_v2_to_state_root_cidv1_hex",
    "state_root_cidv1_bytes_from_layer2_v2",
    "validate_state_root_cidv1_hex",
]
