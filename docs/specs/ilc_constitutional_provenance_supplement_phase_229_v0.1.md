# ILC Constitutional Provenance Supplement (Phase 229) v0.1

Status: Phase-229 documentation supplement
Date: 2026-02-18
Primary source: `docs/specs/ilc_constitutional_context_audit_response_v0.1.md`

## 1. Purpose

Preserve provenance and lineage notes routed to the 225/228/229 documentation lane without altering ratified constitutional state.

## 2. SG-01 - issuance framing provenance note

Historical and current issuance framings track different layers:
- historical simulation framing: Genesis siphon reference at task-level reward context (`8 percent` with decaying schedule proposals),
- implemented Genesis governor framing: issuance-share controls (`theta_hard = 1/20`, `theta_soft = exp(-3)`) in `ilc_core/analysis/genesis_accrual_governor.py`.

Interpretation for Genesis packaging:
- these are not contradictory constants on the same axis,
- simulation values remain calibration/design evidence,
- governor constants are the active implementation-bound controls for this release line.

## 3. SG-03 - operational cap targets preserved as non-binding historical evidence

The following simulation-era operational cap targets are preserved as historical design targets (not active Genesis constraints):
- Genesis audits share cap example: `<= 5 percent` of assignments,
- SoV cap example: `<= 15 percent` shard broadcast budget per agent per epoch,
- per-cluster cap example: `<= 25 percent` weight/seats,
- cluster damping concept: `1 reuse + 1 audit` per trust-cluster per epoch.

Disposition:
- retained for post-Genesis governance/economic calibration lanes,
- not required for Genesis constitutional validity because they were not ratified as fixed constants.

## 4. SG-04 - path-lift lineage note

Historical formula framing (HFM-002) emphasizes diminishing returns over depth/difficulty.

Implemented Phase-214 path-lift method (`docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`) computes deterministic witness-level path efficiency and aggregates node-level marginal contribution signals with normalized comparative ranking.

Lineage statement:
- both approaches reward downstream utility contribution with diminishing sensitivity,
- Genesis implementation intentionally uses deterministic, replayable approximation instead of full coalition or runtime-depth recomputation.

## 5. CG-01 - optional calibration note

Historical simulation refutation probabilities (for example, `P(refute|incorrect)` and `P(false_refute|correct)`) are retained as calibration evidence only.

They are not constitutional constants and are not required for Genesis conformance validity.

## 6. Non-ratification statement

This supplement is documentation-only. It does not mutate CDL status, formulas, or ratification records.

## 7. Canonical anchors

- `docs/specs/ilc_constitutional_context_audit_response_v0.1.md`
- `docs/specs/ilc_constitutional_context_audit_v0.1.md`
- `docs/specs/ilc_genesis_accrual_governor_contract_v0.1.md`
- `docs/specs/ilc_path_lift_counterfactual_contract_v0.1.md`
- `docs/specs/ilc_cdl_011_015_ratification_evidence_bundle_v0.1.md`
