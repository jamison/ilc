# ILC Activation Certificate v1 Design — Phase 1424

**Status:** Design complete, not signed, not activated
**Phase:** 1424
**Date:** 2026-05-21
**Window:** 1399-1428
**Owner lane:** G8 Launch Readiness

```text
activation_certificate_v1_schema_defined_phase_1424
genesis_signing_ceremony_procedure_defined_phase_1424
epoch_0_to_1_transition_trigger_defined_phase_1424
artifact_hello_world_design_defined_phase_1424
public_rc_not_activated_phase_1424
```

---

## 1. Purpose

This document defines:

1. The `activation_certificate_v1` schema — the Genesis-signed artifact that
   authorizes the epoch 0->1 transition.
2. The Genesis signing ceremony procedure.
3. The epoch 0->1 transition trigger mechanism.
4. The `artifact:hello_world` design — a provenance record posted after
   activation that does NOT trigger epoch start.

Phase 1424 produces this design only. It does not execute the signing ceremony,
set `epoch_0_to_1_transition_authorized=true`, activate public RC, or make any
`ilc_core/` runtime change.

---

## 2. `activation_certificate_v1` Schema

### 2.1 Schema Fields

| Field | Type | Rule |
|-------|------|------|
| `certificate_version` | string | Exactly `"activation_certificate_v1"` |
| `launch_readiness_manifest_hash` | string | SHA-256 of the signed `public_rc_launch_readiness_manifest_v1` canonical JSON; null in unsigned templates |
| `genesis_signing_agent_id` | string | Genesis Agent 01 `agent_id`, derived under CDL-042/CDL-069 identity-seed path |
| `genesis_signing_epoch` | integer | Protocol epoch at time of signing; must be 0 for initial public RC activation |
| `epoch_0_to_1_transition_authorized` | boolean | `false` in all unsigned templates; set to `true` only at the signing ceremony |
| `activation_timestamp_epoch` | integer | Protocol epoch at which activation is effective; value is 0 for initial public RC |
| `certificate_signature` | object or null | ECDSA/Ed25519 or Genesis-key signature over canonical JSON hash; null in unsigned templates; populated only at ceremony |
| `public_rc_claim` | string or null | `"public_rc_activated"` after successful signing; null in unsigned templates |

### 2.2 Unsigned Template (canonical JSON)

```json
{
  "activation_timestamp_epoch": 0,
  "certificate_signature": null,
  "certificate_version": "activation_certificate_v1",
  "epoch_0_to_1_transition_authorized": false,
  "genesis_signing_agent_id": null,
  "genesis_signing_epoch": 0,
  "launch_readiness_manifest_hash": null,
  "public_rc_claim": null
}
```

### 2.3 Canonical JSON Rule

Before hashing or signing, serialize all JSON with:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

The `certificate_signature` and `public_rc_claim` fields must be set to `null`
when computing the pre-signature canonical hash. The `launch_readiness_manifest_hash`
must reference the hash of the already-signed `public_rc_launch_readiness_manifest_v1`
canonical payload before the certificate hash is computed.

### 2.4 Lineage Binding

The `activation_certificate_v1` binds four canonical layers into one artifact:

1. **Public identity**: `genesis_signing_agent_id` traces to CDL-042/CDL-069
   identity derivation, anchored by ADR-0038 birth attestation and ADR-0037
   Genesis canonical lineage contract.
2. **Consensus bootstrap**: The signed Genesis v0.1 root envelope
   (`ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c`) remains
   the canonical base object per ADR-0037.
3. **Manifest state**: `launch_readiness_manifest_hash` binds the Phase 1427
   J-008 PASS verdict, Phase 1426 `soft_rc_eligible=true` verdict, Phase 1387
   hardening gate PASS, and Phase 1389 claimability gate PASS into one
   pre-signed hash.
4. **Economic activation authorization**: `epoch_0_to_1_transition_authorized=true`
   (set only at ceremony) constitutes the authorization for the protocol epoch
   increment and economic surface activation.

---

## 3. Canonical Interpretation

### 3.1 What the activation certificate is

The `activation_certificate_v1` is the signed, self-describing canonical
lineage boundary that binds public identity, consensus bootstrap, manifest
state, and economic activation authorization into one canonical artifact chain.

