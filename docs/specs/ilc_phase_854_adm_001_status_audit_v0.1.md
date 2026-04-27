# ILC Phase 854 — ADM-001 Status Audit v0.1

Status: locked
Date: 2026-04-27
Phase: 854
Owner lane: Window 853–862 — HB-001/003 prerequisite audit

`phase_854_adm_001_status_audit`
`adm_001_governance_ratified_via_cdl_020_022_023_024`
`new_seven_truth_primitives_not_yet_individually_ratified`
`hb_001_hb_003_cdl_is_the_ratification_vehicle_for_new_seven`

---

## 1. Purpose

Phase 854 audits the formal governance status of ADM-001
(`docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`)
and its sub-items, so that Phase 857 (HB-001/003 CDL opening) can be
precisely scoped — neither re-ratifying already-locked items nor assuming
constitutional authority that has not yet been granted.

---

## 2. ADM-001 Governance Map

ADM-001 v0.2 describes a four-layer content-addressed distribution architecture
(Layer 0 Protocol Bundle, Layer 1 Genesis State Bundle, Layer 2 Epoch Snapshots,
Layer 3 Wire Protocol). Each layer's governance decisions were dispositioned via
individual CDLs in Windows 318–329.

### 2.1 Already-ratified ADM-001 elements

| CDL | Phase | Scope | Status |
|-----|-------|-------|--------|
| CDL-020 | 319 | Protocol-native bundle schema; full schema catalog selected | **Ratified** |
| CDL-021 | — | Rust kernel port and WASM distribution | Open (deferred indefinitely) |
| CDL-022 | 320 | Genesis state bundle specification and signing ceremony (`genesis bundle + ceremony`) | **Ratified** |
| CDL-023 | 321 | Epoch snapshot mechanism and fast-bootstrap protocol (hybrid model) | **Ratified** |
| CDL-024 | 329 | Wire protocol specification and transport bindings (transport-agnostic + reference bindings) | **Ratified** |
| CDL-034 | 349 | Unified node schema envelope, reserved fields, and `primitive_type` taxonomy | **Ratified** |

**Finding:** ADM-001's four-layer architectural decisions are constitutionally
locked. The document itself says "Proposed (awaiting decision-log ratification)"
because it is an _architectural memo_ — not itself a CDL. Its content was
dispositioned by the CDL series above. No new CDL is needed to "ratify ADM-001"
as a document.

### 2.2 The "New Seven" truth primitives — not ratified

ADM-001 §4.0.1 describes **Layer 0 content** it calls "The New Seven":

```
assert.truth, validate.claim, contradict.assert, refute.claim,
revise.assert, link.claim, commit.epoch
```

These are **submission operation verbs** — how an agent announces a claim,
validates another's claim, refutes a claim, and so on. They are conceptually
at Layer 3 (wire protocol operations) but their schemas are supposed to live in
Layer 0 (so agents can verify them without runtime knowledge).

CDL-020 ratified the "full schema catalog" approach — it locked that the Layer 0
bundle must contain a full type system. It did NOT individually ratify the wire
format of any specific primitive.

CDL-034 ratified a separate `primitive_type` taxonomy for epistemic graph nodes:
```python
ALLOWED_PRIMITIVE_TYPES = (
    "citation", "execution_descriptor", "governance_proposal",
    "knowledge_claim", "observation",
)
```

These are the **node classification** types (what kind of node is this in the
graph). They are a different concept from the New Seven submission verbs.

**Finding:** The New Seven truth primitive wire format — required fields,
canonical DAG-CBOR form, edge-generation behavior — has never been individually
ratified. It is described in ADM-001 §4.0.1 as design intent, not locked canon.
The HB-001/003 CDL (Phase 857) is the correct vehicle to ratify it.

---

## 3. HB-001/003 Scope Clarity

From the audit above, the gap for HB-001/003 is precisely bounded:

