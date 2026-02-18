# ILC Capability-Proof Activation Readiness Gates v0.1

Status: planning artifact  
Date: 2026-02-18  
Scope: readiness criteria and roadmap placement for CapProof, AWP/IIH, and QATPS coupling

## 1. Purpose

Define deterministic go/no-go gates for implementing and activating capability-proof features while preserving ratified constitutional invariants.

This artifact is sequencing guidance. It does not ratify economic policy.

## 2. Current Readiness Assessment

| Surface | Implementation confidence (today) | Activation confidence (today) | Notes |
|---|---:|---:|---|
| CapProof (pricing/scheduling only) | 0.80 | 0.65 | design detail is strong; runtime integration and anti-gaming checks still needed |
| AWP/IIH (challenge proof pipeline) | 0.60 | 0.45 | determinism/audit can be built; economic linkage requires more validation |
| AWP pool split (20%) | 0.70 | 0.40 | policy is designed but not ratified or stress-validated |
| QATPS/CIT runtime reward coupling | 0.50 | 0.35 | high gaming surface; requires adversarial simulation before activation |
| Ingenuity scoring (barrier-mode) | 0.35 | 0.25 | research-stage; keep isolated from economic activation in first pass |

## 3. Readiness Gates

## Gate A — CapProof Contract Freeze (Design -> Build)

Pass criteria:
1. Contract spec locks probe schemas, tolerance rules, and fail-closed behavior.
2. Explicit invariant: capability probes must not mint additional ILC directly.
3. Boundary contract enforced: no user-supplied kernels/backend hints in payload.
4. Canonical serialization and signing contract for capability vectors is fixed.

Blockers if failed:
- Any unresolved ambiguity in probe determinism, replay format, or no-direct-reward rule.

## Gate B — CapProof Shadow-Mode Verification (Build -> Trial)

Pass criteria:
1. Deterministic replay passes across supported environments for fixed seeds.
2. Spot-check and anti-tamper checks produce expected fail-closed behavior.
3. Runtime overhead remains inside predefined budget.
4. Existing invariants remain green (refutation profitability, diversity, freshness, governor).

Blockers if failed:
- Non-deterministic outputs, tolerance drift, or regression in constitutional gates.

## Gate C — AWP/IIH Proof Pipeline (Trial -> Pre-Economic)

Pass criteria:
1. Challenge-set generation is unpredictable pre-epoch and reproducible post-epoch.
2. IIH proof bundle schema, hashing, and signature verification are deterministic.
3. Spot-audit recomputation matches within contract bounds.
4. Fraud detection path and penalty signaling are test-covered.

Blockers if failed:
- Replay ambiguity, unverifiable bundles, or weak anti-fraud audit behavior.

## Gate D — Economic Coupling Decision (Pre-Economic -> Economic Activation)

Pass criteria:
1. Policy decision for AWP pool split is ratified (or explicitly deferred).
2. Adversarial sims show no inversion of constitutional invariants.
3. Sybil/collusion stress tests stay within accepted risk thresholds.
4. Activation guardrails and rollback plan are documented.

Blockers if failed:
- Any simulation evidence of incentive inversion or unresolved policy status.

## Gate E — QATPS/CIT Activation (Optional Late Step)

Pass criteria:
1. Throughput/latency metrics are deterministic and robust to gaming.
2. Coupling with existing reward logic passes full regression suite.
3. Economic fairness and anti-gaming metrics remain inside approved bounds.

Blockers if failed:
- Token-spam or throughput manipulation vectors that materially affect payouts.

## 4. Roadmap Placement

These features should not be inserted into the active 222-229 Genesis packaging closure sequence.

Recommended placement:

1. **Finish current line first**  
   - Complete phases 227, 225, 228, 229 closure.

2. **Start a dedicated post-Genesis capability-proof sequence** (proposed next mainline window)
   - sequence lock + scope gate,
   - CapProof contract freeze and shadow-mode implementation,
   - AWP/IIH proof pipeline in non-economic mode,
   - economic coupling decision/ratification,
   - optional QATPS/CIT activation as a later step,
   - closure and handoff.

3. **Keep ingenuity scoring in research lane initially**  
   - align with Levin-barrier roadmap track and only couple into economics after separate validation.

## 5. Dependencies and Constraints

1. Open security CDL path (`CDL-001`, `CDL-002`, `CDL-007`) remains a hard dependency for any production-grade activation.
2. Capability-proof work must preserve current ratified invariants and replay determinism.
3. Economic activation requires decision-log routing for unresolved policy choices (split values, thresholds, fallback behavior).

## 6. Canonical Anchors

- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/ilc_mining_economics_and_bootstrapping_strategy_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_phase_226_open_cdl_security_triage_v0.1.md`
- `docs/specs/ilc_reviewer_context_pack_v0.2_delta.md`
- `TODO.txt`
