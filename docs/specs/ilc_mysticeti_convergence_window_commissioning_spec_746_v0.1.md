# ILC Mysticeti Convergence Window Commissioning Spec 746 v0.1

**Phase:** 746  
**Window:** 745-748  
**Date:** 2026-04-20  
**Author:** Codex

`mysticeti_convergence_window_commissioned`
`convergence_window_phase_budget_six`
`convergence_window_not_open_until_all_entry_artifacts_exist`

## 1. Purpose and boundary

Phase `746` commissions the later Mysticeti convergence window as a bounded
main-lane window. It does not open that window now, and it does not claim row
closure, `CDL-017` ratification, or Option B graduation in Phase `746`.

This commissioning spec exists to:

1. define the exact artifact-gated entry conditions for the later convergence
   window,
2. fix the convergence window to a bounded six-phase budget,
3. define the only authorized outputs for that later window,
4. define what remains explicitly excluded even inside the convergence lane,
5. accept ADR-0031 as a housekeeping-only status advance because the required
   proto contract is already present in `ilc_app.proto`.

The legal positioning technical facts annex remains deferred non-gate
carry-forward. It is not part of this phase or this window.

## 2. Entry conditions and authority order

The convergence window may not open until every required artifact class exists
and is re-verified by that later window's own sequence lock.

`convergence_entry_artifact_class_a_row7_bundle_defined`
`convergence_entry_artifact_class_b_sim_leakage_results_defined`
`convergence_entry_artifact_class_c_exitability_drill_defined`
`convergence_entry_matrix_recorded_without_open_claim`

The required artifact classes are:

1. **Row-7 censorship-resistance runtime artifact bundle**  
   This artifact class must satisfy the Phase `741` Section `3.2` contract:
   explicit `N=4`, `F=1`, `MaxRound=5`, and `Liveness` mapping back to the
   Phase `698` proof basis, plus the live censoring-validator evidence bundle.
   The currently expected carrier is:
   `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`

2. **Row-5 `SIM-LEAKAGE-01` execution results**  
   This artifact class must satisfy the Phase `740` commissioning contract:
   all three attacker variants exercised, pass/fail measurement against the
   `0.45` / `0.60` linkage recall bands, and explicit observability-floor
   mapping. The currently expected carrier is:
   `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md`

3. **Strong-exitability drill results**  
   This artifact class must satisfy the Phase `741` strong-exitability contract:
   export, independent verify, replay on a fresh node, and migrate without
   original-operator consent. A committed results artifact is required before
   the later convergence window can close row `7`.

Authority order for entry is:

1. committed artifact presence,
2. explicit artifact-content re-verification against the relevant Phase `740`
   and Phase `741` contracts,
3. later convergence-window sequence-lock confirmation,
4. only then any row-closure or Option B graduation-gate work.

Phase labels remain secondary. If Gemini later renumbers or repackages these
artifacts, the artifact class controls.

## 3. Current satisfaction matrix at commission time

At Phase `746` commission time, the later convergence window remains closed.

`convergence_window_entry_not_yet_satisfied_in_phase_746`

Current matrix:

| Artifact class | Current carrier / expectation | Phase 746 posture |
|---|---|---|
| Row-7 censorship bundle | `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md` | committed carrier now exists in the repo, but the later convergence sequence lock must re-verify it before row-7 closure work can begin |
| Row-5 `SIM-LEAKAGE-01` results | `docs/research/ilc_sim_leakage_01_results_M021_v0.1.md` | not present yet |
| Strong-exitability drill results | carrier to be defined by Gemini handoff / convergence packet | not present yet |

Because all three artifact classes are not yet present and re-verified
together, Phase `746` does not open the convergence window.

This preserves the Phase `745` discipline that the live main-lane Track B line
is still taken from `STATUS.md` tail (`M-019` complete; `M-020` next) while
allowing the commissioning spec to name the currently expected committed
artifact carriers honestly.

## 4. Six-phase budget for the later convergence window

The commissioned later convergence window is authorized for exactly six phases:

1. convergence sequence lock and artifact-entry verification,
2. row `5` runtime-closure evaluation using committed `SIM-LEAKAGE-01` results,
3. row `7` censorship-resistance runtime-closure evaluation using the committed
   live artifact bundle,
4. row `7` strong-exitability runtime-closure evaluation using committed drill
   results,
5. row `8` disposition plus Option B graduation-gate synthesis under ADR-0028,
6. coherence report, capsule, and closure gate.

`convergence_window_six_phase_budget_locked`

No extra ratification or runtime-implementation tranche is implied by this
budget. Any future expansion beyond six phases requires a new sequence lock.

## 5. Authorized outputs of the later convergence window

The later convergence window is authorized to produce only the following:

- row `5` runtime-closure verdict,
- row `7` censorship-resistance runtime-closure verdict,
- row `7` strong-exitability runtime-closure verdict,
- row `8` disposition note,
- Option B graduation-gate synthesis under ADR-0028,
- coherence report,
- successor capsule,
- closure gate.

`convergence_window_authorized_outputs_bounded`
`convergence_window_option_b_gate_authorized_not_selection`

Even in that later window, Option B graduation-gate synthesis is not the same
thing as sovereign-substrate selection. The gate may be synthesized only if the
runtime-closure evidence actually supports it.

## 6. Explicit exclusions

This commissioning spec explicitly excludes:

- any row `5` closure claim in Phase `746`,
- any row `7` closure claim in Phase `746`,
- any row `8` advancement in Phase `746`,
- any `CDL-017` ratification claim,
- any sovereign substrate selection,
- any Option B graduation claim,
- any legal positioning technical facts annex work,
- any `ilc_core/` or `ilc_consensus/` mutation.

`phase_746_no_row_closure_claims`
`phase_746_no_cdl_017_ratification`
`phase_746_no_option_b_graduation`

## 7. ADR-0031 housekeeping acceptance

ADR-0031 is accepted in this phase as a housekeeping-only status advance.

`adr_0031_status_accepted_housekeeping_only`
`adr_0031_no_runtime_work_required`

Acceptance basis:

1. `ilc_consensus/proto/ilc_app.proto` already contains `repeated EdgeRecord
   edges = 2;`
2. `ilc_consensus/proto/ilc_app.proto` already contains `repeated
   HyperEdgeRecord hyperedges = 3;`
3. `message EdgeRecord { ... }` already exists in the proto,
4. `message HyperEdgeRecord { ... }` already exists in the proto,
5. no additional runtime, wire-format, or schema mutation is required in this
   phase to satisfy the ADR's original intent.

The ADR file changes status only. No implementation work is performed here.

## 8. Source inputs

- `docs/specs/ilc_phase_745_748_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_745_748_guidance_v0.1.md`
- `docs/specs/ilc_window_739_744_closure_gate_744_v0.1.md`
- `docs/specs/ilc_row_5_runtime_evidence_package_740_v0.1.md`
- `docs/specs/ilc_sim_leakage_01_commissioning_spec_740_v0.1.md`
- `docs/specs/ilc_row_7_runtime_evidence_package_741_v0.1.md`
- `docs/phases/STATUS.md`
- `docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`
- `docs/research/ilc_row_7_runtime_evidence_package_bundle_M020_v0.1.md`
- `docs/research/ilc_external_security_audit_brief_M020_v0.1.md`
- `docs/research/ilc_safety_no_dual_cert_disposition_M020_v0.1.md`
- `docs/adr/ADR_0031_Subgraph_Homomorphism_Query_Contract.md`
- `ilc_consensus/proto/ilc_app.proto`

This commissioning spec remains authoritative until the later convergence
window is packetized by its own sequence lock.