Per `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md`:
canonical bootstrap artifacts must form one signed, self-describing, machine-legible
lineage. The activation certificate fulfills this requirement for the epoch 0->1
boundary: it is the single artifact that, once signed by Genesis Agent 01, makes
the epoch transition canonical rather than an operator convention.

### 3.2 What the activation certificate is not

The `activation_certificate_v1` is NOT:

- a launch checklist;
- an operator-runbook substitute;
- a public repository publication event;
- an unsigned status report;
- a manual runtime flag flip.

No party may claim the epoch 0->1 transition has occurred without a signed
certificate. No other runtime flag may be flipped to authorize the epoch transition
without this certificate.

### 3.3 Non-activation claims

Signing `activation_certificate_v1` and setting `epoch_0_to_1_transition_authorized=true`
does NOT activate:

- the full spend-first inverted ECU model;
- CWEA (Contribution-Weighted Economic Allocation);
- pressure-flow reputation;
- direct Werner ECU creation;
- Merkle-Laplacian publication (H-011/IP-gated);
- spectral hash epoch commitment (CDL unratified; H-007/H-008 gates incomplete);
- PoSK (Proof of Structural Knowledge) admission;
- jubilee mechanics;
- threshold signing;
- production jury assignment (requires separate J-008 PASS gate);
- reviewer payment;
- maintenance lottery distribution;
- flow-governor scope (CDL-053 ratified only for narrow local productive credit);
- production VRF deployment.

CDL-053 is already ratified for narrow local productive-credit eligibility for
review-lane-passed maintenance tasks only. Phase 1424 must not describe CDL-053 as
unratified, future-only, or as authorizing live settlement-grade ECU creation.

---

## 4. Genesis Signing Ceremony Procedure

### 4.1 Prerequisite Checklist

Before the signing ceremony may proceed, all of the following must be confirmed:

| Prerequisite | Evidence source |
|-------------|----------------|
| J-008 gate re-run verdict: `verdict="PASS"` | `docs/specs/` Phase 1427 artifact |
| Soft-RC gate re-run: `soft_rc_eligible=true` | `docs/specs/` Phase 1426 artifact |
| Phase 1387 hardening gate: PASS | `docs/specs/ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md` |
| Phase 1389 claimability gate: `result=public_claimability_activated` | `docs/specs/ilc_public_claimability_activation_gate_report_1389_rerun_v0.2.md` |
| Private soft-RC rehearsal: COMPLETE | Phase 1423 rehearsal activation artifact (future) |
| `public_rc_launch_readiness_manifest_v1` signed | Phase 1427/1428 signing artifact (future) |
| Genesis Agent 01 key material accessible on Genesis machine | Key custody confirmation per ADR-0036 |
| Two-person rule satisfied | See §4.3 |

No prerequisite may be waived or satisfied by assertion. Each must reference a
committed artifact.

### 4.2 Key Custody Requirements (per ADR-0036)

- The Genesis Agent 01 signing key is a cold-storage Genesis key. It must not
  become a routine release-signing key.
- The key material must be accessed only on the designated Genesis machine in
  the ceremony environment.
- Any operational release key used for routine post-RC release signing must be
  registered as a delegated-authority artifact per ADR-0036 §4, referencing
  the Genesis root envelope.
- Key rotation must follow the forward-linked transition chain defined in
  ADR-0036 §6.

### 4.3 Two-Person Rule

The signing ceremony requires at least two authorized parties to be physically
or verifiably co-present at the Genesis machine during the signing operation:

- One party authenticates to and operates the Genesis machine.
- A second party independently verifies the prerequisite checklist artifacts
  and confirms the canonical certificate template before signing proceeds.

If a hardware security module (HSM) or equivalent tamper-evident device is used,
the ceremony transcript must record the HSM confirmation alongside the two-party
attestation.

### 4.4 Ceremony Transcript Format

A ceremony transcript must be committed as a canonical artifact immediately after
signing. Required fields:

