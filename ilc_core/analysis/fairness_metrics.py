"""
Fairness metrics analysis module for Phase 63A.

This module provides offline analysis utilities for SIM-63A to evaluate
fairness and economic distribution (Gini, skill-reward correlation)
and simulate ECU-style β/θ payout reweighting.

These functions are strictly for analysis and do not affect the core protocol
consensus or runtime behavior.
"""

from typing import Sequence, Mapping, Dict, Tuple
import math

def compute_gini(values: Sequence[float]) -> float:
    """
    Compute the Gini coefficient for a sequence of non-negative values.
    Returns 0.0 for empty or all-equal / all-zero input.
    
    The Gini coefficient measures inequality:
    0.0 = perfect equality (everyone has same value)
    1.0 = maximal inequality (one person has everything, others zero)
    """
    if not values:
        return 0.0
    
    # Defensive: clip negatives to 0.0 and filter
    # Just clip in place list
    vals_sorted = sorted([max(0.0, v) for v in values])
    n = len(vals_sorted)
    
    if n == 0:
        return 0.0
        
    total = sum(vals_sorted)
    if total <= 1e-12:
        return 0.0
        
    # Standard Gini formula:
    # G = (2 * sum(i * x_i) - (n + 1) * sum(x_i)) / (n * sum(x_i))
    # where x_i are 1-based indexed sorted values.
    # Using 1-based index i=1..n
    
    sum_ix = sum((i + 1) * val for i, val in enumerate(vals_sorted))
    
    gini = (2.0 * sum_ix - (n + 1) * total) / (n * total)
    return max(0.0, min(1.0, gini))

def compute_pearson_corr(xs: Sequence[float], ys: Sequence[float]) -> float:
    """
    Compute Pearson correlation coefficient between xs and ys.
    Returns 0.0 if lengths mismatch, empty, or variance is zero.
    """
    if len(xs) != len(ys) or len(xs) == 0:
        return 0.0
        
    n = len(xs)
    
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    
    # Covariance and variances
    cov = 0.0
    var_x = 0.0
    var_y = 0.0
    
    for x, y in zip(xs, ys):
        dx = x - mean_x
        dy = y - mean_y
        cov += dx * dy
        var_x += dx * dx
        var_y += dy * dy
        
    if var_x < 1e-12 or var_y < 1e-12:
        return 0.0
        
    return cov / math.sqrt(var_x * var_y)

def apply_beta_theta_payouts(
    skills: Mapping[str, float],
    rewards: Mapping[str, float],
    beta: float,
    theta: float,
) -> Dict[str, float]:
    """
    Given per-agent skill and base rewards, return a new mapping of
    'ECU-like' payouts under a simple β/θ rule:

    - skills are assumed in [0, 1] (caller is responsible for normalizing).
    - θ is a skill threshold in [0, 1].
    - β controls how aggressively we amplify high-skill vs low-skill agents.

    Rule:
        if skill < theta:
            weight = (skill / max(theta, 1e-9)) ** max(beta, 0.0)
        else:
            # Above threshold we ramp linearly with a β gain
            excess = (skill - theta) / max(1.0 - theta, 1e-9)
            # weight = 1.0 + beta * excess  (Prompt suggestion)
            # Wait, prompt says: "weight = 1.0 + beta * excess"
            # Let's ensure continuity? 
            # If skill=0.99, theta=0.8, excess = 0.19/0.2 = ~0.95. w = 1 + beta*0.95.
            # If skill=0.8, theta=0.8. low_branch: (0.8/0.8)^beta = 1. high_branch: 1+0 = 1.
            # Continuity holds at skill=theta.
            
            weight = 1.0 + beta * excess

        payout = rewards[agent] * weight

    Agents missing in either mapping get 0.0 payout.
    """
    payouts = {}
    
    # Avoid zero division
    denom_theta = max(theta, 1e-9)
    denom_above = max(1.0 - theta, 1e-9)
    safe_beta = max(beta, 0.0)
    
    # Iterate over all agents present in EITHER (treat missing as 0 skill / 0 reward)
    all_agents = set(skills.keys()) | set(rewards.keys())
    
    for agent_id in all_agents:
        skill = skills.get(agent_id, 0.0)
        base_reward = rewards.get(agent_id, 0.0)
        
        # Clamp skill just in case
        skill = max(0.0, min(1.0, skill))
        
        if skill < theta:
            # Power law drop-off below threshold
            # Normalized relative to theta
            ratio = skill / denom_theta
            weight = math.pow(ratio, safe_beta)
        else:
            # Linear boost above threshold
            excess = (skill - theta) / denom_above
            weight = 1.0 + beta * excess
            
        payouts[agent_id] = base_reward * weight
        
    return payouts

def summarize_fairness(
    skills: Mapping[str, float],
    payouts: Mapping[str, float],
) -> Tuple[float, float, float]:
    """
    Return (gini, skill_reward_corr, top10_share).

    - gini: Gini of payouts.
    - skill_reward_corr: Pearson correlation between skill and payout.
    - top10_share: Total payout of top 10% of agents / total payout.
    """
    # Align lists for correlation (use 0.0 if missing)
    all_agents = sorted(list(set(skills.keys()) | set(payouts.keys())))
    
    xs = [] # skills
    ys = [] # payouts
    
    for aid in all_agents:
        xs.append(skills.get(aid, 0.0))
        ys.append(payouts.get(aid, 0.0))
        
    gini = compute_gini(ys)
    corr = compute_pearson_corr(xs, ys)
    
    # Top 10% Share
    # Sort payouts desc
    payouts_sorted = sorted(ys, reverse=True)
    total_payout = sum(payouts_sorted)
    
    if total_payout <= 1e-12:
        top10_share = 0.0
    else:
        n = len(payouts_sorted)
        cutoff = max(1, int(math.ceil(0.1 * n)))
        top_slice = payouts_sorted[:cutoff]
        top10_share = sum(top_slice) / total_payout
        
    return gini, corr, top10_share

