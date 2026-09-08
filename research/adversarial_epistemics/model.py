"""
ILC Adversarial Epistemics Research Harness — Formal Model
===========================================================

Formal variable definitions for SIM-CORR-01, SIM-CARTEL-01, and successor SIMs.

Variables
---------
N           Total validator population
E(x)        Validators with sufficient expertise to evaluate claim x
alpha(x)    Adversarial fraction within E(x) — THE critical threat variable
rho         Pairwise epistemic error correlation (0 = fully independent, 1 = identical)
d           Domain expertise depth (0.0–1.0)
R           Selection amplification rate — how reputation advantages compound
delta       Reputation decay rate (Werner CDL-V1)
A           Adversarial budget (fraction of E(x) under adversary control)
I           Information diversity across validators

CDL-V3 Constants (from validator_topology constraints)
------------------------------------------------------
MAX_OPERATOR_FRACTION_PER_PANEL = 0.33   # max 1/3 of jury from same operator cluster
MIN_PANEL_SIZE = 5
DEFAULT_PANEL_SIZE = 7

Werner Economics (CDL-096, CDL-V1)
-----------------------------------
ECU decay is temporal: reputation_t = reputation_0 * exp(-delta * t)
Flow-governing: werner_adjusted = raw_score * (1 + min(0.10, candidate_priority))
Note: WERNER_CREDIT_WIRING_NOT_ACTIVATED is True; these are design targets.

Phase boundary (Werner decay vs. selection amplification):
  delta > R  => ergodic (consensus-quality signal dominates)
  delta < R  => oligarchy (reputation lock-in)

Open research question:
  Can a population of adversarially rational agents be economically incentivized
  to maintain an epistemically useful shared state, when those agents can learn
  the incentive mechanism itself?
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple

# CDL-V3 constants
MAX_OPERATOR_FRACTION_PER_PANEL: float = 1.0 / 3.0
MIN_PANEL_SIZE: int = 5
DEFAULT_PANEL_SIZE: int = 7

# Werner economics parameters (targets, not yet activated)
WERNER_FLOW_CAP: float = 0.10        # max flow-budget bonus
WERNER_DECAY_RATE_DEFAULT: float = 0.05  # delta — fraction per epoch

# Simulation scale defaults
DEFAULT_N_VALIDATORS: int = 1000
DEFAULT_N_OPERATOR_CLUSTERS: int = 10
DEFAULT_N_DOMAINS: int = 5
DEFAULT_TRIALS_PER_CONDITION: int = 10_000
DEFAULT_N_CLAIMS: int = 200          # per trial episode


@dataclass
class SimulationConfig:
    """Top-level configuration for a SIM run."""
    n_validators: int = DEFAULT_N_VALIDATORS
    n_operator_clusters: int = DEFAULT_N_OPERATOR_CLUSTERS
    n_domains: int = DEFAULT_N_DOMAINS
    panel_size: int = DEFAULT_PANEL_SIZE
    trials_per_condition: int = DEFAULT_TRIALS_PER_CONDITION
    n_claims: int = DEFAULT_N_CLAIMS
    werner_decay_rate: float = WERNER_DECAY_RATE_DEFAULT
    random_seed: int = 42

    # Correlation model
    # rho = sigma_shared^2 / (sigma_shared^2 + sigma_independent^2)
    # when total variance = 1: sigma_shared = sqrt(rho), sigma_independent = sqrt(1-rho)

    # Expertise model
    # domain_expertise[domain] drawn from Beta(2, 5) => mean ~0.29, long right tail
    # validator qualifies for E(x) if domain_expertise[domain] >= EXPERTISE_THRESHOLD
    expertise_threshold: float = 0.60

    # Adversarial budget (fraction of E(x) under adversary control, for cartel SIM)
    adversarial_fraction: float = 0.0   # alpha(x)

    # Proportion of false claims in workload (ground truth is False)
    false_claim_rate: float = 0.30


@dataclass
class ExperimentResult:
    """
    Falsifiable experiment result record.
    Format: compatible with ILC truth primitive (assert.truth) submission.
    Every result gets a SHA-384 fingerprint so it can enter the ILC graph
    as a first-class epistemic node.
    """
    sim_id: str                     # e.g. "SIM-CORR-01"
    condition: Dict                 # independent variable values for this row
    metrics: Dict                   # measured outcomes
    config: Dict                    # full SimulationConfig as dict
    n_trials: int = 0
    sha384: str = ""                # filled in by run harness
    run_timestamp_utc: str = ""     # diagnostic only — not used as protocol input
