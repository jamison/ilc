from typing import Any, Dict, Optional, Union
from ilc_core.types import Node, node_to_claim_record
from ilc_core.economics.outcome import TaskOutcome
from ilc_core.exceptions import ProtocolMappingError


def node_to_protocol_claim(node: Node) -> Dict[str, Any]:
    """
    Map an internal Node (type='claim') to the protocol 'claim' object.

    This does NOT write to disk or perform validation beyond basic type checks.
    """
    if node.type != "claim":
        raise ProtocolMappingError(
            f"protocol_mapping_invalid_claim_node_type:{node.type}"
        )

    claim = node_to_claim_record(node)
    return {
        "id": claim.id,
        "type": claim.type,
        "agent_id": claim.agent_id,
        "content": claim.content,
        "parent_ids": claim.parent_ids,
        "timestamp": claim.timestamp,
        "net_stake": claim.net_stake,
    }


def node_to_protocol_refute(node: Node) -> Dict[str, Any]:
    """
    Map an internal Node (type='refutation') to the protocol 'refute' object.

    For now we assume the node has target_id or similar attributes.
    """
    # Note: types.py defines 'refutation', but brief mentioned 'refute'.
    # We accept 'refutation' as the internal type.
    if node.type not in ("refute", "refutation"):
        raise ProtocolMappingError(
            f"protocol_mapping_invalid_refute_node_type:{node.type}"
        )

    claim = node_to_claim_record(node)
    
    return {
        "id": claim.id,
        "type": "refute", # Canonical protocol type is 'refute'
        "agent_id": claim.agent_id,
        "target_claim_id": claim.target_id,
        "content": claim.content,
        "timestamp": claim.timestamp,
        "net_stake": claim.net_stake,
    }


def outcome_to_protocol_task_outcome(
    outcome: TaskOutcome,
    *,
    epoch: Optional[int] = None,
    agent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Map TaskOutcome -> protocol 'task_outcome' object.

    Epoch and agent_id can be supplied by the caller if not already on the outcome.
    """
    return {
        "task_id": getattr(outcome, "task_id", None),
        "task_type": outcome.task_type,
        "domain": outcome.domain,
        "agent_id": agent_id or getattr(outcome, "agent_id", None),
        "epoch": epoch,
        "stake_spent": outcome.stake_spent,
        "reward_paid": outcome.reward_paid,
        "success": outcome.success,
        "meta": {},
    }


def epoch_summary_to_protocol(
    epoch: int,
    summary: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Map a simple epoch summary dict (e.g. from SimpleEpochLedger) into
    the protocol 'epoch_summary' object.
    """
    return {
        "epoch": epoch,
        "total_tasks": int(summary.get("total_tasks", 0)),
        "total_ecu_spent": float(summary.get("total_ecu_spent", 0.0)),
        "total_reward_paid": float(summary.get("total_reward_paid", 0.0)),
        "clearing_price_ilc_per_ecu": float(
            summary.get("clearing_price_ilc_per_ecu", 0.0)
        ),
        "meta": {},
    }
