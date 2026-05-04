# ILC Window 1139-1147 Handoff 1147 v0.1

Status: handoff artifact
Date: 2026-05-04
Classification: sensitive closure and carry-forward handoff

---

## 1. Window Identity And Closure Basis

Window 1139-1147 closes the corrected-baseline, Genesis Atlas Tier-1 signing, and
SIM-SPECTRAL-03 lane opened by Phase 1139.

Closure basis:

- Closure phase: Phase 1147.
- Closure gate: `tests/test_phase_1147_window_1139_1147_closure_gate.py`.
- Verdict: PASS.
- Human GO token: `GO Phase 1147`.
- Incoming baseline: Window 1130-1138 CLOSED, capsule v5.38 current at open.
- Current capsule: `docs/specs/ilc_antigravity_context_capsule_v5.39.md`.
- CDL state: unchanged. `CDL-084` remains the ratified attribution frontier;
  `CDL-085` remains unopened and SIM-gated.
- Runtime state: runtime semantics unchanged. One comment-only audit annotation touched
  `ilc_core/analysis/embedding_pipeline.py` in commit `102ed6f2`; runtime version remains
  `epoch_attribution_settle_runtime_1129_fix1.v0.5`.

`window_1139_1147_closed_phase_1147`
`window_1139_1147_closure_gate_verdict=pass`

---

## 2. Run02 Fix2 Corrected Baseline

Phase 1140 reran the committed 333-entry SIM-SPECTRAL-02 Run 02 matrix with the fixed
normalized-lambda2 harness. Phase 1141 declared
`out/sim_spectral_02_run02_fix2_summary.json` the operative corrected comparison
baseline for SIM-SPECTRAL-03.

Key anchors:

- Output: `out/sim_spectral_02_run02_fix2_summary.json`.
- Entry count: 333.
- Addendum: `docs/sims/sim_spectral_02/run02_fix2_disposition_addendum_1141_v0.1.md`.
- Corrected Track A S3/S1 ratio: `0.6416011282246747`.
- Corrected Track A G2/S1 ratio: `0.8640456434014127`.
- Token: `run02_fix2_disposition_addendum_committed_phase_1141`.

The corrected baseline supersedes the pre-fix Run 02 numeric comparison values where
SIM-SPECTRAL-03 uses the corrected harness.

---

## 3. Atlas Tier-1 And Genesis Signing Outcome

Phases 1142, 1142s, and 1143 established the signed 32-node Genesis star map v0.1.

Key anchors:

- Star map: `out/genesis_core_star_map_v0.1.json`.
- Shape: 32 nodes, 55 edges.
- Signed root envelope:
  `out/genesis_signing_root_envelope_v0.1.json`.
- Public signature: `out/genesis_signing_root_envelope_v0.1.sig`.
- Root envelope hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
- All 32 nodes carry `genesis_attested=true`, `signature_status=signed`, and
  `star_map_version=v0.1`.
- GENESIS-COMPILE-01 checkpoint #1 verdict: `genesis_compile_checkpoint_1_pass`.
- Authority traceability metric: 31 downstream nodes reached from Node 0; 32/32
  authority-grounded nodes included in the signed package.

The 31/32 downstream traversal figure is a measurement convention, not an exclusion of
Node 0. `artifact:genesis_intent_attestation_init_authority_map` is the origin node of
the signed graph and is included in the signed manifest.

Signed-artifact immutability note: `out/genesis_compile_coverage_diagnostic_v0.1.json`
is covered by the Phase 1142s toolchain manifest and must remain at the signed v0.1 hash.
Future regenerated diagnostics should use a new versioned path rather than overwriting the
signed file.

---

## 4. SIM-SPECTRAL-03 Outcome

Phase 1145 reran the corrected 333-entry matrix with one isolated variable change: S1
loaded the signed 32-node Genesis star map as topology seed. Phase 1145a then ran a
bounded topology calibration audit over 180 simulation-overlay variants without mutating
the signed graph.

Result:

- Phase 1145 S1 mean slope: `0.21355627860399237`.
- Phase 1145 S3/S1: `1.6736470076736112`.
- Phase 1145 G2/S1: `2.2539040876901315`.
- Phase 1145a passing variants: `0`.
- Matched-size control: G2/S1 improved to `0.7460347870544758`, but S3/S1 remained
  failing at `0.8310911989859531`.
