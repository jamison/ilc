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
from .governance_weighted_decision import (
    CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN,
    COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN,
    EMPTY_GOVERNANCE_PARTICIPANT_SET_REGRESSION_TOKEN,
    GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN,
    GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN,
    GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION,
    LEGACY_FLOAT_CONVERSION_GUARD_TOKEN,
    NONFINITE_FLOAT_INF_NEGATIVE_INF_REGRESSION_TOKEN,
    PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN,
    PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN,
    GovernanceWeightedDecisionQuote,
    GovernanceWeightedParticipant,
    build_governance_weighted_decision_quote,
    require_production_governance_decision_activation,
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
    # Governance weighted decision runtime
    "CDL_013_GOVERNANCE_WEIGHT_LIVE_INTEGRATION_TOKEN",
    "COMPUTE_GOVERNANCE_WEIGHTS_IN_CALL_PATH_TOKEN",
    "EMPTY_GOVERNANCE_PARTICIPANT_SET_REGRESSION_TOKEN",
    "GOVERNANCE_WEIGHT_DECIMAL_REWRITE_CLOSED_TOKEN",
    "GOVERNANCE_WEIGHT_OUTPUT_WIRED_DECISION_SURFACES_TOKEN",
    "GOVERNANCE_WEIGHTED_DECISION_RUNTIME_VERSION",
    "LEGACY_FLOAT_CONVERSION_GUARD_TOKEN",
    "NONFINITE_FLOAT_INF_NEGATIVE_INF_REGRESSION_TOKEN",
    "PRODUCTION_GOVERNANCE_DECISION_ACTIVATION_TOKEN",
    "PRODUCTION_GOVERNANCE_DECISIONS_NOT_ACTIVATED_TOKEN",
    "GovernanceWeightedDecisionQuote",
    "GovernanceWeightedParticipant",
    "build_governance_weighted_decision_quote",
    "require_production_governance_decision_activation",
]
