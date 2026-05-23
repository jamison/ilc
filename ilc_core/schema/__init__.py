# SPDX-License-Identifier: AGPL-3.0-or-later
"""D2 schema baseline runtime package."""

from .d2_schema_baseline_runtime import (
    ALLOWED_FIELD_TYPES,
    CANONICAL_SCHEMA_VECTORS,
    SCHEMA_BASELINE_VERSION,
    D2SchemaValidationError,
    canonical_schema_vectors,
    generate_schema_catalog,
    verify_schema_catalog,
)

__all__ = [
    "ALLOWED_FIELD_TYPES",
    "CANONICAL_SCHEMA_VECTORS",
    "SCHEMA_BASELINE_VERSION",
    "D2SchemaValidationError",
    "canonical_schema_vectors",
    "generate_schema_catalog",
    "verify_schema_catalog",
]