- Phase 1146 disposition: `CDL-085 recommendation: DEFER`.

The named architectural finding is:

`raw_authority_graph_is_not_the_right_spectral_work_graph`

Interpretation: the signed Genesis star map is valid as an authority graph, but raw
authority topology is not the correct direct substrate for the current spectral
knowledge-work diffusion metric. The next scientific path is a claim-composition
projection, not rejection of the signed Genesis map.

---

## 5. CDL-085 Authorization Status

`CDL-085` remains unopened and SIM-gated. Phase 1146 did not authorize opening or
ratification.

Phase 1146 carry-forward obligations:

- `sim_spectral_04_claim_composition_projection_required_before_cdl_085_reconsideration`
- `genesis_32_node_composability_audit_required`
- `matched_size_controls_required_for_future_spectral_sims`
- `genesis_canonical_lineage_contract_required_before_public_rc`
- `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset`
- `public_rc_envelope_hash_transition_policy_required`
- `contributor_agreement_required_before_public_repo`

Window 1148+ should route CDL-085 away from immediate opening and toward SIM-SPECTRAL-04
claim-composition work unless a human explicitly overrides the Phase 1146 DEFER
recommendation.

---

## 6. Architecture Findings From SIM-SPECTRAL-03

Reference plan:

- `docs/specs/ilc_genesis_claim_composition_projection_plan_1146_v0.1.md`

Key finding:

- The 32-node signed star map is the Genesis authority layer.
- Knowledge work happens at claim/composition granularity.
- SIM-SPECTRAL-04 should test a derived claim-composition projection rather than the raw
  authority graph.
- The Genesis 32-node composability audit must classify each node as primitive,
  historical artifact, parameterized policy, claim composite, or runtime binding pending.

This finding is additive to Atlas Tier-2. Atlas Tier-2 still needs ADR/CDL promotion and
runtime binding preparation; SIM-SPECTRAL-04 needs those results but should not be
collapsed into ordinary star-map edge tuning.

---

## 7. Pre-Public-RC Obligations

The following obligations are not resolved in this window and must be routed before a
public RC:

| Obligation | Owner lane | Note |
|------------|------------|------|
| Genesis Canonical Lineage Contract | ADR/pre-CDL spec | Verify Node 0, signed manifest inclusion, root envelope signature, and release artifact lineage |
| License strategy | Counsel track | Mixed license/sunset strategy requires legal review before public repo |
| Contributor agreement | Counsel / project governance | Required before accepting outside contributions if future relicensing remains possible |
| Trademark / identity policy | Human + counsel | Needed before public launch to reduce namespace-capture and impersonation attacks |
| Truth-primitive permanence | Governance design | Community ratification path required before Genesis sunset |
| Public envelope transition policy | Release engineering | Decide how internal v0.1 root envelopes relate to public RC envelope hashes |
| Canon bundle failures | Tooling debt | `test_canon_bundle_audit_artifact.py` and `test_canon_bundle_pipeline_report.py` currently fail from the canon bundle signing step |

---

## 8. Next-Window Entry Criteria And Routing

Window 1139-1147 is closed. Recommended Window 1148+ entry lanes:

- Atlas Tier-2 governance node promotion and GENESIS-COMPILE checkpoint #2.
- Genesis 32-node composability audit.
- SIM-SPECTRAL-04 claim-composition projection program spec.
- Genesis Canonical Lineage Contract draft.
- Parallel counsel track for license, contributor agreement, and trademark/identity policy.

This handoff does not pre-authorize a CDL opening, public release, license change, or
runtime semantic mutation.

---

## 9. MemPalace Refresh Disposition

- `Disposition:` `required`
- `Active working set impacted:` `yes`
- `Basis:` capsule v5.39, signed 32-node Genesis star map, Phase 1146 DEFER
  disposition, claim-composition projection plan, fork-resistance/license strategy, and
  this handoff materially change the active frontier and retrieval surface.
- `Working-set descriptor:` `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
- `Manifest:` `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
- `Rebuild command:` `bash tools/mempalace/build_active_working_set.sh`

This disposition does not make MemPalace canon. Canon remains committed source artifacts,
gate outputs, specs, capsules, and handoffs.

`window_1139_1147_closed_phase_1147`
`window_1139_1147_closure_gate_verdict=pass`
`sim_spectral_03_cdl_085_defer_carried_forward`
`genesis_claim_composition_projection_carried_forward`