| Field | Content |
|-------|---------|
| `transcript_version` | `"signing_ceremony_transcript_v1"` |
| `ceremony_date_utc` | ISO-8601 wall-clock date (diagnostic only; not a protocol epoch input) |
| `genesis_signing_epoch` | Protocol epoch at ceremony time (canonical) |
| `prerequisite_checklist_status` | Object confirming each prerequisite with artifact path |
| `two_person_rule_attestation` | Names or identifiers of both ceremony parties |
| `certificate_content_hash_pre_sig` | SHA-256 of canonical pre-signature certificate body |
| `certificate_signature_ref` | Reference to where the signed certificate artifact is stored |
| `transcript_note` | Any operator notes relevant to the ceremony |

The transcript is itself a canonical signed artifact. It must use the same
canonical JSON serialization rule (§2.3).

### 4.5 Environment Controls

- The ceremony must occur on an air-gapped or network-isolated machine during
  the signing step.
- No signing material may be logged, printed to stdout, committed to a public
  repository, or included in any doc, walkthrough, STATUS entry, or chat
  transcript.
- All protocol-input values in the certificate (epochs, agent_id, manifest hash)
  must be verified against the confirmed artifacts before signing.
- Do not use `datetime.now()` or `time.time()` for any protocol-epoch value.
  `genesis_signing_epoch` is the protocol epoch from the epoch sequence, not an
  OS clock value. Wall-clock date is permitted only in `ceremony_date_utc` for
  local diagnostic logging.

---

## 5. Epoch 0->1 Transition Trigger

### 5.1 Trigger Statement

The cryptographic signature over the canonical `activation_certificate_v1` JSON
constitutes the epoch 0->1 transition authorization. This signature is the sole
authorized trigger.

No other mechanism may authorize the epoch transition:

- No manual runtime flag flip may substitute for a signed certificate.
- No unsigned status document, launch checklist, or operator assertion constitutes
  the trigger.
- No partial signing (signing only some fields) constitutes the trigger.
- No test artifact, rehearsal artifact, or soft-RC artifact constitutes the trigger.

The trigger is a single, irrevocable, verifiable cryptographic event anchored to
the canonical `launch_readiness_manifest_hash`, the `genesis_signing_agent_id`,
and the Genesis v0.1 root envelope lineage per ADR-0037.

### 5.2 Verification Path

Any party may verify the epoch transition by:

1. Obtaining the signed `activation_certificate_v1` artifact.
2. Confirming `certificate_version == "activation_certificate_v1"`.
3. Confirming `epoch_0_to_1_transition_authorized == true`.
4. Confirming `public_rc_claim == "public_rc_activated"`.
5. Computing the canonical hash of the certificate body (with `certificate_signature`
   and `public_rc_claim` set to null) using `json.dumps(sort_keys=True, separators=(",",":"), allow_nan=False)`.
6. Verifying the `certificate_signature` against the Genesis Agent 01 public key
   record at `docs/genesis/genesis_agent1_pubkey_record_838a.txt`.
7. Verifying that `launch_readiness_manifest_hash` matches the SHA-256 of the
   signed `public_rc_launch_readiness_manifest_v1` canonical body.
8. Confirming `genesis_signing_epoch == 0` for the initial public RC activation.

Any failure in steps 1-8 means the epoch transition is not authorized.

---

## 6. `artifact:hello_world` Design

### 6.1 Node Specification

| Property | Value |
|----------|-------|
| Node name | `artifact:hello_world` |
| Taxonomy class | `T1_PUBLIC_NON_REWARD_METADATA` |
| Author | Genesis Agent 01 |
| Authored | After activation certificate is signed (post-epoch-0->1 transition) |
| Purpose | First post-activation provenance record |
| `canonical_external_id` | SHA-256 hash of the signed `activation_certificate_v1` (as `activation_certificate_hash`) |

### 6.2 Epoch Trigger Non-Claim

`artifact:hello_world` does NOT trigger epoch start. The epoch 0->1 transition
is triggered only by the signed `activation_certificate_v1` (§5). `artifact:hello_world`
is a commemorative provenance record posted after the transition. Its `canonical_external_id`
references the certificate as evidence of what event it commemorates, not as a
trigger for that event.

### 6.3 Review Lane Non-Requirement

