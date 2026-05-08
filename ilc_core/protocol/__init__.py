"""
ILC Protocol module.

This module provides protocol-level utilities including:
- NDJSON bundle transport (Phase 66C)
- Bundle record verification
"""

from .ndjson_bundle import (
    # Constants
    DEFAULT_MAX_LINE_BYTES,
    BUNDLE_VERSION,
    TYPE_HEADER,
    TYPE_RECORD,
    TYPE_FOOTER,
    # Base64url
    b64u_encode,
    b64u_decode,
    # JSON serialization
    dumps_ndjson,
    loads_ndjson,
    # Validators
    validate_bundle_header,
    validate_bundle_record,
    validate_bundle_footer,
    # Factory functions
    make_bundle_header,
    make_bundle_record,
    # Writer/Reader
    write_bundle,
    iter_bundle,
    read_bundle,
)

from .bundle_verify import (
    verify_bundle_record,
    verify_bundle_record_from_bytes,
)
from .harness_interfaces import (
    AdmissionReceiptStore,
    GAP14_ADAPTER_EXTRACTION_VERSION,
    HARNESS_INTERFACES_VERSION,
    PUBLIC_RUNTIME_STORE_INTERFACES_VERSION,
    PublicReceiptStore,
    PublicWalletStore,
    StorageHarness,
    TruthPrimitiveGraphPersistence,
    TransportHarness,
)
from .primitive_type_registry import (
    ALLOWED_PRIMITIVE_TYPES,
    PRIMITIVE_TYPE_REGISTRY_VERSION,
    SYSTEM_PRIMITIVE_TYPES,
)

__all__ = [
    # Constants
    "DEFAULT_MAX_LINE_BYTES",
    "BUNDLE_VERSION",
    "TYPE_HEADER",
    "TYPE_RECORD",
    "TYPE_FOOTER",
    # Base64url
    "b64u_encode",
    "b64u_decode",
    # JSON serialization
    "dumps_ndjson",
    "loads_ndjson",
    # Validators
    "validate_bundle_header",
    "validate_bundle_record",
    "validate_bundle_footer",
    # Factory functions
    "make_bundle_header",
    "make_bundle_record",
    # Writer/Reader
    "write_bundle",
    "iter_bundle",
    "read_bundle",
    # Verification
    "verify_bundle_record",
    "verify_bundle_record_from_bytes",
    # Harness adapter interfaces
    "AdmissionReceiptStore",
    "GAP14_ADAPTER_EXTRACTION_VERSION",
    "HARNESS_INTERFACES_VERSION",
    "PUBLIC_RUNTIME_STORE_INTERFACES_VERSION",
    "PublicReceiptStore",
    "PublicWalletStore",
    "StorageHarness",
    "TruthPrimitiveGraphPersistence",
    "TransportHarness",
    # Primitive type registry
    "ALLOWED_PRIMITIVE_TYPES",
    "PRIMITIVE_TYPE_REGISTRY_VERSION",
    "SYSTEM_PRIMITIVE_TYPES",
]
