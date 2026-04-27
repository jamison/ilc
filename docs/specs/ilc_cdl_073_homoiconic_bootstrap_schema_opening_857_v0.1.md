# ILC CDL-073 — Homoiconic Bootstrap Schema: HB-001 + HB-003

**Status:** open
**Opened phase:** 857
**Opened date:** 2026-04-27
**Owner lane:** Window 853–862 — RC1 homoiconic bootstrap

`cdl_073_not_ratified_at_opening`
`cdl_073_hb_001_hb_003_vehicle`

---

## 1. Subject

CDL-073 ratifies the truth-primitive wire format, genesis-authority assertion
schema, and Layer 0 bundle schema section required for RC1 homoiconic bootstrap
(HB-001 and HB-003 obligations from human decision log 2026-04-26 §D7).

---

## 2. Scope

CDL-073 governs exactly:

1. **Truth primitive wire format** (Phase 855): The canonical wire format for
   the seven ILC truth primitives (`assert.truth`, `validate.claim`,
   `contradict.assert`, `refute.claim`, `revise.assert`, `link.claim`,
   `commit.epoch`) — required fields, DAG-CBOR canonical form, COSE Sign1
   scope, edge generation behavior.

2. **Genesis-authority assertion schema** (Phase 856): The specific schema for
   genesis-authority `assert.truth` objects — `GenesisAssertionContent` fields,
   genesis authority key embedding (ML-DSA-65, CDL-069), lineage anchor, and
   the agent-verifiable path from assertion to trust without a code repository.

3. **New primitive_type value**: Addition of `"genesis_authority_assertion"` to
   the canonical primitive type registry. May be via `ALLOWED_PRIMITIVE_TYPES`
   extension or `SYSTEM_PRIMITIVE_TYPES` exempt set (decided at implementation
   Phase 858; both options are constitutional).

4. **Layer 0 bundle schema section** (Phase 859): The machine-legible artifact
   containing the truth-primitive schema definitions, structured so a new
   participant can parse it without a compiled binary.

---

## 3. Option Inventory

| Option | Description |
|--------|-------------|
| A | Defer — leave truth primitive wire format and genesis assertion schema as design intent without CDL lock |
| **B (proposed)** | **Full lock — ratify truth primitive wire format + genesis assertion schema + Layer 0 bundle schema section as constitutional canon via single CDL** |
| C | Partial lock — ratify genesis assertion schema only; defer truth primitive wire format and Layer 0 bundle to a later CDL |

**Proposed selection: Option B**

Rationale: HB-001 (genesis assertion schema) and HB-003 (Layer 0 bundle schema
section) share the truth primitive wire format as a common dependency. Splitting
them across CDLs creates a dependency chain without benefit — the scopes are
cleanly separable within one evidence checklist. Option C weakens the Layer 0
bundle guarantee, which is the point of HB-003. Option A leaves RC1
homoiconic bootstrap perpetually deferred.

---

## 4. Ratification Criteria

CDL-073 may be ratified when ALL of the following evidence items are satisfied:

### Evidence 1 — Truth primitive wire format locked (Phase 855)
Confirm `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md`
is committed and carries token `new_seven_wire_format_locked_phase_855`.
All seven primitives have required fields, DAG-CBOR canonical form, COSE
Sign1 scope, and edge type registry.

### Evidence 2 — Genesis assertion schema locked (Phase 856)
Confirm `docs/specs/ilc_phase_856_genesis_assertion_schema_design_v0.1.md`
is committed and carries token `genesis_assert_truth_content_schema_locked`.
`GenesisAssertionContent` field schema and verification path are specified.

### Evidence 3 — Runtime implementation (Phase 858)
`ilc_core/genesis/assertion_schema.py` exists and implements:
- `GenesisAssertionContent` dataclass or typed dict
- `encode_genesis_assertion()` → bytes (canonical DAG-CBOR + COSE Sign1)
- `verify_genesis_assertion(data: bytes, expected_network_id: str) → GenesisAssertionContent`
- `CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"`

