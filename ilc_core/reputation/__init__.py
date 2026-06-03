# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-V1 temporal-decay runtime package."""

from .temporal_decay_runtime import (
    CDL_V1_DEPENDENCY,
    CDL_V1_DECIMAL_REWRITE_TOKEN,
    CDL_V1_RUNTIME_VERSION,
    TemporalDecayValidationError,
    apply_temporal_decay,
    compute_decay_multiplier,
)

__all__ = [
    "CDL_V1_RUNTIME_VERSION",
    "CDL_V1_DEPENDENCY",
    "CDL_V1_DECIMAL_REWRITE_TOKEN",
    "TemporalDecayValidationError",
    "compute_decay_multiplier",
    "apply_temporal_decay",
]
