# ILC Integration Coherence Report 1155 v0.1

Status: pass
Phase: 1155
Date: 2026-05-04
Window: 1148-1156

`coherence_report_1155_verdict=pass`

---

## 1. Verdict

Window 1148-1156 is coherent for closure at Phase 1155.

The window advanced Atlas Tier-2 as an unsigned v0.2 candidate, ran
GENESIS-COMPILE checkpoint #2 against that candidate, closed the Genesis 32-node
composability audit obligation, published the SIM-SPECTRAL-04 program spec, produced the
Genesis Canonical Lineage Contract planning spec, and consolidated pre-public-RC
obligations.

Phase 1156 is not authorized by this closure. The v0.2 candidate remains unsigned.

---

## 2. Constitutional And Runtime Coherence

`CDL-084` remains the ratified attribution frontier.

- `PROVENANCE_DECAY_ALPHA = Decimal("0.45")`
- Runtime frontier: `epoch_attribution_settle_runtime_1129_fix1.v0.5`
- `CDL-085` remains unopened and SIM-gated.
- No CDL mutation occurred in Window 1148-1156.
- No runtime semantic mutation occurred in Window 1148-1156.

The window is consistent with the Phase 1146 DEFER disposition: CDL-085 cannot open until
future SIM-SPECTRAL-04 claim-composition projection evidence supports reconsideration or a
human override explicitly changes that route.

---

## 3. Genesis Atlas Coherence

Signed v0.1 remains the canonical signed Genesis Atlas artifact.

- Star map: `out/genesis_core_star_map_v0.1.json`
- Shape: 32 nodes, 55 edges
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`
- Signed artifacts were not regenerated or overwritten.

Unsigned v0.2 candidate exists as a planning and diagnostic artifact.

- Candidate star map: `out/genesis_core_star_map_v0.2_candidate.json`
- Shape: 36 nodes, 63 edges
- Added ADR nodes: ADR-0019, ADR-0026, ADR-0028, ADR-0031
- New nodes are `signature_status=pending_signing`
- The candidate is not a signed artifact.

This preserves the lineage rule: signed v0.1 is stable; v0.2 candidate references the
Tier-2 planning lane and cannot become canonical-signed without a future key/authorization
event.

---

## 4. Checkpoint #2 Coherence

GENESIS-COMPILE checkpoint #2 passes the authority-traceability gate.

- Source diagnostic: `out/genesis_compile_coverage_diagnostic_v0.2_candidate.json`
- Report: `docs/sims/sim_spectral_02/genesis_compile_checkpoint_2_1150_v0.1.md`
- Authority-traceable core nodes: `36/36`
- Authority ratio: `1.000000`
- Checkpoint token: `genesis_compile_checkpoint_2_pass`

The diagnostic tool still reports `FAIL_CORE_INADEQUATE` on the legacy
basis-reachability/source-explainability verdict. That is expected and not the checkpoint
#2 criterion; it is outside the Phase 1150 authority gate. Phase 1150 explicitly gates on
authority traceability, not legacy basis reachability.

Summary: `FAIL_CORE_INADEQUATE` is expected and not the checkpoint #2 criterion.

---

## 5. SIM-SPECTRAL-04 Coherence

Phase 1151 and Phase 1152 complete the SIM-SPECTRAL-04 planning prerequisites.

- `out/genesis_32_node_composability_audit_v0.1.json`
- `docs/sims/sim_spectral_04/composability_audit_1151_v0.1.md`
- `docs/sims/sim_spectral_04/program.md`

The audit covers all 32 signed v0.1 Genesis nodes and classifies them into:

- `primitive`
- `historical_artifact`
- `parameterized_policy`
- `claim_composite`
- `runtime_binding_pending`

SIM-SPECTRAL-04 remains spec-only in this window. No SIM-SPECTRAL-04 run occurred.

---

## 6. Pre-Public-RC Coherence

The Genesis Canonical Lineage Contract planning spec and Phase 1154 obligations synthesis
correctly route pre-public-RC work without claiming closure.

Carried-forward obligations include:

- formal Genesis Canonical Lineage Contract ADR;
- operational release-key ADR;
- truth-primitive permanence community ratification before Genesis sunset;
- public RC envelope transition formalization;
- contributor agreement before public repo;
- license strategy and trademark/identity counsel track;
- canon bundle signing failure repair;
- ADR acceptance gates for ADR-0008, ADR-0012, ADR-0020, ADR-0022, and ADR-0023.

The documents make no legal conclusion, select no license terms, authorize no public repo,
open no CDL, accept no proposed ADR, and authorize no Phase 1156 signing.

---

## 7. Known Carry-Forward Debt

Known debt is explicit and does not block Phase 1155 closure:

- `test_canon_bundle_audit_artifact.py` and `test_canon_bundle_pipeline_report.py` still
  fail on a pre-existing canon bundle signing root cause.
- Phase 1156 signing is deferred until an operational release key or explicit Genesis
  exceptional signing authorization exists.
- Proposed ADRs remain blocked from Tier-2 promotion until accepted.
- SIM-SPECTRAL-04 execution is deferred to Window 1157+ or later.

---

## 8. Closure Result

Window 1148-1156 may close at Phase 1155.

`coherence_report_1155_verdict=pass`
