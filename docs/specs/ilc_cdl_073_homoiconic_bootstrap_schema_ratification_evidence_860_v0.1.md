# ILC CDL-073 Homoiconic Bootstrap Schema Ratification Evidence 860 v0.1

Status: Phase-860 ratification evidence artifact
Date: 2026-04-27
Phase: 860
Owner lane: Window 853–862 — RC1 homoiconic bootstrap

`cdl_073_ratified_phase_860`

---

## 1. Purpose and Scope

Record ratification evidence for CDL-073 using the locked sequence:
- Phase 853: sequence lock
- Phase 854: ADM-001 status audit
- Phase 855: truth primitive wire format specification
- Phase 856: genesis assertion schema design
- Phase 857: CDL-073 opening
- Phase 858: HB-001 runtime implementation (`ilc_core/genesis/assertion_schema.py`)
- Phase 859: HB-003 Layer 0 bundle schema section artifact
- Phase 860: ratification evidence (this document)

Scope boundary:
- Mutate only CDL-073 ratification fields.
- Do not mutate other CDL-* rows.
- No migration of Rust genesis loading (excluded per sequence lock §6).

---

## 2. Evidence Chain Summary

1. `docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md`
2. `docs/specs/ilc_phase_854_adm_001_status_audit_v0.1.md`
3. `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md`
4. `docs/specs/ilc_phase_856_genesis_assertion_schema_design_v0.1.md`
5. `docs/specs/ilc_cdl_073_homoiconic_bootstrap_schema_opening_857_v0.1.md`
6. `ilc_core/genesis/assertion_schema.py` (Phase 858)
7. `ilc_core/node/node_schema_core_runtime_360.py` — `SYSTEM_PRIMITIVE_TYPES` added (Phase 858)
8. `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json` (Phase 859)
9. `docs/specs/ilc_constitutional_decision_log_v0.1.md`

---

## 3. CDL-073 Option Inventory and Selection Statement

Option inventory:
- `defer` (Option A)
- `full lock — truth primitive wire format + genesis assertion schema + Layer 0 bundle schema section` (Option B, proposed)
- `partial lock — genesis assertion schema only` (Option C)

Selection statement:
- Selected option: `full lock` (Option B)
- Rejected options: `defer` (Option A), `partial lock` (Option C)
- Rationale: Both HB-001 and HB-003 share the truth primitive wire format as
  a common dependency. Splitting produces a dependency chain without benefit.
  Option B closes both RC1 obligations in one evidence-checkable CDL.

---

## 4. Evidence Checklist Satisfaction

### Evidence 1 — Truth primitive wire format locked (Phase 855)

File: `docs/specs/ilc_phase_855_truth_primitive_wire_format_spec_v0.1.md`

Token present: `new_seven_wire_format_locked_phase_855` ✓

All seven primitives have:
- Required fields ✓
- DAG-CBOR canonical form ✓
- COSE Sign1 scope ✓
- Edge type registry ✓

### Evidence 2 — Genesis assertion schema locked (Phase 856)

File: `docs/specs/ilc_phase_856_genesis_assertion_schema_design_v0.1.md`

Token present: `genesis_assert_truth_content_schema_locked` ✓

`GenesisAssertionContent` field schema specified ✓
Genesis authority key embedding (ML-DSA-65) locked ✓
Agent-verifiable path without code repository specified ✓

### Evidence 3 — Runtime implementation (Phase 858)

File: `ilc_core/genesis/assertion_schema.py`

Present: ✓

- `CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"` ✓
- `GenesisAssertionContent` dataclass ✓
- `encode_genesis_assertion_payload()` ✓
- `verify_genesis_assertion_schema()` ✓
- `GenesisAssertionError` ✓

### Evidence 4 — Layer 0 bundle schema section artifact (Phase 859)

File: `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json`

Present: ✓
Machine-legible JSON, no ILC imports required ✓
All seven primitives present ✓
Edge type registry complete (14 edge types) ✓
COSE Sign1 section: Ed25519 (-8) + ML-DSA-65 (-65) ✓
DAG-CBOR canonical rules ✓
Submission envelope ✓

