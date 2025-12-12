"""
Tests for ilc_core/analysis/fairness_metrics.py
"""
import pytest
import math
from ilc_core.analysis.fairness_metrics import (
    compute_gini,
    compute_pearson_corr,
    apply_beta_theta_payouts,
    summarize_fairness
)

def test_compute_gini():
    # 1. Perfect equality
    assert compute_gini([10.0, 10.0, 10.0]) == 0.0
    
    # 2. Max inequality (one has all)
    # Gini of [0, 0, 10] -> ( (2*20 - 4*10) / (3*10) ) ?! 
    # Formula check:
    # vals = [0, 0, 10]
    # sum_ix = 1*0 + 2*0 + 3*10 = 30
    # G = (2*30 - 4*10) / 30 = (60 - 40)/30 = 20/30 = 0.666...
    # Wait, Gini for N=3 where one has all is (N-1)/N? -> 2/3. Correct.
    # Theoretical limit is 1.0 as N -> inf.
    g = compute_gini([0, 0, 10])
    assert abs(g - (2/3)) < 1e-6
    
    # 3. Known value: [0, 1, 2] -> sum=3, n=3
    # vals=[0, 1, 2]. sum_ix = 1*0 + 2*1 + 3*2 = 8
    # G = (2*8 - 4*3) / (3*3) = (16-12)/9 = 4/9 = 0.444...
    assert abs(compute_gini([0, 1, 2]) - (4/9)) < 1e-6
    
    # 4. Empty/Zero
    assert compute_gini([]) == 0.0
    assert compute_gini([0, 0, 0]) == 0.0

def test_compute_pearson_corr():
    # 1. Perfect correlation
    xs = [1, 2, 3]
    ys = [2, 4, 6]
    assert abs(compute_pearson_corr(xs, ys) - 1.0) < 1e-6
    
    # 2. Perfect anti-correlation
    ys_neg = [6, 4, 2]
    assert abs(compute_pearson_corr(xs, ys_neg) - (-1.0)) < 1e-6
    
    # 3. Uncorrelated / Orthogonal
    # xs=[1,2,3], ys=[1, -2, 1] (centered? no)
    # mean_x=2, mean_y=0.
    # dx=[-1, 0, 1], dy=[1, -2, 1]
    # cov = -1 + 0 + 1 = 0
    assert abs(compute_pearson_corr([1, 2, 3], [1, -2, 1])) < 1e-6
    
    # 4. Zero variance
    assert compute_pearson_corr([1, 1, 1], [1, 2, 3]) == 0.0

def test_apply_beta_theta_payouts_monotonicity():
    # Simple check: higher skill should generally yield higher/equal payout given equal base reward,
    # or monotonically strictly increasing payout map if base rewards are equal.
    
    skills = {"a": 0.2, "b": 0.5, "c": 0.8, "d": 0.9}
    base = {k: 100.0 for k in skills}
    
    # Case 1: Beta=1.0, Theta=0.5
    # a (0.2 < 0.5): drop off
    # b (0.5 == 0.5): neutral (weight=1.0)
    # c (0.8 > 0.5): boost
    # d (0.9 > 0.8): bigger boost
    
    payouts = apply_beta_theta_payouts(skills, base, beta=1.0, theta=0.5)
    
    # Check monotonicity
    vals = [payouts[k] for k in ["a", "b", "c", "d"]]
    assert vals[0] < vals[1] < vals[2] < vals[3]
    
    # Check neutral point
    assert abs(payouts["b"] - 100.0) < 1e-6
    
    # Check below threshold behavior (0.2 / 0.5)^1 = 0.4 weight
    assert abs(payouts["a"] - 40.0) < 1e-6
    
    # Check above threshold behavior (0.8 - 0.5)/(1-0.5) = 0.3/0.5 = 0.6 excess
    # weight = 1 + 1*0.6 = 1.6 -> 160.0
    assert abs(payouts["c"] - 160.0) < 1e-6

def test_summarize_fairness():
    skills = {"a": 0.0, "b": 0.5, "c": 1.0}
    payouts = {"a": 10.0, "b": 20.0, "c": 70.0} # highly skewed to c
    
    gini, corr, top10 = summarize_fairness(skills, payouts)
    
    # Gini: [10, 20, 70]. sum=100. sum_ix = 1*10 + 2*20 + 3*70 = 10+40+210 = 260.
    # G = (2*260 - 4*100) / (3*100) = (520 - 400)/300 = 120/300 = 0.4
    assert abs(gini - 0.4) < 1e-6
    
    # Corr should be high (perfect rank correlation)
    assert corr > 0.9
    
    # Top 10% share: 3 items -> top 1 item (c) = 70. 70/100 = 0.7
    assert abs(top10 - 0.7) < 1e-6
