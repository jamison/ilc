# ILC CapProof CDL-115 Ratification Candidate Audit

Phase: `GAP-CAPPROOF-CDL-115-RATIFICATION-CANDIDATE-PREP-00`  
Status: candidate-prep complete  
Date: 2026-10-01  
Sensitivity: NON-SENSITIVE  
Authority boundary: this document does not ratify CDL-115 and does not clear `CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED`.

## §1 — CDL-115 Invariant Inventory

CDL-115 is open and not ratified. The live CDL register records `status_detail: open_not_ratified`, `ratification_status: deferred_until_Gate_A_evidence_or_later_exact_governance_authorization`, and `runtime_activation_status: not_authorized`.

The CDL-115 opening document locks the following ratification-candidate invariant surface:

1. **Five-probe capability-vector inventory:** `GEMMProbe`, `InferProbe`, `GraphProbe`, `BandwidthProbe`, and `DeterminismProbe`.
2. **Capability-vector fields:** `gemm_gops`, `infer_tps`, `bw_gbps`, `graph_mteps`, and `det_pass`.
3. **Single bounded Decimal multiplier:** `b in [Decimal("0.85"), Decimal("1.15")]`.
4. **No-stacking boundary:** CapProof's band is a single bounded multiplier and must not silently stack with passive ECU centrality, Werner reweighting, provenance decay, governance hardware-scale fees, reputation voting-power boosts, validator admission eligibility, or another multiplier lane absent later CDL authority.
5. **No direct ILC mint boundary:** `CAPPROOF_V1_NO_ILC_MINT = true`; CapProof may govern bounded ECU pricing adjustment only.
6. **Runtime shape boundary:** current runtime uses mapping-shaped capability/trust vectors; CDL-115 must not claim a live `TrustVector` dataclass.
7. **Anti-gaming commitments opened for future ratification:** epoch-salted probes, commit-reveal, at least 1 percent spot-check rate before production use, deterministic challenge material, replayable verification, content-addressed probe artifacts, signed capability-vector chain under CDL-092 authority, and future 100 percent fraud slash subject to later value-path authority.
8. **GraphProbe PoSK question:** Phase 1608 must bind Proof of Structural Knowledge to `GraphProbe` without changing the other four probe semantics.
9. **Default-off runtime activation boundary:** CapProof production scoring and epoch wiring remain unauthorized until later ratification and guard clearance.

CDL-115 has six deliberation questions. Current disposition:

| Question | Current disposition |
|---|---|
| Q1 — independent probe normalization vs. aggregate-score normalization | Partially resolved for Gate A by the current implementation: each positive probe metric maps through a unit-interval curve and the four numeric probe scores average before mapping to the bounded band. Production governance should ratify or amend this before guard clearance. |
| Q2 — deterministic weights for the five probe fields | Partially resolved for Gate A: the four numeric fields are equally weighted; `det_pass` is a gate-like lower-bound selector rather than a fifth numeric score. Production governance should explicitly ratify this weighting. |
| Q3 — `det_pass = false` lower-bound vs. hard-fail eligibility | Partially resolved for Gate A only: runtime returns the floor multiplier `Decimal("0.85")` and zero potential, with comments preserving the open CDL question. Production governance must decide whether this remains acceptable or becomes eligibility hard-fail. |
| Q4 — minimum spot-check evidence for Gate A | Gate A is complete for scaffold verification. Post-live production evidence is still required before ratification. |
| Q5 — stake source and due process before fraud slash | Unresolved. No slashing is active, and no stake custody or due-process path is ratified by CDL-115. |
| Q6 — GraphProbe PoSK binding | Partially resolved for Gate A by Phase 1608's challenge-bound, replay-detectable local graph traversal proof. Spectral and consensus-binding admission remain inactive. |

## §2 — Invariant → Evidence Mapping

