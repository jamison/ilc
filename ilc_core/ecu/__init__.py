# SPDX-License-Identifier: AGPL-3.0-only
"""ECU fast-path intent primitives."""

from .ecu_fast_path_intent import (
    ECU_FAST_PATH_INTENT_VERSION,
    ECU_FAST_PATH_TRANSFER_ENABLED,
    PRE_RC_TRANSFER_CAP_ECU,
    ECUFastPathIntent,
    TransferClass,
    validate_intent,
)
from .ecu_transfer_adapter import ECU_TRANSFER_ADAPTER_VERSION, ECUTransferAdapter
from .ecu_transfer_context_verifier import (
    ECU_TRANSFER_CONTEXT_VERIFIER_VERSION,
    ECUContextVerificationError,
    ECUTransferContextVerifier,
)

__all__ = [
    "ECU_FAST_PATH_INTENT_VERSION",
    "ECU_FAST_PATH_TRANSFER_ENABLED",
    "ECU_TRANSFER_ADAPTER_VERSION",
    "ECU_TRANSFER_CONTEXT_VERIFIER_VERSION",
    "PRE_RC_TRANSFER_CAP_ECU",
    "ECUContextVerificationError",
    "ECUFastPathIntent",
    "ECUTransferAdapter",
    "ECUTransferContextVerifier",
    "TransferClass",
    "validate_intent",
]
