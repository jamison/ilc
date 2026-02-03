from typing import Dict, Any, List, Optional
import hashlib
import json
from dataclasses import asdict

from ilc_core.ledger.stake_snapshot import StakeSnapshot

def hash_inputs(
    epoch_record: Dict[str, Any],
    snapshot: StakeSnapshot,
    balances_before: Dict[str, float],
    balances_after: Dict[str, float],
) -> str:
    """
    Create a deterministic hash of the verification inputs.
    """
    # Deterministic sorting
    input_data = {
        "epoch_record": epoch_record,
        "snapshot": asdict(snapshot) if snapshot else None,
        "balances_before": dict(sorted(balances_before.items())),
        "balances_after": dict(sorted(balances_after.items())),
    }
    dump = json.dumps(input_data, sort_keys=True, default=str)
    return hashlib.sha256(dump.encode("utf-8")).hexdigest()[:16]

def verify_stake_distribution(
    epoch_record: Dict[str, Any],
    snapshot: StakeSnapshot,
    balances_before: Dict[str, float],
    balances_after: Dict[str, float],
) -> Dict[str, Any]:
    """
    Verify that reward distribution matches the stake snapshot and expected total.
    """
    eps = 1e-6
    status = epoch_record.get("distribution_status")
    
    # Extract total reward (robust access)
    summary = epoch_record.get("summary", {})
    if isinstance(summary, dict):
        reward_total = float(summary.get("reward_total", 0.0))
    else:
        # Should not happen in spec, but defensive
        reward_total = 0.0

    # Compute actual deltas
    deltas = {}
    # We care about all agents in the snapshot, plus any that appeared in balances 
    # (though typically only snapshot agents get rewards).
    # Verification should track all balance changes.
    all_agents = set(balances_before.keys()) | set(balances_after.keys())
    if snapshot:
        all_agents.update(snapshot.stakes.keys())
        
    for agent_id in all_agents:
        before = float(balances_before.get(agent_id, 0.0))
        after = float(balances_after.get(agent_id, 0.0))
        delta = after - before
        if abs(delta) > eps or agent_id in (snapshot.stakes if snapshot else []):
             deltas[agent_id] = delta

    total_delta = sum(deltas.values())
    expected_total = reward_total if status == "distributed" else 0.0
    
    max_err = 0.0
    
    # Fix B: Guard against distributed status without valid snapshot
    if status == "distributed" and (not snapshot or snapshot.total_stake <= 0):
        # Critical failure: Distributed but no snapshot means we can't verify logic.
        return {
            "ok": False, # Explicit fail
            "total_delta": total_delta,
            "expected_total": expected_total,
            "max_agent_error": max(deltas.values(), default=0.0), # Treat all deltas as error? Or undefined.
            "top_errors": ["Validation Failed: 'distributed' status but missing valid snapshot/stake"],
            "input_hash": hash_inputs(epoch_record, snapshot, balances_before, balances_after),
        }

    if status == "distributed" and snapshot and snapshot.total_stake > 0:
        for agent_id, stake in snapshot.stakes.items():
            expected = (stake / snapshot.total_stake) * reward_total
            actual = deltas.get(agent_id, 0.0)
            err = abs(actual - expected)
            max_err = max(max_err, err)
            
        # Also check if non-stakers got rewards? (deltas keys not in stakes)
        for agent_id, delta in deltas.items():
            if agent_id not in snapshot.stakes and abs(delta) > eps:
                # Unexpected change for non-staker
                max_err = max(max_err, abs(delta))
                
    elif status == "stub_no_snapshot":
        # Expect zero changes
        max_err = max((abs(v) for v in deltas.values()), default=0.0)
        
    # Check bounds
    ok_total = abs(total_delta - expected_total) <= eps
    ok_individual = max_err <= eps
    ok = ok_total and ok_individual
    
    # Top errors
    # We want to identify the biggest discrepancies.
    # If distributed: error = |actual - expected|
    # If stub: error = |actual - 0|
    error_map = {}
    if status == "distributed" and snapshot and snapshot.total_stake > 0:
        for agent_id in deltas.keys() | snapshot.stakes.keys():
            actual = deltas.get(agent_id, 0.0)
            stake = snapshot.stakes.get(agent_id, 0.0)
            expected = (stake / snapshot.total_stake) * reward_total
            error_map[agent_id] = abs(actual - expected)
    else:
        for agent_id, delta in deltas.items():
            error_map[agent_id] = abs(delta)
            
    top_errors = sorted(error_map.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_errors_formatted = [f"{k}:{v:.6f}" for k, v in top_errors if v > eps]

    return {
        "ok": ok,
        "total_delta": total_delta,
        "expected_total": expected_total,
        "max_agent_error": max_err,
        "top_errors": top_errors_formatted,
        "input_hash": hash_inputs(epoch_record, snapshot, balances_before, balances_after),
    }