| CDL-115 invariant | Implementation phase | File:line evidence | Gate A evidence | Verdict |
|---|---|---|---|---|
| Five-probe suite exists | Phase 1606 | `ilc_core/capproof/probe_runner.py:19`, `:26`, `:33`, `:40`, `:46`, `:53`, `:65`, `:77`, `:150`, `:161`; exports in `ilc_core/capproof/__init__.py:7-39` | `3_5probe_suite_complete.result = pass`; probe_count `5`; Phase 1606 test count `15` | pass for scaffold; partial for production because probes are deterministic stubs |
| Capability-vector schema has exact fields and validation | Phase 1606 | `ilc_core/capproof/capability_vector.py:24-34`, `:36-55`, `:57-73`, `:76-96` | `3_5probe_suite_complete.result = pass`; adjacent Phase 1606 tests cover schema validation | pass for schema |
| Bounded Decimal multiplier is single-band `[0.85, 1.15]` | Phase 1606 | `ilc_core/capproof/multiplier.py:10-14`, `:22-39`, `:48-53` | `2_ecu_band_bounded.result = pass`; floor `0.85`; ceil `1.15`; `10000` deterministic fuzz samples | pass for bounded arithmetic; partial for final production weighting policy |
| `det_pass=False` behavior is explicit and non-silent | Phase 1606 and Phase 1607 | `ilc_core/capproof/multiplier.py:25-27`; `ilc_core/epoch/capproof_epoch_init_wiring.py:112-120`, `:123-136` | `2_ecu_band_bounded.det_pass_false_multiplier = 0.85`; tests cover lower-bound behavior | partial because CDL-115 Q3 remains a governance decision |
| No-stacking boundary | Phase 1607 | `ilc_core/epoch/capproof_epoch_init_wiring.py:123-128`; `tools/capproof/verify_gate_a.py` verifies `step4_compute_band_multiplier` excludes forbidden terms | `5_no_stacking_rule.result = pass`; forbidden terms empty; guarded default adjusted amount `100` | pass for current code boundary; partial until production ratifies composition policy |
| No direct ILC mint | Phase 1606, Phase 1607, Phase 1609 | `ilc_core/capproof/probe_runner.py:13`; `ilc_core/epoch/capproof_epoch_init_wiring.py:23-29`, `:123-132`; `tools/capproof/verify_gate_a.py:76-119` | `1_no_ilc_mint.result = pass`; forbidden imports empty; wiring reassertion true | pass |
| Runtime shape uses current mapping/schema surfaces, not a fabricated `TrustVector` dataclass | Phase 1606 and Phase 1607 | `ilc_core/capproof/capability_vector.py:24-34`; `ilc_core/epoch/capproof_epoch_init_wiring.py:112-120` uses `potential` as a Decimal output dimension, not a `TrustVector` dataclass | Covered indirectly by Phase 1606/1607 tests and Gate A conservation/no-stacking checks | pass for non-overclaim |
| Epoch-salted deterministic probe material | Phase 1606 | `ilc_core/capproof/probe_runner.py:16`, `:56-74`, `:80-86`, `:153-179`, `:182-198`, `:201-208` | Probe suite passes; Phase 1606 tests confirm salt validation and salt divergence | pass for scaffold; partial until live production probe evidence exists |
| GraphProbe PoSK challenge binding | Phase 1608 | `ilc_core/capproof/graph_probe_posk.py:16-22`, `:37-64`, `:67-85`, `:88-126`, `:152-191`, `:200-224`, `:227-257` | `4_posk_present.result = pass`; `spectral_not_activated = true`; tamper rejected true; Phase 1608 test count `18` | pass for local challenge-bound substrate; partial because consensus and spectral binding are not active |
| Conservation check for adjusted base ECU | Phase 1607 and Phase 1609 | `ilc_core/epoch/capproof_epoch_init_wiring.py:139-158`, `:191-238`, `:282-285`; `tools/capproof/verify_gate_a.py:221-247` | `6_conservation_equation.result = pass`; base `123.456`; adjusted `123.456000`; test counts 15/15/18 | pass for current arithmetic gate |
| Default-off guard remains active | Phase 1607 | `ilc_core/epoch/capproof_epoch_init_wiring.py:1-6`, `:25-29`, `:206-218` | Gate A source list includes wiring file; V5 confirmed guard line at runtime | pass for default-off state |
| Anti-gaming commitments for commit-reveal, spot-checks, signed CV chain, and slash due process | CDL-115 opening; not yet production implemented | CDL text opens commitments but does not activate them; current code has deterministic, replayable scaffold only | Gate A does not claim post-live production evidence | blocked for production ratification until post-live evidence and value-path authority exist |

