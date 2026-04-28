# CDL-082: H-013 Gossip Beacon Emission Threshold Amendment

**Status:** RATIFIED
**Opened:** Phase 948 (2026-04-28)
**Ratified:** Phase 950 (2026-04-28)
**Authority:** CDL-079 (H-013 activation); SIM-BEACON-01 evidence (Phase 939)
**Amends:** H-013 gossip beacon emission parameters (`ilc_core/node/node_startup_runtime.py`)

---

## 1. Problem Statement

`H013_CHANGE_THRESHOLD: float = 0.1` was set at H-013 activation (Phase 938) as a provisional
value. SIM-BEACON-01 (Phase 939) found that this value places the gossip beacon emission system
in a **spurious-emission regime**:

- Small spectral perturbations — below the threshold of meaningful network topology change —
  trigger unnecessary beacon emissions, wasting bandwidth and marginally increasing structural
  correlation leakage.
- `spectral_distance(prev_fingerprint, curr_fingerprint) > 0.10` fires on noise, not signal.

**SIM-BEACON-01 findings:**
- At threshold=0.10: spurious-emission regime confirmed. Stable nodes emit unnecessarily.
- At threshold=0.15: spurious-emission regime exited. Only meaningful spectral change triggers
  emission.
- Routing correctness at sigma=0.05: **97.65%** — unchanged by threshold increase.
- `DEFAULT_DEAD_PEER_SILENCE_EPOCHS = 10` — confirmed unaffected.
- `H013_TESTNET_EMISSION_SIGMA = 0.05` — recommended to keep unchanged.

`H013_CHANGE_THRESHOLD = 0.15` exits the spurious-emission regime without degrading routing
correctness. This is a constitutionally observable parameter: it governs beacon emission
frequency, affecting privacy (fewer emissions = less correlation surface) and bandwidth (direct
reduction in gossip traffic). A CDL amendment is required before any deployment changes this
value.

---

## 2. Human-Gate Decision

**Q1 — Should `H013_CHANGE_THRESHOLD` be raised from 0.10 to 0.15?**

**RESOLVED: Yes.**

Evidence: SIM-BEACON-01 (Phase 939) — `docs/specs/ilc_sim_beacon_01_noise_budget_commissioning_results_939_v0.1.md`

Decision record:
- Value 0.10 (current): spurious-emission regime. Stable nodes emit on noise.
- Value 0.15 (proposed): spurious-emission regime exited. Stable nodes suppress emission.
- Routing correctness impact: none (97.65% at sigma=0.05 confirmed).
- Bandwidth impact: positive (reduced gossip traffic from stable nodes).
- Privacy impact: positive (fewer emissions reduce correlation surface).

`cdl_082_q1_raise_change_threshold_0_10_to_0_15_resolved`

---

## 3. Constitutional Text

```
H013_CHANGE_THRESHOLD: float = 0.15

No deployment may set H013_CHANGE_THRESHOLD to a value other than 0.15 without a subsequent
CDL amendment. The value 0.10 is retired.
```

Runtime mutation target: `ilc_core/node/node_startup_runtime.py`

---

## 4. Out of Scope

This CDL does **NOT** constitute:

- Changes to `H013_TESTNET_EMISSION_SIGMA` — remains 0.05; sigma change requires adversary
  model revision SIM (separate future CDL)
- Mainnet sigma parameter change — adversary model revision required first
- Any change to sealed-sender (ADR-0034) implementation
- Changes to `DEFAULT_DEAD_PEER_SILENCE_EPOCHS = 10` — confirmed unchanged by SIM-BEACON-01
- Any change to spectral routing (H-015) or `PeerFingerprintCache`

The adversary reduction finding (`adversary_reduction ≈ 0.684 = 1 - 1/√T` for T=10 Gaussian
averaging, regardless of sigma) is noted but does not affect this CDL's scope. That finding
applies to the sealed-sender adversary model revision — a separate future SIM.

---

## 5. Ratification Gate

Pre-ratification checklist (to be verified at Phase 950):

```
[x] SIM-BEACON-01 evidence cited — Phase 939 — done
[x] Prelock hardening complete — Phase 949 — done
[x] Runtime mutation committed — H013_CHANGE_THRESHOLD = 0.15 in node_startup_runtime.py — done (Commit 1, Phase 950)
[x] Human ratification authorization — granted Phase 950
```

---

## 6. Two-Commit Ratification Pattern

CDL-082 ratification (Phase 950) follows the established two-commit CDL pattern (CDL-081
precedent, Phases 942–943):

- **Commit 1 (runtime mutation — non-CDL commit):** `ilc_core/node/node_startup_runtime.py`
  — raise `H013_CHANGE_THRESHOLD` from 0.10 to 0.15. No `ILC_CDL_MUTATION_AUTHORIZED` env var.
- **Commit 2 (CDL mutation commit):** This spec OPEN → RATIFIED; CDL log row updated.
  Requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=950`.

Pre-commit hook enforces that CDL-authorized commits must NOT touch `ilc_core/`.

---

---

## 7. Prelock Record

**Prelock phase:** 949 (2026-04-28)
**Opening commit:** `192e58ea` (`feat(cdl): open CDL-082 h013 emission threshold amendment (Phase 948)`)

Historical assertion: at commit `192e58ea`, CDL-082 status was `open`.

Verification command:
```bash
git show 192e58ea:docs/specs/ilc_cdl_082_h013_emission_threshold_amendment_opening_948_v0.1.md \
  | grep "^\*\*Status:"
```
Expected output: `**Status:** OPEN`

`cdl_082_prelock_hardening_complete_phase_949`

---

`cdl_082_open_phase_948`
`h013_change_threshold_amendment_constitutional_basis_established`
`cdl_082_prelock_hardening_complete_phase_949`
`cdl_082_ratified_phase_950`
`h013_change_threshold_0_15_constitutional_lock`
