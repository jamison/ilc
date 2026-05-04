# ADR-0036: Operational Release Key Genesis Binding

**Status:** Proposed
**Date:** 2026-05-04
**Phase:** 1159

`adr_0036_release_key_draft_committed_phase_1159`

---

## 1. Context

Phase 1142s established the signed Genesis v0.1 root envelope using Genesis
Agent 01 Plate 2 ML-DSA-65 material. That key is a cold-storage Genesis key and
must not become a routine release-signing key.

Later public RC and post-RC releases need an operational signing path for:

- release envelopes;
- package artifacts;
- versioned star-map candidates;
- release metadata and receipts.

This ADR drafts the narrow mechanism for registering an operational release key
as Genesis-bound delegated authority. It does not create the key and does not
authorize any signing ceremony.

---

## 2. Decision

ILC should define an operational release key as a delegated authority artifact
whose legitimacy traces to the signed Genesis root envelope or to an explicitly
authorized successor envelope.

The intended chain is:

```text
Genesis root envelope
  -> release key registration artifact
  -> operational release public key
  -> release envelope
  -> package / star-map / runtime artifact hashes
```

The release key is not an independent root. It is a scoped operational key for
routine release signing.

---

## 3. Scope

ADR-0036 scope is limited to the release-key mechanism:

- release key public-key registration;
- key scope and intended signed artifact classes;
- release-envelope hash binding;
- key rotation and supersession;
- verifier behavior for package and release consumers.

ADR-0036 does not define:

- the full Genesis Canonical Lineage Contract;
- `network_id` derivation;
- Node 0 Merkle-inclusion proof requirements;
- rolling ECU legitimacy windows;
- gossip-domain continuity;
- contributor keys or third-party application keys;
- legal licensing or trademark policy.

`genesis_canonical_lineage_contract_adr_required_separate_from_adr_0036`

---

## 4. Release Key Registration

A release key registration artifact must include:

- `release_key_id`;
- public key bytes and algorithm identifier;
- signed Genesis-root envelope reference;
- key scope;
- validity window expressed in protocol epochs where applicable;
- optional successor or supersession reference;
- canonical JSON hash of the registration payload.

The registration artifact must be signed or explicitly referenced by a Genesis
root envelope or by a successor envelope whose own authority traces to Genesis.

---

## 5. Signed Release Envelope

A release envelope signed by the operational key must bind:

- release version;
- package artifact hashes;
- star-map artifact hash where applicable;
- runtime artifact hashes where applicable;
- prior release-envelope hash;
- release key registration reference;
- Genesis root envelope reference or authorized transition-envelope reference.

Release-envelope JSON is a machine-verifiable artifact and must use canonical
serialization.

---

## 6. Key Rotation

Routine rotation is allowed only through a forward-linked transition:

```text
old release key
  -> signed key-transition envelope
  -> new release key registration artifact
```

The transition envelope must reference the prior release-key registration and
the new key registration. It must not retroactively invalidate releases already
signed under a valid prior key.

Compromise response is future canonical-authority gating, not deletion of
historical releases. Earlier releases remain historical artifacts and are
interpreted according to the key state valid at their signing epoch.

---

## 7. Public RC Transition

The public RC envelope transition policy remains a separate obligation. This
ADR only states that the operational release key is the expected mechanism for
routine public RC release signing once the public envelope transition has been
authorized.

`public_rc_envelope_hash_transition_policy_required`

---

## 8. Status

This ADR is a Phase 1159 draft. It remains Proposed. Acceptance review is
deferred to a later window after the full Genesis Canonical Lineage Contract
routing is resolved.
