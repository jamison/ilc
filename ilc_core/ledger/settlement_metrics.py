from typing import Dict, Any
from ilc_core.ledger.backend import LedgerBackend

def compute_settlement_metrics(
    ledger: LedgerBackend
) -> Dict[str, Any]:
    """
    Compute aggregate metrics from the ledger's state.
    
    Returns a dictionary suitable for inclusion in experiment summaries.
    
    Assumptions:
    - Reads from `ledger.epoch_records` and `ledger.stake_snapshots`.
    - Intended for InMemory/File backends that expose those attributes.
    """
    
    records = getattr(ledger, "epoch_records", {})
    snapshots = getattr(ledger, "stake_snapshots", {})
    
    # Initialize counters
    num_epochs_total = len(records)
    num_epochs_settled = 0
    num_epochs_rolled_back = 0
    num_epochs_superseded = 0
    
    total_rewards_distributed = 0.0
    total_rewards_stubbed = 0.0
    
    for _, rec in records.items():
        status = rec.get("status", "unknown")
        dist_status = rec.get("distribution_status", "unknown")
        
        if status == "settled":
            num_epochs_settled += 1
        elif status == "rolled_back":
            num_epochs_rolled_back += 1
        elif status == "superseded": # Assumption of status name
             num_epochs_superseded += 1
             
        # Reward sums
        # "total_rewards_distributed should sum summary.reward_total only where status == settled and distribution_status == distributed"
        summary = rec.get("summary", {})
        reward = float(summary.get("reward_total", 0.0))
        
        if status == "settled":
            if dist_status == "distributed":
                total_rewards_distributed += reward
            elif dist_status == "stub_no_snapshot":
                total_rewards_stubbed += reward
                
    # Snapshot count
    num_snapshots = len(snapshots)
    
    return {
        "num_epochs_total": num_epochs_total,
        "num_epochs_settled": num_epochs_settled,
        "num_epochs_rolled_back": num_epochs_rolled_back,
        "num_epochs_superseded": num_epochs_superseded,
        "num_snapshots": num_snapshots,
        "total_rewards_distributed": total_rewards_distributed,
        "total_rewards_stubbed": total_rewards_stubbed,
    }
