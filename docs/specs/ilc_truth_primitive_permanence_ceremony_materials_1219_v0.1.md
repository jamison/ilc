# Truth-Primitive Permanence Ceremony Materials 1219 v0.1

**Phase:** 1219 Stage A
**Window:** 1218-1224
**Date:** 2026-05-06
**Status:** CEREMONY MATERIALS COMMITTED - GENESIS ATTESTATION PENDING

`truth_primitive_permanence_ceremony_materials_committed_phase_1219`
`truth_primitive_permanence_genesis_attestation_pending_phase_1219`

---

## 1. Reference Packet

This ceremony package consumes the Phase 1211 packet:

- Packet: `docs/specs/ilc_truth_primitive_permanence_ratification_packet_1211_v0.1.md`
- Packet token: `truth_primitive_permanence_ratification_packet_committed_phase_1211`
- Target event token: `truth_primitive_permanence_ratification_event_required_window_1218_1224`
- Unsafe-after token: `truth_primitive_permanence_unsafe_after_window_1225_1232_closure`

The Phase 1211 packet defines the primitive set, evidence requirements, Genesis authority
attestation model, event mechanics, threshold, sunset boundary, and non-bypass rule.

---

## 2. Evidence Bundle

All evidence references are resolved to current repository paths and stable tokens.

| # | Evidence item | Resolved reference |
|---|---------------|--------------------|
| 1 | ADR-0004 acceptance of the New Seven primitive set | `docs/adr/ADR_0004_Genesis_Primitive_Commit_Epoch.md`; ADR register row in `docs/adr/README.md` marks ADR-0004 Accepted |
| 2 | CDL-073 wire-format dependency | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-073`; status `ratified`; ratified phase `860`; evidence document `docs/specs/ilc_cdl_073_homoiconic_bootstrap_schema_ratification_evidence_860_v0.1.md` |
| 3 | CDL-074 ratified runtime | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-074`; dependency token `cdl_074_truth_primitive_runtime_ratified.v0.1`; evidence document `docs/specs/ilc_cdl_074_truth_primitive_runtime_ratification_evidence_870_v0.1.md` |
| 4 | CDL-075 graph persistence | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-075`; dependency token `cdl_075_truth_primitive_graph_persistence.v0.1`; evidence document `docs/specs/ilc_cdl_075_truth_primitive_graph_persistence_ratification_evidence_883_v0.1.md` |
| 5 | CDL-052 for `refute.claim` criterion dependency | `docs/specs/ilc_constitutional_decision_log_v0.1.md` row `CDL-052`; runtime dependency token `cdl_052_ratified_466.v0.1` |
| 6 | Runtime token | `ilc_core/epistemic/truth_primitive_submission_runtime.py`: `TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"` |
| 7 | Graph-store token | `ilc_core/epistemic/truth_primitive_graph_store.py`: `TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"` |
| 8 | Layer-0 bundle schema path | `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json` |
| 9 | Signed Genesis v0.1 root envelope hash | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`; recorded in `docs/specs/ilc_antigravity_context_capsule_v5.47.md` and `docs/specs/ilc_window_1209_1217_handoff_1217_v0.1.md` |
| 10 | Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`; verified at Phase 1218 sequence lock and recorded in `docs/specs/ilc_phase_1218_1224_sequence_lock_v0.1.md` |

---

## 3. Primitive Set Covered

This ceremony package covers exactly the ADR-0004 New Seven Genesis truth primitives.

| Primitive | Permanence status proposed by this ceremony | Agent-issuable |
|-----------|---------------------------------------------|----------------|
| `assert.truth` | Covered | Yes |
| `validate.claim` | Covered | Yes |
| `contradict.assert` | Covered | Yes |
| `refute.claim` | Covered, with CDL-052 criterion dependency | Yes |
| `revise.assert` | Covered | Yes |
| `link.claim` | Covered | Yes |
| `commit.epoch` | Covered for primitive identity and consensus-only / non-agent-issuable boundary; production emission runtime not ratified by this ceremony | No |

`star.map` is explicitly excluded. It remains an L2 routing / development / experience
artifact and is not a Genesis truth primitive under this ceremony.

