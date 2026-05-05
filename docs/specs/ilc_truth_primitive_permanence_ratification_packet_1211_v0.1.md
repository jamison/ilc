# Truth-Primitive Permanence Ratification Packet 1211 v0.1

**Phase:** 1211
**Window:** 1209-1217
**Date:** 2026-05-05
**Status:** PACKET COMMITTED - NOT RATIFIED

`truth_primitive_permanence_ratification_packet_committed_phase_1211`

---

## 1. Scope And Non-Claims

This packet consumes:

```text
truth_primitive_permanence_ratification_packet_required_window_1209
```

It defines the governance packet needed to ratify truth-primitive permanence before
Genesis governance sunset. It does not itself ratify permanence, open or ratify a CDL,
accept an ADR, authorize public RC / public launch claims, mutate signed Genesis v0.1,
mutate the v0.2 candidate, generate release keys, or change runtime behavior.

---

## 2. Primitive Set

The permanence packet covers exactly the ADR-0004 "New Seven" Genesis truth primitives.
`star.map` is explicitly excluded and remains an L2 routing / development artifact.

| Primitive | Definition | Agent-issuable | Enforcement / schema surfaces |
|-----------|------------|----------------|-------------------------------|
| `assert.truth` | Creates a truth assertion node. | Yes | ADR-0004; CDL-073; CDL-074; CDL-075; `ilc_core/epistemic/truth_primitive_submission_runtime.py`; `ilc_core/epistemic/truth_primitive_graph_store.py` |
| `validate.claim` | Creates validation evidence for an existing claim node. | Yes | ADR-0004; CDL-073; CDL-074; CDL-075; `truth_primitive_submission_runtime.py`; `truth_primitive_graph_store.py` |
| `contradict.assert` | Creates contradiction evidence against an assertion. | Yes | ADR-0004; CDL-073; CDL-074; CDL-075; `truth_primitive_submission_runtime.py`; `truth_primitive_graph_store.py` |
| `refute.claim` | Creates refutation evidence under the ratified refutation criterion contract. | Yes | ADR-0004; CDL-052; CDL-073; CDL-074; CDL-075; `truth_primitive_submission_runtime.py`; `truth_primitive_graph_store.py` |
| `revise.assert` | Creates a revised assertion node and revision edges. | Yes | ADR-0004; CDL-073; CDL-074; CDL-075; `truth_primitive_submission_runtime.py`; `truth_primitive_graph_store.py` |
| `link.claim` | Creates semantic link edges between claims. | Yes | ADR-0004; CDL-073; CDL-074; CDL-075; `truth_primitive_submission_runtime.py`; `truth_primitive_graph_store.py` |
| `commit.epoch` | Finalizes epoch state at the consensus layer. | No; consensus-layer only | ADR-0004; Layer-0 bundle schema; Phase 867 / 872 `commit_epoch_agent_submission_rejected`; CDL-074 runtime exclusion |

---

## 3. Evidence Bundle

Ratification must cite at minimum:

- ADR-0004 acceptance of the New Seven primitive set.
- CDL-073 wire-format dependency for truth-primitive submissions.
- CDL-074 ratified runtime dependency:
  `cdl_074_truth_primitive_runtime_ratified.v0.1`.
- CDL-075 graph persistence dependency:
  `cdl_075_truth_primitive_graph_persistence.v0.1`.
- CDL-052 for the `refute.claim` criterion dependency:
  `cdl_052_ratified_466.v0.1`.
- Runtime token:
  `TRUTH_PRIMITIVE_RUNTIME_VERSION = "truth_primitive_submission_runtime_868.v0.1"`.
- Graph-store token:
  `TRUTH_PRIMITIVE_GRAPH_STORE_VERSION = "truth_primitive_graph_store_880.v0.1"`.
- Layer-0 bundle schema:
  `docs/specs/ilc_layer_0_bundle_schema_section_v0.1.json`.
- Signed Genesis v0.1 hash:
  `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`.
- Immutable diagnostic SHA:
  `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56`.

Known exception note: `commit.epoch` is a truth primitive but not agent-issuable; agent
submissions remain permanently rejected by `commit_epoch_agent_submission_rejected`.

Known exclusion note: `star.map` is not a truth primitive and cannot be ratified as one by
this packet.

Known dissent note: Phase 1206 recorded no specific dissent against the primitive set, but
the later ratification event must include an explicit dissent field even if empty.

---

## 4. Ratifier Class

Truth-primitive permanence is ratified by Genesis authority attestation.

The Genesis founding authority (or an authorized Genesis delegate) commits a
ratification artifact anchored in the repository. Per ADR-0036, signing authority for
ILC's initial project lineage traces to the Genesis root envelope — no multi-party
committee is required for Genesis bootstrap ratification.

Optional: additional witness attestations may be included in the ceremony artifact.
Witnesses may include collaborators, reviewers, or external auditors. Their attestations
supplement the Genesis authority attestation but are not required for validity.

A multi-party signer roster (e.g., ≥3 founding members + external witnesses) is
appropriate for public release / community ratification events but is not required for
Genesis bootstrap governance.

---

## 5. Event Mechanics

Ratification is a later human-authorized governance event, not this packet.

Required order:

1. Publish this Phase 1211 packet.
2. Execute a later explicit human-authorized ratification ceremony in the target window.
3. Produce a commit-anchored ratification artifact by Genesis authority that cites this
   packet, the primitive set, evidence hashes, the Genesis authority attestation, dissent
   field (required even if empty), and non-bypass rule. Optional witness attestations may
   be included. No multi-party vote tally is required for Genesis bootstrap ratification.
4. Open or ratify a CDL only if the ceremony determines that constitutional register
   mutation is required; otherwise the signed ceremony artifact is the ratification event.

The later ceremony must be reproducible from repository artifacts and must not rely on
oral/social convention as the only evidence of permanence.

---

## 6. Threshold

Ratification is complete when Genesis authority commits a ratification attestation
anchored in the repository that cites this packet and the evidence bundle.

Genesis authority attestation constitutes ratification for Genesis bootstrap governance.
No vote quorum or multi-party roster is required.

If additional witnesses provide attestations, record them in the ceremony artifact.
If any contributor raises an objection, it must be recorded in the dissent field and
evaluated by Genesis authority before ratification is committed. Any unresolved objection
blocks the attestation until resolved or explicitly superseded by a ratified CDL.

---

## 7. Sunset Boundary

Target ratification window:

```text
Window 1218-1224
```

Hard unsafe-after boundary:

```text
Window 1225-1232 closure
```

If ratification has not completed by the hard boundary, the Genesis governance sunset
condition is unsafe for any public-launch-adjacent permanence claim unless a ratified CDL
explicitly supersedes this packet.

---

## 8. Non-Bypass Rule

No public RC claim, public launch claim, release announcement, public repository
publication, or equivalent act may imply truth-primitive permanence unless this
ratification path completes or is explicitly superseded by a ratified CDL amendment.

Internal engineering work may continue, but it must not present truth-primitive permanence
as complete before the ratification event.

---

## 9. Carry-Forward

```text
truth_primitive_permanence_ratification_packet_committed_phase_1211
truth_primitive_permanence_ratification_event_required_window_1218_1224
truth_primitive_permanence_unsafe_after_window_1225_1232_closure
```
