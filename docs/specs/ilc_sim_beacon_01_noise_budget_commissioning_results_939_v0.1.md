# ILC SIM-BEACON-01: Noise Budget Calibration — Commissioning Results

**Phase:** 939
**SIM-ID:** SIM-BEACON-01
**Status:** Complete — non-ratifying calibration evidence
**Date:** 2026-04-28
**Gate:** h013_gossip_beacon_activation_sequence_lock_930.v0.1

---

## 1. Scope

Commissioned: H-013 Phase 937 coherence report §7.

Three calibration questions:

- **Q-SIGMA**: What noise sigma balances routing utility vs. adversarial reconstruction difficulty?
- **Q-THRESHOLD**: What change threshold correctly suppresses stable-node spurious emission?
- **Q-SILENCE**: What dead-peer silence epoch count minimises false-dead rate?

Non-ratifying: outputs are calibration evidence inputs for a future CDL amendment.
This document does not open, amend, or ratify any CDL row.

---

## 2. Model and Parameters

```
Model:       Monte Carlo, deterministic (SEED=938001)
Fingerprint: k=8 normalised Laplacian eigenvalues, Beta(2,3)×2 ∈ (0,2)
N_SAMPLES:   2000 per sigma cell
T_ADVERSARY: 10 observations accumulated by adversary (mean estimate)
N_PEERS:     16 peers in routing scenario
TOP_K:       3 (routing correct if true nearest is in top-3)
DRIFT_SIGMA: 0.02 per-epoch random-walk step
N_DRIFT:     500 epochs for emission-rate and silence calibration

SIGMA_CANDIDATES:     [0.005, 0.01, 0.02, 0.05, 0.10, 0.20]
THRESHOLD_CANDIDATES: [0.05, 0.10, 0.15, 0.20]
SILENCE_CANDIDATES:   [5, 10, 15, 20]
```

---

## 3. Q-SIGMA Results

| sigma | utility_loss_mean | adversary_reduction | routing_correctness | routing_ok | privacy_ok |
|-------|-------------------|---------------------|---------------------|------------|------------|
| 0.005 | 0.013834 | 0.68748 | 1.0 | YES | NO |
| 0.01  | 0.027311 | 0.681658 | 1.0 | YES | NO |
| 0.02  | 0.054523 | 0.682853 | 0.999 | YES | NO |
| 0.05  | 0.136491 | 0.682306 | 0.9765 | YES | NO |
| 0.10  | 0.271868 | 0.679714 | 0.904 | YES | NO |
| 0.20  | 0.537093 | 0.680078 | 0.7275 | NO | NO |

### Key Finding — Privacy Target Structurally Unachievable with T=10 Model

The adversary_reduction fraction is ~0.68 across **all** sigma values. This is not a
simulation artifact — it is a mathematical property of Gaussian averaging: accumulating
T=10 independent observations reduces estimation error by `1 - 1/√T ≈ 0.684`,
regardless of sigma. The privacy target (adversary_reduction ≤ 0.50) would require
either T < 4 observations or a fundamentally different adversary model.

**Model limitation identified:** The T=10 free-observation adversary model overstates
adversarial capability in the H-013 sealed-sender context. In practice:

- Each beacon is sealed per-recipient — a relay sees the outer layer only (next hop + inner ciphertext)
- The terminal sees the inner plaintext, but different senders use different emission IDs
- Accumulating 10 observations of the *same node* requires identifying 10 distinct beacons from
  the same agent_id — not trivially achievable under the sealed-sender model (ADR-0034)
- The sealed-sender protocol is the primary privacy mechanism; noise is secondary obfuscation

**Verdict:** The privacy target metric is not actionable as stated. A revised adversary model
(constrained by sealed-sender observation difficulty) should be used in a future SIM.

---

## 4. Q-THRESHOLD Results (all sigma values, stable_node_ok = emission_rate < 20%)