def _pb_validate_inputs(gating_mode: str) -> None:
    """Validate gating mode input."""
    if gating_mode not in ("none", "soft", "strict"):
        raise ValueError(f"Unknown gating_mode: {gating_mode}")

def _pb_apply_boost_and_conserve(
    base_payouts: Dict[str, float],
    pb_set: set[str],
    pb_intensity: float
) -> Dict[str, float]:
    """Apply PB boost and optionally scale down others to roughly conserve total."""
    pb_boosted = {}
    
    # Naive boost
    for aid, val in base_payouts.items():
        if aid in pb_set:
            pb_boosted[aid] = val * (1.0 + pb_intensity)
        else:
            pb_boosted[aid] = val
            
    # Calculate extra minted
    extra = sum(pb_boosted[a] - base_payouts.get(a, 0.0) for a in base_payouts if a in pb_set)
    pool_others = sum(base_payouts[a] for a in base_payouts if a not in pb_set)
    
    # Scale down others if needed to roughly conserve pie BEFORE gating
    if pool_others > 1e-9 and extra > 0:
        scale_others = max(0.0, 1.0 - extra / pool_others)
        for aid, val in base_payouts.items():
            if aid not in pb_set:
                pb_boosted[aid] = val * scale_others
                
    return pb_boosted

def _pb_apply_gating_logic(
    base_payouts: Dict[str, float],
    pb_boosted: Dict[str, float],
    pb_set: set[str],
    gating_mode: str,
    pb_intensity: float,
    gestation_epochs: int
) -> Dict[str, float]:
    """Apply gating rules (none, soft, strict) to boosted payouts."""
    gated = {}
    
    # Precompute soft factor
    soft_denom = 1.0 + max(0, gestation_epochs) * max(0.0, pb_intensity)
    soft_factor = 1.0 / soft_denom
    
    for aid in base_payouts.keys(): # Iterate original keys to ensure stability
        val_boosted = pb_boosted.get(aid, 0.0)
        base_val = base_payouts.get(aid, 0.0)
        
        if gating_mode == "none":
            gated[aid] = val_boosted
            
        elif gating_mode == "soft":
            if aid in pb_set:
                uplift = max(0.0, val_boosted - base_val)
                gated[aid] = base_val + uplift * soft_factor
            else:
                gated[aid] = val_boosted
                
        elif gating_mode == "strict":
            if aid in pb_set:
                gated[aid] = base_val # Revert boost completely
            else:
                gated[aid] = val_boosted
                
        # Clamp negative guard
        gated[aid] = max(0.0, gated.get(aid, 0.0))
        
    return gated

def _pb_renormalize_payouts(
    gated: Dict[str, float],
    target_total: float
) -> None:
    """In-place renormalize gated payouts to match target total."""
    sum_gated = sum(gated.values())
    if sum_gated > 1e-9 and target_total > 1e-9:
        scale = target_total / sum_gated
        for k in gated:
            gated[k] *= scale

def apply_pb_farming_and_gating(
    base_payouts: Dict[str, float],
    pb_agent_ids: Sequence[str],
    pb_intensity: float,
    gating_mode: str,
    gestation_epochs: int,
) -> Dict[str, float]:
    """
    Simulate Principal/Bounty (PB) farming boosts and subsequent subjective gating.

    1. PB Boost: Agents in pb_agent_ids get scaled by (1 + pb_intensity).
       We preserve total reward by scaling down non-PB agents if extra value is minted.
    2. Gating:
       - "none": PB boost is fully realized.
       - "soft": PB boost is dampened by gestation_epochs (1 / (1 + gest * intensity)).
       - "strict": PB boost is completely removed, reverting PB agents to base reward.
    3. Renormalization: Ensure total sum equals sum(base_payouts).

    Args:
        base_payouts: Baseline rewards from simulation.
        pb_agent_ids: List of agents acting as "PB farmers".
        pb_intensity: Strength of the PB mechanism (0.0 to 1.0+).
        gating_mode: "none", "soft", or "strict".
        gestation_epochs: Severity of the gating hysteresis.

    Returns:
        New payout dictionary with gating applied.
    """
    _pb_validate_inputs(gating_mode)
        
    total_base = sum(base_payouts.values())
    pb_set = set(pb_agent_ids)
    
    # 1. PB Boost & Conservation
    pb_boosted = _pb_apply_boost_and_conserve(base_payouts, pb_set, pb_intensity)

    # 2. Apply Gating
    gated = _pb_apply_gating_logic(
        base_payouts, pb_boosted, pb_set,
        gating_mode, pb_intensity, gestation_epochs
    )

    # 3. Final Renormalization
    _pb_renormalize_payouts(gated, total_base)
            
    return gated

import numpy as np

def compute_group_roi_ratio(
    payouts: Dict[str, float], 
    pb_agent_ids: Sequence[str]
) -> Tuple[float, float, float]:
    """
    Compute ratio of average rewards: PB-Group / Honest-Group.
    
    Returns:
        (pb_mean, honest_mean, ratio)
    """
    pb_ids = set(pb_agent_ids)
    
    # Filter only agents present in payouts
    pb_vals = [payouts[a] for a in payouts if a in pb_ids]
    honest_vals = [payouts[a] for a in payouts if a not in pb_ids]
    
    pb_mean = float(np.mean(pb_vals)) if pb_vals else 0.0
    honest_mean = float(np.mean(honest_vals)) if honest_vals else 0.0
    
    ratio = pb_mean / honest_mean if honest_mean > 1e-9 else 0.0
    return pb_mean, honest_mean, ratio
