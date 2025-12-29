"""
Phase 64D: Economic Accounting Helper.

Provides a transparent "accounting layer" to compute macro-econ metrics
(burn, PB allocation, net issuance) from simulation summaries.
"""
from dataclasses import dataclass
from typing import Optional
from ilc_core.sim.devnet_experiments import DevnetExperimentSummary

@dataclass
class EconAccountingParams:
    burn_rate: float            # 0.0 to 1.0
    pb_rate: float              # 0.0 to 1.0 (Public Benefit)
    starting_vault: float = 0.0 # Optional runway metric

@dataclass
class EconAccountingSummary:
    gross_rewards: float
    burned: float
    pb_allocated: float
    net_issued: float
    vault_delta: float
    ending_vault: float

def compute_econ_accounting(
    summary: DevnetExperimentSummary,
    burn_rate: float,
    pb_rate: float,
    starting_vault: float = 0.0
) -> EconAccountingSummary:
    """
    Compute derived economic metrics from a simulation summary.
    
    Args:
        summary: The experiment summary (containing total_reward).
        burn_rate: Fraction of gross info-reward burned.
        pb_rate: Fraction of gross info-reward allocated to Public Benefit.
        starting_vault: Optional vault balance to add burns to.
        
    Returns:
        EconAccountingSummary with absolute token amounts.
        
    Raises:
        ValueError: If rates are invalid (negative or sum > 1.0).
    """
    # Strict validation (Hardening Step)
    if not (0.0 <= burn_rate <= 1.0):
        raise ValueError(f"Invalid burn_rate: {burn_rate} (must be in [0.0, 1.0])")
    if not (0.0 <= pb_rate <= 1.0):
        raise ValueError(f"Invalid pb_rate: {pb_rate} (must be in [0.0, 1.0])")
    
    # Check sum with slight epsilon for float precision, though inputs are usually clean decimals
    if burn_rate + pb_rate > 1.0000001: 
        raise ValueError(f"burn_rate + pb_rate must be <= 1.0 (got {burn_rate + pb_rate})")
        
    gross = summary.total_reward
    
    # Calculate cuts
    burned = gross * burn_rate
    pb_allocated = gross * pb_rate
    
    # Net Issued = Gross - (Burn + PB)
    net_issued = gross - burned - pb_allocated
    
    # Vault logic: simple accumulation of burned tokens
    vault_delta = burned
    ending_vault = starting_vault + vault_delta
    
    return EconAccountingSummary(
        gross_rewards=gross,
        burned=burned,
        pb_allocated=pb_allocated,
        net_issued=net_issued,
        vault_delta=vault_delta,
        ending_vault=ending_vault
    )