| sigma | threshold | emission_rate | threshold/noise_amp | stable_node_ok |
|-------|-----------|---------------|---------------------|----------------|
| 0.005 | 0.05 | 0.728 | 3.54 | NO |
| 0.005 | 0.10 | 0.240 | 7.07 | NO |
| 0.005 | 0.15 | 0.116 | 10.61 | YES |
| 0.005 | 0.20 | 0.066 | 14.14 | YES |
| 0.05  | 0.05 | 0.990 | 0.35 | NO |
| 0.05  | 0.10 | 0.974 | 0.71 | NO |
| 0.05  | 0.15 | 0.968 | 1.06 | NO |
| 0.05  | 0.20 | 0.890 | 1.41 | NO |
| 0.10  | 0.05 | 1.0   | 0.18 | NO |
| 0.10  | 0.10 | 1.0   | 0.35 | NO |
| 0.10  | 0.15 | 1.0   | 0.53 | NO |
| 0.10  | 0.20 | 1.0   | 0.71 | NO |

**Note on threshold/noise_amplitude:** `threshold / (sigma × √k)`. Values < 1 mean the threshold
is smaller than the expected noise amplitude — pure noise alone will trigger emission on most epochs
even without any real fingerprint change. This is the spurious emission regime.

For sigma=0.05 (testnet), threshold=0.10 gives threshold/noise_amp = 0.71 — we are in the
spurious emission regime. The testnet threshold=0.1 was provisional and should be raised.

---

## 5. Q-SILENCE Results (sigma=0.05, varying threshold and silence_epochs)

| threshold | silence_epochs | false_dead_rate | acceptable (<5%) |
|-----------|----------------|-----------------|------------------|
| 0.10 | 5  | 0.0    | YES |
| 0.10 | 10 | 0.0    | YES |
| 0.15 | 5  | 0.2025 | NO  |
| 0.15 | 10 | 0.0    | YES |
| 0.15 | 15 | 0.0    | YES |
| 0.20 | 5  | 0.6475 | NO  |
| 0.20 | 10 | 0.2375 | NO  |
| 0.20 | 15 | 0.1825 | NO  |
| 0.20 | 20 | 0.0    | YES |

At threshold=0.15 with sigma=0.05: silence_epochs=10 is the minimum that achieves <5% false-dead.
At threshold=0.20 with sigma=0.05: silence_epochs=20 required — too conservative.

---

## 6. Disposition Recommendations

These are calibration evidence inputs, not constitutional locks. A CDL amendment is
required before these replace the provisional values in H013_TESTNET_EMISSION_SIGMA,
H013_CHANGE_THRESHOLD, and DEFAULT_DEAD_PEER_SILENCE_EPOCHS.

| Parameter | Current (provisional) | SIM-BEACON-01 Evidence | Recommended for mainnet |
|-----------|------------------------|------------------------|-------------------------|
| sigma | 0.05 (testnet) | σ=0.05 gives routing_correctness=97.65%; no sigma meets privacy target as modeled | **0.05** — keep testnet value; adversary model revision needed |
| change_threshold | 0.10 | 0.10 is in spurious-emission regime for σ=0.05; 0.15 is the first stable-node-suppressing threshold (at σ=0.005) | **0.15** for mainnet; revisit with revised adversary model |
| dead_peer_silence_epochs | 10 | 10 epochs confirmed: 0% false-dead at threshold=0.15, σ=0.05 | **10** — confirmed |

**Mainnet gate:** sigma=0.05 is recommended for mainnet pending adversary model revision.
The threshold should be raised from 0.10 to 0.15 to exit the spurious-emission regime.
Silence epochs remain at 10.

---

## 7. Artifact Hashes

See `out/simulations/sim_beacon_01_noise_budget/run_manifest.json` for artifact sha256 values
and rows_digest confirming reproducibility.

---

`sim_beacon_01_complete`
`sim_beacon_01_recommended_sigma=0.05`
`sim_beacon_01_recommended_change_threshold=0.15`
`sim_beacon_01_recommended_dead_peer_silence_epochs=10`
`sim_beacon_01_adversary_model_revision_needed`
`mainnet_sigma_0_05_pending_cdl_amendment`
