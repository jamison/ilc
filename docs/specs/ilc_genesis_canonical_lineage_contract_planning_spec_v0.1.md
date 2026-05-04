# ILC Genesis Canonical Lineage Contract Planning Spec v0.1

Status: planning spec; not an ADR; not ratified
Phase: 1153
Date: 2026-05-04

`genesis_canonical_lineage_contract_planning_spec_committed_phase_1153`

---

## 1. Purpose

This planning spec defines the future Genesis Canonical Lineage Contract. The goal is to
make canonical ILC releases, gossip domains, ECU recognition, and star-map transitions
derive from the signed Genesis root envelope instead of from a loose project name or
mutable repository convention.

This document does not open an ADR or CDL. It does not mutate signed Genesis artifacts.
It is input to a future formal ADR, likely Window 1157+.

---

## 2. Network ID Derivation

Canonical network identity should derive from the signed Genesis root envelope:

```text
network_id = H("ILC_NETWORK_ID_V1" || genesis_root_envelope_hash)
```

Current internal v0.1 root envelope hash:

```text
ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c
```

Rationale: this binds network identity to the signed root of authority rather than to a
brand string. A fork may copy code, but if it strips or replaces Node 0, it has a
different `network_id` and cannot honestly claim canonical ILC lineage.

---

## 3. Node 0 Merkle Inclusion

Every canonical release receipt should carry a proof that Node 0 is included in the
signed Genesis manifest:

- Node 0 ID: `artifact:genesis_intent_attestation_init_authority_map`
- Signed manifest: `out/genesis_node_attestation_manifest_v0.1.json`
- Root envelope: `out/genesis_signing_root_envelope_v0.1.json`
- Signature: `out/genesis_signing_root_envelope_v0.1.sig`

Future release receipts should verify:

1. the root envelope hash matches the declared Genesis envelope;
2. the root envelope signature verifies against Genesis Agent 01 public key;
3. the node manifest hash appears inside the root envelope;
4. Node 0 appears in the node manifest;
5. the release artifact lineage references the verified root envelope or an authorized
   transition envelope.

This is a forward/backward chain: releases point backward to Genesis; validators can walk
forward through signed transition envelopes.

---

## 4. Operational Release Key Genesis Binding

Routine releases should not require Plate 2. The preferred future pattern is:

```text
Genesis root envelope
  -> release key registration artifact
  -> release key public key
  -> release envelope
  -> package / star-map candidate / runtime artifact hashes
```

The release key is not an independent root. It is a Genesis-bound delegated authority
artifact. A future ADR must define:

- release key generation and custody;
- key scope;
- transition envelope format;
- signature algorithm;
- expiration/supersession mechanics;
- verification behavior for validators and package consumers.

Phase 1153 does not create or authorize the release key.

---

## 5. Rolling ECU Legitimacy Windows

Canonical ECU/ILC recognition should require continuous Genesis-lineage-valid settlement.

Planning rule:

```text
ecu_window_valid(epoch_range) =
  all settlement receipts in epoch_range verify against the canonical network_id
  and every release/runtime receipt traces to Genesis or an authorized transition.
```

Implication: a fork that strips Node 0 or breaks the transition chain can still run code,
but its ECU/ILC accounting is not canonically recognized by ILC. The fork creates a new
economic universe.

This is an economic legitimacy rule, not a legal claim.

---

## 6. Gossip-Domain Continuity

Canonical gossip should carry a domain derived from Genesis:

```text
genesis_domain = H("ILC_GENESIS_GOSSIP_DOMAIN_V1" || genesis_root_envelope_hash)
```

Peers should reject or quarantine canonical-relay claims whose declared domain does not
match the local canonical domain. This prevents a stripped-Genesis fork from silently
participating in canonical relay surfaces while presenting incompatible lineage.

Future runtime work must decide where this is enforced:

- handshake envelope;
- peer announcement record;
- signed event envelope;
- release receipt;
- all of the above.

No runtime implementation is authorized by this planning spec.

---

## 7. Envelope Transition Policy

The current signed v0.1 root envelope is an internal Genesis custody artifact. A public RC
may later publish a different public-facing envelope.

Any transition must be explicit:

- `prior_envelope_hash`
- `new_envelope_hash`
- `change_summary`
- `transition_scope`
- `signing_key_ref`
- `signature`
- `effective_epoch_or_release`

A public RC envelope must not silently overwrite the internal v0.1 history. It may choose
public version numbering independently, but the technical transition chain must remain
auditable to validators.

This closes planning coverage for:

`public_rc_envelope_hash_transition_policy_required`

---

## 8. Non-Goals

This spec does not:

- open ADR-0036 or any other ADR;
- open or ratify a CDL;
- authorize a release key;
- authorize runtime enforcement;
- make license, trademark, or legal recommendations;
- mutate signed Genesis v0.1 artifacts.

---

`genesis_canonical_lineage_contract_planning_spec_committed_phase_1153`