Overall candidate verdict: **candidate-ready for Genesis review, not self-ratifying.** Gate A evidence supports drafting a future CDL-115 ratification phase, but the later phase must explicitly resolve the partial and blocked rows above before any guard clearance.

## §3 — Post-Live Production Evidence Requirements

Before CDL-115 ratification or `CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED` clearance, the ratification record should require at least:

1. **Live probe run evidence:** multiple real operator deployments running the five-probe suite with package version, host class, epoch salt, output capability vector, and deterministic replay material.
2. **Independent replay evidence:** a verifier can recompute or validate challenge material and capability-vector commitments without trusting the original reporting process.
3. **Spot-check evidence:** a concrete spot-check rate and sample record, at least the CDL-115-opened minimum of 1 percent before production use unless a later CDL amends it.
4. **Commit-reveal policy:** canonical fields, timing, replay/nullifier behavior, and failure modes for submitted CapProof claims.
5. **Signed capability-vector chain:** signature profile and content-addressing path under CDL-092 authority.
6. **No-stacking production assertion:** a live-source proof that CapProof's band replaces rather than compounds with passive centrality, Werner, provenance, governance fee, reputation, validator admission, or reward multipliers unless explicitly authorized.
7. **No-direct-ILC-mint audit:** a release-candidate source audit and test asserting no CapProof code path can mint, transfer, or settle ILC.
8. **Slashing due-process authority:** if fraud slashing is to be ratified, a separate value-path authority must define stake source, custody, proof standard, appeal/due-process surface, and exact settlement effects.
9. **`det_pass=false` policy:** a ratified answer to whether `det_pass=false` preserves lower-bound multiplier, zeroes benefit while preserving floor, or hard-fails eligibility.
10. **PoSK production boundary:** whether the Phase 1608 local challenge-bound PoSK remains sufficient, or whether spectral/consensus binding must be active first.

## §4 — Current Guard States

`CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED = True` is live in `ilc_core/epoch/capproof_epoch_init_wiring.py:26`.

Current default behavior is intentionally neutral: `process_capproof_epoch_init()` validates inputs, then returns `protocol_executed=False`, `potential_updated=Decimal("0")`, `band_multiplier=Decimal("1.00")`, `cap_adjusted_base_ecu_amount=base`, and `conservation_check_passed=True` while the guard is true.

Activation path:

1. Candidate audit reviewed by Genesis.
2. Future SENSITIVE CDL-115 ratification phase receives exact authorization.
3. Ratification resolves or explicitly accepts the partial and blocked rows in this audit.
4. A separate guard-clear/runtime activation phase changes the guard only after ratification.

This phase performs none of those activation steps.

## §5 — PoSK Status

Phase 1608 implemented a local, challenge-bound GraphProbe PoSK substrate:

- challenge binds `graph_root_hash`, `epoch_salt`, and `epoch`;
- traversal nodes and edges must be canonical, unique, sorted, bounded, and content-addressed;
- proof commitment is recomputed by the verifier;
- replay detection is bounded by `(epoch, proof_commitment)`;
- tampered proof commitments are rejected;
- `POSK_SPECTRAL_NOT_ACTIVATED = True`;
- `POSK_CONSENSUS_BINDING = False`.

This is enough for Gate A's `4_posk_present` invariant. It is not enough to claim spectral PoSK admission, consensus-bound production PoSK, fraud slashing, or production CapProof scoring.

## §6 — Non-Claims

- CDL-115 is not ratified by this phase.
- No CDL register row is mutated by this phase.
- `CAPPROOF_EPOCH_WIRING_NOT_ACTIVATED` is not cleared.
- No CapProof production activation occurs.
- No live probe execution on validators occurs.
- No public-RC package, PyPI, public mirror, or VPS mutation occurs.
- No wallet, LMDB, Atlas, epoch, validator, ECU, ILC, settlement, treasury, reward, or slashing state is mutated.
- No direct ILC mint path is authorized.
- No CapProof reward path is authorized.
- No production spot-check, commit-reveal, signed capability-vector chain, or fraud-slashing process is activated.
- No spectral PoSK admission or consensus binding is activated.
- Gate A synthetic/scaffold evidence is not post-live production evidence.

Output token on phase completion:

```text
capproof_cdl_115_ratification_candidate_prep_complete_GAP_CAPPROOF_CDL_115_RATIFICATION_CANDIDATE_PREP_00
```