### Evidence 4 — Layer 0 bundle schema section artifact (Phase 859)
A machine-legible schema artifact exists at
`docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json` (or `.cbor`)
containing the truth-primitive schema definitions for all seven primitives
in a format parseable without compiled binary.

### Evidence 5 — primitive_type extension or exempt list (Phase 858)
Either:
- `"genesis_authority_assertion"` is added to `ALLOWED_PRIMITIVE_TYPES`
  in `ilc_core/node/node_schema_core_runtime_360.py`, OR
- `SYSTEM_PRIMITIVE_TYPES = frozenset({"genesis_authority_assertion", "epoch_record"})`
  is introduced as a parallel exempt set in that module.
Both are constitutional; Phase 858 selects.

### Evidence 6 — Test coverage (Phase 858–859)
At minimum:
- `test_encode_genesis_assertion_produces_valid_cose_sign1`
- `test_verify_genesis_assertion_correct_network_id`
- `test_verify_genesis_assertion_wrong_network_id_rejected`
- `test_genesis_assertion_content_schema_fields_present`
- `test_layer_0_bundle_schema_section_is_machine_parseable`
- `test_genesis_primitive_type_accepted_by_node_schema_layer`
- `test_truth_primitive_envelope_required_fields_enforced` (parametrized over all seven)

### Evidence 7 — CDL-073 dependency token in implementation
All implementation modules in this window carry:
`CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"`

### Evidence 8 — Historical hardening
Tests for prior CDLs that overlap in domain (CDL-022 genesis bundle, CDL-034
node schema, CDL-069 identity) pass without modification. No regression.

---

## 5. Exclusion Tokens (what this CDL does NOT authorize)

```
cdl_073_does_not_authorize_live_graph_deployment_of_new_seven
cdl_073_does_not_replace_genesis_json_rust_binary
cdl_073_does_not_authorize_agent_issued_commit_epoch
cdl_073_does_not_open_hb_002_peer_bootstrap_distribution
cdl_073_does_not_advance_cdl_070
cdl_073_does_not_extend_epistemic_runtime_to_full_seven_in_live_graph
```

---

## 6. Governing Route

CDL-073 is constitutional law for RC1 homoiconic bootstrap. It does not amend
CDL-022 (genesis state bundle) or CDL-034 (node schema) — it extends them with
explicit forward-compatible additions. CDL-034's `ALLOWED_PRIMITIVE_TYPES` guard
either absorbs `genesis_authority_assertion` or the exempt path is used; either
way CDL-034's existing types are unchanged.

CDL-073 takes precedence over ADM-001 §4.0.1 design intent where they differ.
If any conflict exists between Phase 855/856 specifications and ADM-001, Phase
855/856 (as ratified by CDL-073) are authoritative.

---

## 7. Forward Obligations Created by CDL-073 Ratification

1. **HB-002** (RC2+): Peer-to-peer bootstrap distribution protocol now has a
   ratified genesis assertion schema to distribute. HB-002 may proceed after
   CDL-073 ratification.
2. **Full seven primitive runtime** (Phase 863+): CDL-073 locks the wire format
   but does not deploy the full seven to the live epistemic graph. A separate
   CDL extending `ALLOWED_PRIMITIVE_TYPES` and deploying the submission runtime
   is the Phase 863+ target.
3. **Rust binary migration** (Phase 863+): Migrating `config.rs` genesis loading
   to verify and parse genesis assertion objects instead of raw JSON is deferred
   to Phase 863+.

---

## 8. Dependency Bundle

Every Phase 857–860 artifact must carry or reference:

- `docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md`
- `docs/specs/ilc_phase_854_adm_001_status_audit_v0.1.md`
- `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md`
- `docs/specs/ilc_phase_856_genesis_assertion_schema_design_v0.1.md`
- `docs/specs/ilc_homoiconic_bootstrap_forward_obligations_v0.1.md`
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_ratification_evidence_838j_v0.1.md`