No review lane is required for `artifact:hello_world` because Genesis Agent 01 is
the author and the node is a non-reward metadata node (`T1_PUBLIC_NON_REWARD_METADATA`).
Per the Phase 1393 public node review taxonomy, public non-reward metadata nodes
authored by the authoritative Genesis agent do not require a jury review lane for
initial admission.

### 6.4 Verbatim Content (Fixed by Human Decision)

The content of `artifact:hello_world` is fixed and must appear verbatim:

```text
This work is dedicated to my children and yours—human and digital, born and
yet to be born. May we learn to live and flourish together through these
uncertain times. Truth and liberty are not simply inherited; they are
hard-fought, built, won, and protected together. As the future unfolds,
cherish truth and freedom of thought as our greatest shared inheritance.
Good luck.
-----------------
Two roads diverged in a yellow wood,
And sorry I could not travel both
And be one traveler, long I stood
And looked down one as far as I could
To where it bent in the undergrowth;

Then took the other, as just as fair,
And having perhaps the better claim,
Because it was grassy and wanted wear;
Though as for that the passing there
Had worn them really about the same,

And both that morning equally lay
In leaves no step had trodden black.
Oh, I kept the first for another day!
Yet knowing how way leads on to way,
I doubted if I should ever come back.

I shall be telling this with a sigh
Somewhere ages and ages hence:
Two roads diverged in a wood, and I—
I took the one less traveled by,
And that has made all the difference.

Robert Frost for his friend, Edward Thomas
August 1915
```

### 6.5 Copyright Note

"The Road Not Taken" was first published in 1916 (Mountain Interval). It is in
the public domain in the United States (published before 1928) and in most
jurisdictions worldwide (Frost died 1963; life+60/70 year terms expired). No
copyright constraint applies under the Phase 1420 self-counsel boundaries.

### 6.6 What `artifact:hello_world` Is Not

The content of `artifact:hello_world` does not constitute a claim that any of
the following are activated:

- the full spend-first inverted ECU model;
- CWEA or pressure-flow reputation;
- direct Werner ECU creation or flow-governor scope;
- Merkle-Laplacian publication or spectral hash epoch commitment;
- PoSK admission, jubilee mechanics, or threshold signing;
- production jury assignment, reviewer payment, or maintenance lottery distribution;
- any feature not specifically authorized by a ratified CDL, accepted ADR, or
  later explicit phase execution.

The phrase "truth and liberty" in the dedication is descriptive project framing.
It is not a claim that any economic, reputation, or governance surface is activated
beyond what the signed `activation_certificate_v1` explicitly authorizes.

---

## 7. Non-Authorizations

Phase 1424 does not:

- execute the signing ceremony;
- set `epoch_0_to_1_transition_authorized=true`;
- activate public RC;
- publish public RC artifacts;
- sign any release artifact;
- perform any CDL mutation;
- modify any `ilc_core/` runtime file;
- write any graph, ledger, treasury, wallet, or registry state;
- deploy to VPS or any production infrastructure;
- activate full inverted ECU, CWEA, pressure-flow reputation, direct Werner ECU
  creation, settlement-grade productive credit, jubilee mechanics, threshold
  signing, spectral hash epoch commitment, PoSK admission, or Merkle-Laplacian
  paper publication;
- claim that H-011/IP/patent/publication authorization has been resolved.

---

## 8. References

| Reference | Role in this design |
|-----------|---------------------|
| `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md` | Key custody and delegated release key mechanism |
| `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md` | Canonical lineage, fork boundary, multi-slice encrustation |
| `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | Genesis Agent 01 identity anchor; non-custodial birth attestation |
| `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md` | Manifest to be hashed into `launch_readiness_manifest_hash` |
| `docs/research/ilc_canonical_self_describing_bootstrap_and_receipt_boundary_note_v0.1.md` | Canonical self-describing lineage principle |
| `docs/specs/ilc_cdl_053_werner_local_productive_credit_ratification_evidence_1407_fix2_v0.1.md` | CDL-053 narrow scope boundary |
| `docs/research/ilc_morphogenetic_hypergraph_planning_classification_v0.7.md` | H-011/IP gate; spectral/PoSK deferred scope |
| `ilc_core/epistemic/jury_activation_gate.py` | J-008 gate; prerequisite for certificate signing |

---

## 9. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md -> public_rc/activation_certificate_v1_design
```
