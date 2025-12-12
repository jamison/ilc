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
