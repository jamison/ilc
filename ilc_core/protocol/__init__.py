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
    HARNESS_INTERFACES_VERSION,
    StorageHarness,
    TransportHarness,
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
    "HARNESS_INTERFACES_VERSION",
    "StorageHarness",
    "TransportHarness",
]
