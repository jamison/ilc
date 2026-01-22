"""
ILC Encoding module - Deterministic DAG-CBOR and CIDv1 NodeID.

This module provides content-addressable encoding primitives:
- Deterministic DAG-CBOR subset encoder/decoder
- CIDv1 NodeID generation (SHA2-256 multihash, base32 lowercase)

All implementations are stdlib-only (no external dependencies).
"""

from .dag_cbor import (
    encode_dag_cbor,
    decode_dag_cbor,
    decode_dag_cbor_strict,
    validate_ilc_object_keys_str_only,
    is_ilc_object_keys_str_only,
    validate_canonical_ilc_dag_cbor,
    is_canonical_ilc_dag_cbor,
)
from .cidv1 import node_id_from_obj, parse_cidv1, parse_nodeid_strict, is_nodeid

__all__ = [
    "encode_dag_cbor",
    "decode_dag_cbor",
    "decode_dag_cbor_strict",
    "node_id_from_obj",
    "parse_cidv1",
    "parse_nodeid_strict",
    "is_nodeid",
    "validate_ilc_object_keys_str_only",
    "is_ilc_object_keys_str_only",
    "validate_canonical_ilc_dag_cbor",
    "is_canonical_ilc_dag_cbor",
]
