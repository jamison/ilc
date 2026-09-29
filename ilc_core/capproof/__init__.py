# SPDX-License-Identifier: AGPL-3.0-only
"""Default-off CapProof v1 runtime substrate for CDL-115."""

from .capability_vector import CapabilityVector, CapProofValidationError
from .multiplier import (
    CAPPROOF_MULTIPLIER_BASELINE,
    CAPPROOF_MULTIPLIER_MAX,
    CAPPROOF_MULTIPLIER_MIN,
    compute_capproof_multiplier,
)
from .probe_runner import (
    CAPPROOF_RUNTIME_VERSION,
    CAPPROOF_V1_NO_ILC_MINT,
    BandwidthProbe,
    BandwidthProbeResult,
    DeterminismProbe,
    DeterminismProbeResult,
    GEMMProbe,
    GEMMProbeResult,
    GraphProbe,
    GraphProbeResult,
    InferProbe,
    InferProbeResult,
)

__all__ = [
    "BandwidthProbe",
    "BandwidthProbeResult",
    "CAPPROOF_MULTIPLIER_BASELINE",
    "CAPPROOF_MULTIPLIER_MAX",
    "CAPPROOF_MULTIPLIER_MIN",
    "CAPPROOF_RUNTIME_VERSION",
    "CAPPROOF_V1_NO_ILC_MINT",
    "CapProofValidationError",
    "CapabilityVector",
    "DeterminismProbe",
    "DeterminismProbeResult",
    "GEMMProbe",
    "GEMMProbeResult",
    "GraphProbe",
    "GraphProbeResult",
    "InferProbe",
    "InferProbeResult",
    "compute_capproof_multiplier",
]
