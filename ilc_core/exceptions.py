"""Centralized ILC domain exception hierarchy."""

from __future__ import annotations


class IlcError(Exception):
    """Base exception for all ILC domain errors."""


class InsufficientStakeError(IlcError, ValueError):
    """Raised when a stake value is below the required threshold."""

    def __init__(
        self,
        agent_id: str,
        stake: float,
        required: float,
        message: str = "",
    ) -> None:
        self.agent_id = agent_id
        self.stake = stake
        self.required = required
        super().__init__(
            message or f"Insufficient stake for {agent_id}: {stake} < {required}"
        )


class StakeNotFoundError(IlcError, KeyError):
    """Raised when a referenced agent has no stake record."""

    def __init__(self, agent_id: str, message: str = "") -> None:
        self.agent_id = agent_id
        super().__init__(message or f"No stake record for agent: {agent_id}")


class EpochError(IlcError, ValueError):
    """Raised for epoch boundary/state violations."""


class ContradictionError(IlcError, ValueError):
    """Raised when contradiction processing fails validation."""


class GraphIntegrityError(IlcError, ValueError):
    """Raised when a graph operation violates structural integrity."""


class DuplicateNodeError(GraphIntegrityError):
    """Raised when inserting a node with a duplicate id."""

    def __init__(self, node_id: str, message: str = "") -> None:
        self.node_id = node_id
        super().__init__(message or f"Duplicate node ID: {node_id}")


class NodeNotFoundError(IlcError, KeyError):
    """Raised when a referenced node id does not exist."""

    def __init__(self, node_id: str, message: str = "") -> None:
        self.node_id = node_id
        super().__init__(message or f"Node not found: {node_id}")


class GossipValidationError(IlcError, ValueError):
    """Raised when an inbound gossip payload fails validation."""

    def __init__(self, token: str, message: str = "") -> None:
        self.token = token
        super().__init__(message or token)


class ManifestError(IlcError, ValueError):
    """Base for manifest-related errors."""


class ManifestParseError(ManifestError):
    """Raised when a manifest cannot be parsed or validated."""


class ManifestEntryNotFoundError(IlcError, FileNotFoundError):
    """Raised when a manifest entry references a missing file."""


class CanonVerificationError(IlcError, ValueError):
    """Raised when canon verification fails."""


class LedgerError(IlcError, ValueError):
    """Base for ledger operation errors."""


class ConfigError(IlcError, ValueError):
    """Raised for configuration loading/validation failures."""


class ConfigNotFoundError(ConfigError, FileNotFoundError):
    """Raised when a required config file is not found."""

    def __init__(self, path: str, message: str = "") -> None:
        self.path = path
        super().__init__(message or f"config_not_found:{path}")


class TokenizationError(IlcError, ValueError):
    """Raised when tokenization limits are exceeded or tokens are invalid."""


class NgramExtractionError(IlcError, ValueError):
    """Raised when n-gram extraction parameters are invalid."""


class ProtocolError(IlcError, ValueError):
    """Base exception for protocol-surface errors."""


class ProtocolSchemaLoadError(ProtocolError):
    """Raised when a protocol schema cannot be loaded or parsed."""


class ProtocolMappingError(ProtocolError):
    """Raised when internal models cannot be mapped to protocol contracts."""


class ReplayProofError(IlcError, ValueError):
    """Base exception for replay-proof contract failures."""


class ReplayProofManifestError(ReplayProofError):
    """Raised when replay-proof manifest content violates contract rules."""


class ReplayProofPackageError(ReplayProofError):
    """Raised when replay-proof package content violates contract rules."""


class ReplayProofBaselineError(ReplayProofError):
    """Raised when replay-proof baseline reports are invalid."""