| Item | Constitutional status | Action needed |
|------|-----------------------|---------------|
| Four-layer architecture | Ratified (CDL-020/022/023/024) | None |
| Node primitive taxonomy | Ratified (CDL-034) | None |
| New Seven submission verbs wire format | **NOT ratified** | Phase 855 spec → Phase 857 CDL |
| Genesis-authority `assert.truth` schema | **NOT ratified** | Phase 856 design → Phase 857 CDL |
| Layer 0 bundle schema section | **NOT ratified** | Phase 859 implementation → Phase 860 CDL |

### 3.1 Relationship between New Seven and CDL-034 primitives

The two taxonomies are orthogonal and non-conflicting:

- **CDL-034 `primitive_type`**: classification field _inside_ a graph node — what
  the node represents (a citation, a governance proposal, a knowledge claim, etc.)
- **New Seven verbs**: operations for _creating_ or _acting on_ nodes — the
  submission envelope that produces a node + edges in the graph

A genesis-authority assertion would use `assert.truth` as the submission verb to
create a node. The resulting node's `primitive_type` may be a new value
(`genesis_authority_assertion`) or reuse an existing value. This question is
scoped to Phase 856.

### 3.2 ALLOWED_PRIMITIVE_TYPES extension

Extending `ALLOWED_PRIMITIVE_TYPES` in `node_schema_core_runtime_360.py` to add
`genesis_authority_assertion` (or similar) requires a separate CDL authorizing
the extension. The HB-001/003 CDL may fold this in, or it may be deferred to a
Phase 863+ epistemic graph extension CDL. Phase 857 will decide.

---

## 4. ADM-001 Document Status Decision

**Decision recorded here (Phase 854):**

ADM-001 v0.2 is a foundational architectural memo. Its governance decisions are
carried through CDL-020/022/023/024/034. It does not need to be re-ratified as
a document. It continues as authoritative architectural reference material.

The ADM-001 v0.2 document header "Proposed (awaiting decision-log ratification)"
is a stale artifact from when the memo was first written before the CDL series
ratified its contents. That label is superseded by the CDL ratifications. Future
patches to ADM-001 may remove the stale "Proposed" status, but this is cosmetic
housekeeping, not a governance action.

`adm_001_content_ratified_via_cdl_series_not_via_document_itself`
`adm_001_proposed_label_is_stale_no_new_ratification_needed`

---

## 5. Phase 855 Prerequisite

Phase 855 (truth primitive wire format specification) must specify, for each of
the New Seven:

1. **Required fields** — what fields must every submission of this type contain
2. **Optional fields** — what fields are permitted but not required
3. **Canonical DAG-CBOR form** — field ordering, encoding rules, CID derivation
4. **COSE Sign1 requirements** — which fields are signed, signature scope
5. **Edge-generation behavior** — what graph edges does a successful submission
   produce (source → target, edge type, weight)
6. **Forbidden interpretations** — what this primitive does NOT authorize

Phase 856 (genesis assertion schema) then applies `assert.truth` specifically to
the genesis authority domain.

---

## 6. Dependency Acknowledgment

This phase carries the mandatory dependency bundle from
`docs/specs/ilc_phase_853_862_sequence_lock_v0.1.md`.

- `docs/specs/ilc_homoiconic_bootstrap_forward_obligations_v0.1.md`
- `docs/specs/ilc_human_decision_log_2026_04_26_v0.1.md` (§D7)
- `docs/adr/ADR_0027_Canonical_Self_Describing_Bootstrap_and_Receipt_Boundary.md`
- `docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.21.md`

---

## 7. Tokens

```
phase_854_adm_001_status_audit_complete
adm_001_governance_ratified_via_cdl_020_022_023_024
adm_001_proposed_label_is_stale_superseded_by_cdl_ratifications
new_seven_truth_primitives_wire_format_not_yet_ratified
cdl_034_primitive_type_taxonomy_and_new_seven_verbs_are_orthogonal
hb_001_hb_003_cdl_is_the_ratification_vehicle_for_new_seven_wire_format
genesis_authority_assertion_primitive_type_question_deferred_to_phase_856
phase_855_new_seven_wire_format_spec_prerequisite_cleared
```
