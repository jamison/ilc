# ILC Phase 853–862 Sequence Lock v0.1

Status: locked
Date: 2026-04-27
Phase: 853
Owner lane: RC1 homoiconic bootstrap — HB-001 + HB-003

`window_853_862_sequence_lock`
`hb_001_hb_003_rc1_window_commissioned`
`truth_primitive_wire_format_precedes_genesis_assertion_schema`
`adm_001_ratification_decision_precedes_hb_001_cdl`

---

## 1. Window Purpose

Window 853–862 delivers the two RC1 homoiconic bootstrap obligations recorded in
the human decision log (2026-04-26 §D7) and carried forward in capsule v5.21 §11:

- **HB-001** — Genesis-authority assertion schema: genesis authority expressed as
  signed `assert.truth` objects verifiable by any agent using the protocol's native
  verification machinery.
- **HB-003** — Layer 0 bundle truth-primitive schema: the truth-primitive schema
  definitions embedded in the Layer 0 protocol bundle so a new participant can
  verify genesis and governance artifacts without out-of-band knowledge.

**HB-002** (peer-to-peer bootstrap distribution) targets RC2+ and is explicitly
excluded from this window.

CDL-070 (PQ migration ceremony) remains deferred; SIM-MONETARY-01 prerequisite
unchanged. This window does not touch CDL-070.

---

## 2. Prerequisite State

| Item | Status at Window Open |
|------|-----------------------|
| HB-001/003 obligations | Named, not yet opened (`homoiconic_bootstrap_forward_obligations_v0.1`) |
| ADM-001 (four-layer distribution) | Proposed — awaiting decision-log ratification |
| Truth primitive wire format ("New Seven") | Designed in ADM-001 §4.0.1; no runtime implementation |
| Current `ALLOWED_PRIMITIVE_TYPES` | `{citation, execution_descriptor, governance_proposal, knowledge_claim, observation}` — not yet extended |
| Genesis loading (Rust) | Pure JSON serde — `RawGenesis` struct in `config.rs`; no assertion objects |
| CDL-070 | Deferred (SIM-MONETARY-01 prerequisite) |
| CDL-071 | Ratified (Phase 851) — temporal tier framework constitutionally explicit |

---

## 3. Hard Pass Condition

Window 853–862 passes only if ALL of the following are true:

1. ADM-001 formal status is decided and recorded (ratified as CDL, kept as ADR,
   or explicitly deferred with a new governance vehicle scoped).
2. The truth-primitive wire format for all seven primitives is specified in a
   locked Phase artifact (`assert.truth`, `validate.claim`, `contradict.assert`,
   `refute.claim`, `revise.assert`, `link.claim`, `commit.epoch`), including
   required fields, canonical serialization, and edge-generation behavior for
   each.
3. A genesis-authority `assert.truth` schema is designed and locked — specifying
   how genesis authority (signer identity, network parameters, validator set)
   maps to signed truth-primitive assertion objects.
4. The Layer 0 bundle schema section is specified — a machine-legible artifact
   containing the truth-primitive schema definitions, structured so that a new
   participant can parse it without a compiled binary.
5. At minimum one CDL (or a single CDL covering both HB-001 and HB-003) is
   ratified, locking the genesis assertion schema and Layer 0 bundle schema
   section into constitutional canon.
6. The Python runtime (`ilc_core/genesis/`) carries at least a reference
   implementation of the genesis assertion schema encoder/verifier.
7. The window does not claim runtime deployment of genesis bootstrap via
   truth-primitive objects on M-009 — that is a subsequent integration milestone.

`window_853_862_hard_pass_condition`

---

## 4. Sequencing Constraints

```
truth_primitive_wire_format_precedes_genesis_assertion_schema
genesis_assertion_schema_precedes_hb_001_cdl_opening
adm_001_status_decision_precedes_hb_001_cdl_opening
layer_0_bundle_schema_spec_precedes_hb_003_cdl_opening
hb_001_and_hb_003_cdl_may_be_single_vehicle
coherence_report_precedes_closure_gate
```

The two CDL items (HB-001 and HB-003) may be opened and ratified as a single
CDL vehicle if the scopes remain cleanly separable within one document. If
entanglement is discovered during Phase 857, they split into two CDLs.

---

## 5. Phase Map

| Phase | Topic | Deliverable |
|-------|-------|-------------|
| 853 | Sequence lock | This document |
| 854 | ADM-001 status audit | Governance decision — ratify as CDL, keep as ADR, or open new CDL vehicle |
| 855 | Truth primitive wire format specification | Locked spec: all seven primitives, required fields, canonical form, edge-generation behavior |
| 856 | Genesis assertion schema design | Spec: how genesis authority maps to signed `assert.truth` objects; field-level schema |
| 857 | HB-001/003 CDL opening | CDL document opened; scope, ratification criteria, evidence checklist |
| 858 | HB-001 implementation | `ilc_core/genesis/assertion_schema.py` — encoder, verifier, canonical form |
| 859 | HB-003 implementation | Layer 0 bundle schema section artifact; machine-legible truth-primitive schema definitions |
| 860 | HB-001/003 CDL ratification | Evidence checklist satisfied; CDL master log updated; tests |
| 861 | Coherence report + capsule v5.22 | Coherence report 861, capsule v5.22 |
| 862 | Closure gate | Gate script; STATUS.md; window closed |

---

## 6. Scope Boundaries

This window DOES:
- Decide ADM-001 formal governance status.
- Specify the truth-primitive wire format for all seven primitives.
- Lock the genesis-authority `assert.truth` schema.
- Lock the Layer 0 bundle schema section specification.
- Ratify HB-001/003 via CDL.
- Implement a Python reference implementation of the genesis assertion schema.

This window does NOT:
- Implement runtime truth-primitive submission or validation for the full seven
  primitives in the live epistemic graph (that is a separate Phase 863+ item).
- Change the live M-009 genesis loading (Rust `config.rs`) to use
  truth-primitive objects — the reference schema implementation in Python is
  authoritative for this window.
- Claim full homoiconic bootstrap is live on M-009.
- Deploy new primitives to `ALLOWED_PRIMITIVE_TYPES` without a separate CDL
  authorizing the epistemic graph runtime extension.
- Open or advance CDL-070.
- Open HB-002 (peer-to-peer bootstrap distribution — RC2+).

---

## 7. Dependency Bundle

Every Phase 853–862 artifact must carry or reference:

- `docs/specs/ilc_homoiconic_bootstrap_forward_obligations_v0.1.md`
- `docs/specs/ilc_human_decision_log_2026_04_26_v0.1.md` (§D7)
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.21.md`

---

## 8. CDL Carry-Forward

| CDL | Status | Action in this window |
|-----|--------|-----------------------|
| CDL-070 | Deferred | No change — SIM-MONETARY-01 prerequisite unchanged |
| HB-001/003 CDL (unnumbered) | Not yet opened | Open Phase 857, ratify Phase 860 |

---

## 9. Exclusions Tokens

```
no_hb_002_in_window_853_862
no_m009_genesis_loading_change_in_window_853_862
no_cdl_070_in_window_853_862
no_allowed_primitive_types_extension_without_separate_cdl
no_full_seven_primitive_runtime_in_window_853_862
no_public_launch_claim_in_window_853_862
```