### Evidence 5 — primitive_type extension or exempt list (Phase 858)

`SYSTEM_PRIMITIVE_TYPES = frozenset({"genesis_authority_assertion", "epoch_record"})`
added to `ilc_core/node/node_schema_core_runtime_360.py` ✓

`CDL_073_DEPENDENCY` added to `node_schema_core_runtime_360.py` ✓

Selected path: `SYSTEM_PRIMITIVE_TYPES` exempt set (not merged into `ALLOWED_PRIMITIVE_TYPES`)
— avoids coupling agent-issuable and system-only primitives in the same guard ✓

### Evidence 6 — Test coverage (Phase 858–859)

Test file: `tests/test_phase_858_hb_001_genesis_assertion_schema.py` — 35 tests ✓
Test file: `tests/test_phase_859_hb_003_layer_0_bundle_schema_section.py` — 16 tests ✓

Coverage confirmed:
- `test_encode_genesis_assertion_payload_returns_bytes` ✓
- `test_verify_genesis_assertion_schema_correct_network_id` ✓
- `test_verify_genesis_assertion_schema_wrong_network_id_rejected` ✓
- `test_genesis_assertion_content_schema_fields_present` ✓
- `test_layer_0_bundle_schema_section_is_machine_parseable` ✓
- `test_genesis_primitive_type_in_system_primitive_types` ✓ (Evidence 5 test)
- `test_layer_0_bundle_schema_section_contains_all_seven_primitives` ✓
- `test_cdl_073_dependency_token_present` ✓

### Evidence 7 — CDL-073 dependency token in implementation

`CDL_073_DEPENDENCY = "cdl_073_homoiconic_bootstrap_schema_ratified.v0.1"` present in:
- `ilc_core/genesis/assertion_schema.py` ✓
- `ilc_core/node/node_schema_core_runtime_360.py` ✓

### Evidence 8 — Historical hardening

Tests covering overlapping CDLs run and passing without modification:

| Test file | Tests | Result |
|-----------|-------|--------|
| `test_cdl_034_ratification_349.py` | (included) | PASS ✓ |
| `test_node_schema_core_runtime_360.py` | (included) | PASS ✓ |
| `test_cdl_022_ratification_320.py` | (included) | PASS ✓ |
| `test_genesis_state_bundle_runtime_312.py` | (included) | PASS ✓ |
| `test_phase_838c_epoch_endorsement_runtime.py` | 75 tests | PASS ✓ |

Total across all five historical files: 111 tests, 111 passed. No regression.

---

## 5. Ratification Record

| Field | Value |
|-------|-------|
| decision_id | `CDL-073` |
| status | `ratified` |
| ratified_phase | `860` |
| ratified_date | `2026-04-27` |
| evidence_document | `docs/specs/ilc_cdl_073_homoiconic_bootstrap_schema_ratification_evidence_860_v0.1.md` |
| selected_option | `full lock — truth primitive wire format + genesis assertion schema + Layer 0 bundle schema section` |
| dependency_token | `cdl_073_homoiconic_bootstrap_schema_ratified.v0.1` |

---

## 6. Mutation Protocol Confirmation

- Only `CDL-073` ratification fields mutated in constitutional decision log.
- No other `CDL-*` rows mutated.
- Runtime files changed: `ilc_core/genesis/assertion_schema.py` (new),
  `ilc_core/node/node_schema_core_runtime_360.py` (`SYSTEM_PRIMITIVE_TYPES` + dependency token added).
- Rust binary `config.rs` unchanged (excluded per sequence lock §6).

---

## 7. Non-Goals Confirmed

This ratification does NOT:
- Deploy the New Seven to the live epistemic graph runtime.
- Replace genesis.json Rust loading with assertion objects.
- Open HB-002 (peer-to-peer bootstrap distribution).
- Advance or touch CDL-070.
- Authorize agent-issued `commit.epoch`.