`commit.epoch` remains consensus-layer only. Agent submissions remain rejected under
`commit_epoch_agent_submission_rejected`.

This ceremony does not ratify a final production `commit.epoch` emission runtime. It
ratifies `commit.epoch` as the ADR-0004 New Seven time/finality primitive and preserves
the non-agent-issuable boundary. The production mapping from CDL-051 epoch-state/quorum
records and Genesis epoch-zero bootstrap into the `commit.epoch` primitive remains a
carry-forward specification obligation:

```text
commit_epoch_causal_frontier_mapping_spec_required
```

---

## 4. Attestation Template

The ratification event requires Genesis authority attestation. Optional witness
attestations may be included, but they are not required for Genesis bootstrap validity.

### 4.1 Genesis Authority Attestation

| Field | Value |
|-------|-------|
| Genesis authority identifier | Pending Genesis authority review |
| Date of attestation | Pending Stage B |
| Attestation statement | "I, as Genesis authority for the initial ILC project lineage, attest that the Phase 1211 packet and this Phase 1219 evidence bundle correctly define truth-primitive permanence for the ADR-0004 New Seven. `star.map` is excluded. `commit.epoch` is permanently ratified as the New Seven time/finality primitive for primitive identity and non-agent-issuable boundary only; this attestation does not ratify a final production `commit.epoch` emission runtime, which remains governed by CDL-051 finality semantics and the carry-forward token `commit_epoch_causal_frontier_mapping_spec_required`." |
| Evidence basis | This file, Phase 1211 packet, ADR-0004, CDL-073, CDL-074, CDL-075, CDL-052, runtime/store tokens, signed Genesis v0.1 hash, immutable diagnostic SHA |
| Form | Commit-anchored attestation in `docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md` after `GO Phase 1219 ratification commit` |

### 4.2 Optional Witness Attestations

Optional witness list for Stage B:

```text
[]
```

If witnesses are added before Stage B, each entry must include:

- witness identifier;
- date of attestation;
- attestation or objection statement.

---

## 5. Dissent Field

Current Stage A dissent record:

```text
No dissent recorded in the repository materials as of Phase 1219 Stage A.
```

Stage B must carry a dissent field explicitly, even if it remains empty. Any objection
raised before Stage B must be recorded and evaluated by Genesis authority before the
ratification event is committed.

---

## 6. Non-Bypass Rule

No public RC claim, public launch claim, release announcement, public repository
publication, or equivalent act may imply truth-primitive permanence unless this
ratification path completes or is explicitly superseded by a ratified CDL amendment.

Internal engineering work may continue, but it must not present truth-primitive permanence
as complete before the ratification event.

---

## 7. Threshold Statement

Genesis authority attestation, commit-anchored in the repository, constitutes
truth-primitive permanence ratification for Genesis bootstrap governance. Optional witness
attestations may be included. Any objection must be recorded in the dissent field and
evaluated by Genesis authority before ratification is committed.

This Stage A package does not itself ratify truth-primitive permanence. Stage B requires:

```text
GO Phase 1219 ratification commit
```

If Stage B is authorized, Codex must create:

`docs/specs/ilc_truth_primitive_permanence_ratification_event_1219_v0.1.md`

and record:

`truth_primitive_permanence_genesis_attested_phase_1219`

The Stage B event must also carry forward:

```text
commit_epoch_causal_frontier_mapping_spec_required
```

Scope: map CDL-051 epoch-state/quorum records plus Genesis epoch-zero bootstrap into the
ADR-0004 `commit.epoch` primitive wire format, with no wall-clock protocol time and no
float economics.

---

## 8. Explicit Non-Events

This Stage A package does not:

- ratify truth-primitive permanence;
- mutate the CDL register;
- accept an ADR;
- mutate runtime behavior;
- ratify a final production `commit.epoch` emission runtime;
- mutate signed Genesis v0.1;
- sign Genesis Atlas v0.2;
- generate or register a release key;
- produce a release envelope;
- authorize public repository publication;
- authorize public RC or public launch claims.
