"""PUBLIC_RC_EXCLUDE: adr_0009_layer2_private_implementation
PUBLIC_RC_EXCLUDE_REASON: Private ADR-0009 Layer 2 generator/verifier. Does not mutate ADR status or publish protocol bundles.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION = True


def _reject_float(value: object, token: str) -> None:
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, Mapping):
        for key, nested in value.items():
            _reject_float(key, token)
            _reject_float(nested, token)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            _reject_float(nested, token)


def _canonical_json(payload: Mapping[str, object]) -> str:
    _reject_float(payload, "layer2_epoch_snapshot_float_not_allowed")
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _require_non_empty_string(value: str, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)


def _require_epoch_number(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("layer2_epoch_snapshot_invalid_epoch_number")


@dataclass(frozen=True)
class Layer2EpochSnapshot:
    epoch_number: int
    previous_snapshot_sha256: str
    layer0_protocol_bundle_sha256: str
    graph_state_digest: str
    agent_state_digest: str
    active_contract_digest: str
    canonical_json: str
    sha256: str
    public_rc_exclude: bool = True


def generate_layer2_epoch_snapshot(
    *,
    epoch_number: int,
    previous_snapshot_sha256: str,
    layer0_sha256: str,
    graph_state_digest: str,
    agent_state_digest: str,
    active_contract_digest: str,
) -> Layer2EpochSnapshot:
    _require_epoch_number(epoch_number)
    _require_non_empty_string(layer0_sha256, "layer2_epoch_snapshot_missing_layer0_sha256")
    _require_non_empty_string(graph_state_digest, "layer2_epoch_snapshot_missing_graph_state_digest")
    _require_non_empty_string(agent_state_digest, "layer2_epoch_snapshot_missing_agent_state_digest")
    _require_non_empty_string(
        active_contract_digest,
        "layer2_epoch_snapshot_missing_active_contract_digest",
    )
    if epoch_number > 1 and previous_snapshot_sha256 == "":
        raise ValueError("layer2_epoch_snapshot_missing_previous_sha256")

    envelope = {
        "active_contract_digest": active_contract_digest,
        "agent_state_digest": agent_state_digest,
        "epoch_number": epoch_number,
        "graph_state_digest": graph_state_digest,
        "layer": 2,
        "layer0_protocol_bundle_sha256": layer0_sha256,
        "previous_snapshot_sha256": previous_snapshot_sha256,
        "public_rc_exclude": True,
    }
    canonical_json = _canonical_json(envelope)
    return Layer2EpochSnapshot(
        epoch_number=epoch_number,
        previous_snapshot_sha256=previous_snapshot_sha256,
        layer0_protocol_bundle_sha256=layer0_sha256,
        graph_state_digest=graph_state_digest,
        agent_state_digest=agent_state_digest,
        active_contract_digest=active_contract_digest,
        canonical_json=canonical_json,
        sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
    )


def verify_layer2_epoch_snapshot(snapshot: Layer2EpochSnapshot) -> bool:
    rebuilt = generate_layer2_epoch_snapshot(
        epoch_number=snapshot.epoch_number,
        previous_snapshot_sha256=snapshot.previous_snapshot_sha256,
        layer0_sha256=snapshot.layer0_protocol_bundle_sha256,
        graph_state_digest=snapshot.graph_state_digest,
        agent_state_digest=snapshot.agent_state_digest,
        active_contract_digest=snapshot.active_contract_digest,
    )
    return (
        rebuilt.canonical_json == snapshot.canonical_json
        and rebuilt.sha256 == snapshot.sha256
        and snapshot.public_rc_exclude is True
    )


__all__ = [
    "ADR_0009_LAYER2_NOT_PUBLIC_DISTRIBUTION",
    "Layer2EpochSnapshot",
    "generate_layer2_epoch_snapshot",
    "verify_layer2_epoch_snapshot",
]
