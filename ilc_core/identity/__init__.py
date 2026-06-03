# SPDX-License-Identifier: AGPL-3.0-only
"""Identity runtime package."""

from .sybil_resistance_runtime import (
    CDL_V1_DEPENDENCY,
    CDL_V2_DEPENDENCY,
    CDL_V2_RUNTIME_VERSION,
    SybilResistanceValidationError,
    compute_burst_write_penalty,
    compute_identity_cluster_risk,
    compute_sybil_penalty,
    compute_diversity_floor_contribution,
)
from .agent_id_runtime import (
    AGENT_ID_RUNTIME_VERSION,
    CDL_042_DEPENDENCY,
    NODE_SCHEMA_DEPENDENCY,
    AgentIdentityError,
    derive_agent_id,
    verify_agent_id,
)
from .log_redaction_runtime import (
    AGENT_ID_PLAINTEXT_REDACTED_VALIDATOR_LOGS_TOKEN,
    HIGH_001_LOG_REDACTION_RUNTIME_VERSION,
    SENDER_PRIVACY_CLAIM_BLOCKER_CLEARED_TOKEN,
    AgentIDLogRedactionFilter,
    redact_agent_id_for_log,
    redact_agent_ids_in_log_message,
)

__all__ = [
    "CDL_V2_RUNTIME_VERSION",
    "CDL_V2_DEPENDENCY",
    "CDL_V1_DEPENDENCY",
    "SybilResistanceValidationError",
    "compute_identity_cluster_risk",
    "compute_burst_write_penalty",
    "compute_diversity_floor_contribution",
    "compute_sybil_penalty",
    "AGENT_ID_RUNTIME_VERSION",
    "CDL_042_DEPENDENCY",
    "NODE_SCHEMA_DEPENDENCY",
    "AgentIdentityError",
    "derive_agent_id",
    "verify_agent_id",
    "AGENT_ID_PLAINTEXT_REDACTED_VALIDATOR_LOGS_TOKEN",
    "HIGH_001_LOG_REDACTION_RUNTIME_VERSION",
    "SENDER_PRIVACY_CLAIM_BLOCKER_CLEARED_TOKEN",
    "AgentIDLogRedactionFilter",
    "redact_agent_id_for_log",
    "redact_agent_ids_in_log_message",
]
