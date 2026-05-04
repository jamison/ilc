# ILC Phase 1166-1175 Sequence Lock v0.1

**Date:** 2026-05-04
**Status:** committed
**Window:** 1166-1175
**Phase:** 1166

`window_1166_1175_sequence_lock_committed`

---

## 1. Authorization and Boundary

Window 1166-1175 was approved for Strike Force execution through non-sensitive Phases
1166-1171 by explicit human authorization:

`GO Strike Force Phase 1166-1171`

This sequence lock does not authorize Phase 1172 or Phase 1175. Phase 1172 remains
conditional and SENSITIVE; it requires `sim_spectral_05_gate_pass` and explicit
`GO Phase 1172`. Phase 1175 remains SENSITIVE and requires explicit `GO Phase 1175`.

No CDL mutation, runtime mutation, signed v0.1 mutation, v0.2 signing, release-key
generation, or public-RC action is authorized by this sequence lock.

---

## 2. Window Header

| Field | Value |
|-------|-------|
| Window | 1166-1175 |
| Baseline capsule | `docs/specs/ilc_antigravity_context_capsule_v5.41.md` |
| Incoming handoff | `docs/specs/ilc_window_1156_1165_handoff_1165_v0.1.md` |
| Prior closure commit | `265e4b58` (`window_1156_1165_closed_phase_1165`) |
| Current guidance | `docs/specs/ilc_window_1166_1175_candidate_phase_grouping_v0.1.md` |
| Phase prompts | `docs/phases/phase_1166_*` through `docs/phases/phase_1175_*` |
| CDL frontier | CDL-084 ratified; CDL-085 SIM-gated |
| Runtime frontier | `epoch_attribution_settle_runtime_1129_fix1.v0.5` |
| Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Unsigned Atlas candidate | v0.2 candidate, 41 nodes / 73 edges, unsigned |

---

## 3. Carry-Forward Intake

| Carry-forward | Window 1166-1175 routing |
|---------------|--------------------------|
| `cdl_085_sim_gated_pending_sybil_discrimination_resolution` | Phases 1169-1171 SIM-SPECTRAL-05; Phase 1172 conditional only |
| `sim_spectral_05_structural_impedance_and_spectral_discriminant_calibration_required` | Phase 1169 Track A |
| `sim_spectral_05_branchial_claim_state_projection_required` | Phases 1170-1171 Track B |
| `sim_spectral_05_multi_slice_observer_convergence_framework_required` | Phase 1168 program spec and framework |
| `genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr` | Phase 1167 ADR-0037 scope |
| `genesis_equivalence_and_merge_policy_required_for_lineage_contract_adr` | Phase 1167 ADR-0037 scope |
| `popperian_equivalence_criterion_required_as_merge_gate_in_lineage_contract_adr` | Phase 1167 ADR-0037 scope |
| `genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036` | Phase 1167; ADR-0037 is the separate Lineage Contract ADR |
| v0.2 signing ceremony | Deferred to Window 1176+; not authorized here |
| ADR-0036 acceptance review | Phase 1173, after ADR-0037 and SIM-SPECTRAL-05 disposition |
| Tier-3 runtime linkage | Carry-forward only; ADR-0020 governance prerequisite is met, runtime lane separate |
| Truth-primitive permanence community ratification | Carry-forward only |
| Contributor agreement / license / trademark | Counsel track carry-forward |
| Canon bundle signing repair | Tooling debt carry-forward |

---

## 4. Locked Phase Order

| Phase | Topic | Sensitivity | Execution status |
|-------|-------|-------------|------------------|
| 1166 | Window sequence lock | NON-SENSITIVE | authorized |
| 1167 | ADR-0037 Genesis Canonical Lineage Contract draft | NON-SENSITIVE | authorized |
| 1168 | SIM-SPECTRAL-05 program spec + multi-slice framework | NON-SENSITIVE | authorized |
| 1169 | SIM-SPECTRAL-05 Track A structural discriminant calibration | NON-SENSITIVE | authorized |
| 1170 | SIM-SPECTRAL-05 Track B branchial projection build | NON-SENSITIVE | authorized |
| 1171 | SIM-SPECTRAL-05 Track B run + combined disposition | NON-SENSITIVE | authorized |
| 1172 | CDL-085 opening | SENSITIVE / conditional | not authorized |
| 1173 | ADR-0036 + ADR-0037 acceptance reviews | NON-SENSITIVE | not in current Strike Force GO |
| 1174 | Coherence report + capsule v5.42 | NON-SENSITIVE | not in current Strike Force GO |
| 1175 | Closure gate | SENSITIVE | not authorized |

---

## 5. Sequencing Inversion

ADR-0037 Genesis Canonical Lineage Contract must be drafted before SIM-SPECTRAL-05
executes. The provenance equivalence criterion defined in ADR-0037 §3.2 is a named,
required input to the SIM-SPECTRAL-05 program spec in Phase 1168.

Do not begin Phase 1169 or Phase 1170 until Phase 1168 is committed and the provenance
equivalence criterion has been specified in operational form.

ADR-0037 and ADR-0036 acceptance review is deferred to Phase 1173. ADR-0037 must be
reviewed first in Phase 1173; ADR-0036 consistency is then checked against ADR-0037's
versioning and fork-boundary semantics.

---

## 6. CDL-085 Inherited State

Current state:

`cdl_085_sim_gated_pending_sybil_discrimination_resolution`

Phase 1172 may execute only if both conditions are met:

1. Phase 1171 emits `sim_spectral_05_gate_pass`.
2. Human issues explicit `GO Phase 1172`.

If either condition is absent, Phase 1172 does not execute.

Prior CDL-085 scope references to preserve for Phase 1172:

- `docs/sims/sim_spectral_04/program.md` §5 gate criterion
- `docs/sims/sim_spectral_04/disposition_1162_v0.1.md`
- `docs/research/sim_spectral_04_structural_perturbation_research_1164_v0.1.md`
- `docs/specs/ilc_pre_public_rc_obligations_synthesis_1154_v0.1.md`
- `ilc_constitutional_decision_log_v0.1.md` for CDL number confirmation

---

## 7. SIM-SPECTRAL-04 Diagnosis Inherited by SIM-SPECTRAL-05

SIM-SPECTRAL-04 failed because matched-size S3/S1 did not clear the corrected Run 02
threshold:

- S3/S1 minimum: `0.7805038558408779`
- S3/S1 maximum: `0.8082732092863824`
- Threshold: `0.6416011282246747`

The Phase 1164 correction stands: λ2-based `structural_impedance` is inactive when both
S1 and S3 clear `THETA_FLOOR`. This is a calibration issue; it is not evidence that
λmax or spectral-gap measurements pass against the actual Sybil topology.

Track A must retest λmax, spectral_gap, degree_gini, and THETA_FLOOR sensitivity against
the committed `synthetic_sybil_cluster` topology. The Window 1156-1165 Path 3 z-scores
against Erdos-Renyi random graphs are directional only and are not gate evidence.

---

## 8. Planning Index Update

`docs/PLANNING_INDEX.md` is advanced by Phase 1166 from "Window 1166+ guidance pending"
to "Window 1166-1175 in progress." New sessions should read:

1. Capsule v5.41
2. Window 1166-1175 sequence lock
3. Window 1166-1175 guidance
4. Window 1156-1165 handoff
5. `docs/phases/STATUS.md`

---

## 9. Phase 1166 Result

Phase 1166 commits this sequence lock and records the approved non-sensitive Strike
Force span 1166-1171.

`window_1166_1175_sequence_lock_committed`
