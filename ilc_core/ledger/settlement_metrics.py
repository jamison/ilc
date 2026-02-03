from typing import Dict, Any
from ilc_core.ledger.backend import LedgerBackend

def compute_settlement_metrics(
    ledger: LedgerBackend
) -> Dict[str, Any]:
    """
    Compute aggregate metrics from the ledger's state.
    
    Returns a dictionary suitable for inclusion in experiment summaries.
    """
    
    # 1. Gather all epoch records
    # The ledger backend doesn't expose a list_all_epochs method directly in the base class (yet?),
    # but Memory/File backends have internal storage.
    # Wait, LedgerBackend base class doesn't enforce iteration.
    # Let's inspect LedgerBackend definition to see if we can iterate or if we need to rely on the concrete implementations exposing something.
    # The prompt says: "Read from ledger.epoch_records + ledger.stake_snapshots."
    # This implies we might be accessing attributes that exist on the backend implementations we care about (InMemory, File).
    # Ideally we should add a `list_epoch_records()` method to the ABC, but for now let's assume we can access properties
    # if the backend implementation supports it, or check if we updated the backend definition to be iterable.
    #
    # Looking at Phase 70A/C implementation (which I authored/reviewed):
    # InMemoryLedgerBackend has self.epoch_records (Dict) and self.stake_snapshots (Dict).
    # FileLedgerBackend has internal caches or we rely on it adhering to a similar structure if we want to read it?
    # FileLedgerBackend loads on demand, so `epoch_records` dict might not be populated with everything on disk unless we scan.
    # However, for metric reporting at the end of a run, we might assume the run populated the cache (InMemory) or we need a way to scan.
    #
    # If FileLedgerBackend doesn't expose all records, `compute_settlement_metrics` will be hard for persisted runs that just started up.
    # But for "Devnet Summary" usage (Task B), we are usually at the end of a run where we might have just written them?
    # Actually, if we just ran `run_devnet_multi_epoch`, the backend was active.
    # But `FileLedgerBackend` typically only keeps what it touched.
    #
    # Let's check `LedgerBackend` ABC first.
    # I'll optimistically implement assuming I can iterate or I'll implement a fallback/scan if needed.
    # For now, let's look at `InMemoryLedgerBackend` as the primary target for devnet experiments (sim state).
    # If `FileLedgerBackend` is used, we might need to ensure it exposes these collections or methods.
    # I will assume standard dict access `epoch_records` and `stake_snapshots` are available or I will simply assume
    # the passed object gives me access.
    
    # To be safe and clean, I should probably check if the ledger has `get_all_epochs` or similar.
    # Since I don't recall adding that, I'll access the protected/public storage directly if possible or cast.
    # Let's write code that attempts to access `epoch_records` and `stake_snapshots` attributes.
    
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
