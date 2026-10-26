# ILC Release Authority Set Node Spec

**Phase:** GAP-RELEASE-AUTHORITY-SET-NODE-SPEC-00  
**Version:** v0.1  
**Date:** 2026-10-13  
**Status:** Spec-only candidate; no runtime activation, no CDL mutation, no key ceremony  
**Authority context:** CDL-121 open/prelocked homoiconic release object taxonomy; Phase 1335 Ed25519 release-signing workflow; release assertion native discovery and RC fresh-invite smoke completed through Rev 278

---

## 1. Purpose

This document defines the graph-native authority vocabulary needed before any
release assertion edge grows a `signature_scheme` field. The current release
validator accepts only the Phase 1335 Ed25519 release key and reports
`release_authority: "ed25519_phase_1335"`. That behavior is intentionally
preserved. This spec names the authority-set node that future schema and
verifier work can reference, and it states the fail-closed dispatch rules that
must apply when additional release-signing schemes are introduced.

The deliverable is vocabulary and protocol shape only. It does not add a live
runtime object, change release keys, modify `ReleaseAttestationEdge`, ratify
CDL-121, publish an assertion, or activate threshold signing.

---

## 2. Current Baseline

The active public-RC release authority is the embedded Phase 1335 Ed25519 public
key:

```text
5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a
```

The current `validate_release_assertion()` path validates
`ReleaseAttestationEdge` records by recomputing `compute_signed_preimage_sha256()`,
requiring `signing_algorithm == "Ed25519"`, requiring the embedded public key,
and verifying `signature_hex` over the raw 32 bytes decoded from
`signed_preimage_sha256`. It returns `release_authority: "ed25519_phase_1335"`.
There is no scheme-dispatch table in the runtime today.

CDL-121 is open/prelocked, not ratified. Its opened release object taxonomy
includes `SoftwareReleaseNode`, `ArtifactNode`, `BuildRecipeNode`, and
`ReleaseAttestationEdge`. Transport URLs remain retrieval hints; release
authority comes from graph records plus release-signing evidence.

---

## 3. `ReleaseAuthoritySetNode`

`ReleaseAuthoritySetNode` is a content-addressed graph node describing which
release signers may attest releases, under which signature schemes, and for
which release channels. It is not a key, not a process, not a serving host, and
not a mutable account record.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `node_kind` | string | Literal `ReleaseAuthoritySetNode` |
| `schema_version` | string | Literal `release_authority_set_node.v0.1` |
| `authority_set_id` | string | Stable content-addressed identifier for this authority-set payload; normally the CIDv1 of the canonical node record |
| `channel_scope` | array[string] | Release channels governed by this set, using release-channel vocabulary such as `public_rc`, `testnet`, `mainnet`, or `dev` when those channels are otherwise authorized |
| `authorized_signers` | array[object] | Signer entries described below |
| `effective_from_phase` | string | Phase identifier where the set becomes effective |
| `supersedes_authority_set_cid` | string, optional | CID of the prior `ReleaseAuthoritySetNode` replaced by this set |
| `genesis_sunset_disposition` | string | How this set continues or rotates after Genesis authority expires |

Each `authorized_signers` entry contains:

| Field | Type | Meaning |
|---|---|---|
| `signer_label` | string | Human-stable label such as `phase_1335_release_operator_ed25519` |
| `signature_scheme` | string | One of the legal scheme labels in Section 4 |
| `public_key_hex` | string | Lowercase hex public key bytes for the scheme profile, or the scheme-specific aggregate/verification key when activated |
| `added_at_phase` | string | Phase that introduced the signer entry |
| `status` | string | `active`, `planned`, `retired`, or `revoked` |

A conforming v0.1 public-RC authority set has exactly one active entry for
`ed25519_phase_1335`. Planned threshold entries may be described for migration
analysis, but they do not authorize verification while their status is
`planned`.

---

## 4. Legal `signature_scheme` Vocabulary

The public-RC v0.1 vocabulary is closed:

| `signature_scheme` | Status | Verification profile | Notes |
|---|---|---|---|
| `ed25519_phase_1335` | active | Ed25519 verification over raw bytes decoded from `signed_preimage_sha256`, with preimage produced by `compute_signed_preimage_sha256()` and public key `5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a` | This is the only currently active release authority scheme. It preserves the existing validator behavior. |
| `threshold_bls_v1` | planned | Future threshold-BLS aggregate release authority profile, not yet implemented and not yet authorized | Must fail closed until a future SENSITIVE activation phase ratifies keys, threshold policy, aggregation rules, and verifier code. |

Unknown values are invalid. A verifier that encounters an unrecognized
`signature_scheme` must hard stop with `release_authority_unknown_signature_scheme`.
It must not fall back to Ed25519, infer a scheme from key length, or treat an
unknown string as a retrieval hint.

A verifier that encounters a known but inactive scheme such as
`threshold_bls_v1` while its status is `planned` must hard stop with
`release_authority_signature_scheme_not_active`.

---

## 5. Verifier Dispatch Semantics

When a future `ReleaseAttestationEdge` includes `signature_scheme`, the verifier
selects the verification algorithm by the exact scheme label and the referenced
`ReleaseAuthoritySetNode`.

Dispatch rules:

1. If `signature_scheme` is absent in the current v0.1 legacy assertion shape,
   the verifier may continue the current Ed25519-only path as
   `ed25519_phase_1335` until Row 21i defines the compatibility field behavior.
2. If `signature_scheme == "ed25519_phase_1335"`, the verifier uses the current
   Phase 1335 Ed25519 profile: recompute `compute_signed_preimage_sha256()`,
   require `signed_preimage_domain == "ILC_RELEASE_ARTIFACT_SIGNATURE_V1"`,
   require the authorized Ed25519 public key, and verify `signature_hex` over
   the raw 32-byte preimage digest.
3. If `signature_scheme == "threshold_bls_v1"` before activation, the verifier
   fails closed with `release_authority_signature_scheme_not_active`.
4. If `signature_scheme` is unknown, the verifier fails closed with
   `release_authority_unknown_signature_scheme`.
5. If the signer key is absent from the current authority set for the release
   channel, the verifier fails closed with `release_authority_signer_not_authorized`.
6. If the authority set channel scope does not include the asserted release
   channel, the verifier fails closed with `release_authority_set_channel_scope_mismatch`.

No dispatch path may silently accept an assertion under a weaker or different
scheme because another verifier path succeeds.

---

## 6. Downgrade Protection

Downgrade protection is mandatory. A verifier must not accept a weaker scheme
for a release assertion, release channel, or successor authority record that was
previously verified under a stronger or newer active scheme unless an explicit
valid authority-set rotation authorizes that transition.

For v0.1, `ed25519_phase_1335` is the only active scheme, so this rule is mostly
a migration invariant for Row 21i and later threshold work. Once any stronger or
multi-signer scheme becomes active, verifier state or channel-index state must
be able to detect and reject a later assertion that attempts to return to a
legacy scheme without a valid rotation record. The expected rejection token is
`release_authority_downgrade_detected`.

---

## 7. Rotation And Supersession

Authority rotation creates a new immutable `ReleaseAuthoritySetNode` whose
`supersedes_authority_set_cid` points to the prior set. The old node is not
mutated. A `superseded_by` relation may exist later as a derived index or a
separate `ReleaseChannelIndexNode` relation, but it is not a required field in
the old content-addressed payload.

Rotation rules:

1. Historical authority sets remain available for historical release
   verification. They are retained, not deleted.
2. A successor set must be signed by the authority set it supersedes, or by
   Genesis authority during the bootstrap period.
3. Competing successor records for the same prior authority-set CID and channel
   fail closed with `release_authority_rotation_race` unless a later channel
   index or governance rule defines the canonical successor.
4. A release assertion that references a superseded authority set for a channel
   after the effective successor phase fails closed with
   `release_authority_set_superseded`, except when verifying historical
   releases whose attestation date and release node lineage are within the old
   set's effective range.
5. Rotation evidence must bind the old authority set CID, new authority set CID,
   channel scope, effective phase, and signer status transitions.

---

## 8. Genesis-Sunset Relationship

For public RC, Genesis may publish the first valid `ReleaseAuthoritySetNode`.
After that first set is committed, the system is self-maintaining: rotations are
authorized by the existing authority set rather than by recurring Genesis
participation.

The required `genesis_sunset_disposition` value for the initial public-RC set is:

```text
genesis_signs_initial_authority_set_then_successor_sets_self_rotate
```

This means Genesis signs once for the initial authority root. After Genesis
sunset, the extant release authority set signs successor sets. If the only
active signer is lost before a successor threshold policy is activated, that is
a signer-loss governance problem for `SIM-RELEASE-THRESHOLD-BLS-AUTHORITY-00`
and later authority recovery design; this spec does not pretend that a lost
single key can be recovered without a valid governance path.

---

## 9. Relationship To CDL-121 And Row 21i

This spec is a precursor to later schema and CDL work. It does not ratify
CDL-121 and does not amend the current `ReleaseAttestationEdge` schema.

Row 21i may use this vocabulary to add forward-compatible fields such as
`signature_scheme` and `release_authority_set_ref`. Row 21i must preserve the
current Phase 1335 Ed25519 behavior for existing assertions and must fail closed
for inactive `threshold_bls_v1` evidence until a later SENSITIVE activation
phase exists.

---

## 10. Non-Claims

This phase does not authorize or claim:

- runtime changes in `ilc_core/`;
- a new live release key;
- a signing ceremony;
- threshold-BLS activation;
- addition of `signature_scheme` to current release assertions;
- CDL-121 ratification or any CDL mutation;
- publication, package upload, PyPI change, public mirror push, or VPS mutation;
- graph/Atlas/LMDB write;
- package install or upgrade apply;
- public RC activation, mainnet, production minting, settlement, epoch, wallet,
  validator, jury, or Werner-credit mutation.

---

## 11. Candidate Initial Authority Set Shape

```json
{
  "node_kind": "ReleaseAuthoritySetNode",
  "schema_version": "release_authority_set_node.v0.1",
  "authority_set_id": "cidv1-of-canonical-authority-set-record",
  "channel_scope": ["public_rc"],
  "authorized_signers": [
    {
      "signer_label": "phase_1335_release_operator_ed25519",
      "signature_scheme": "ed25519_phase_1335",
      "public_key_hex": "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a",
      "added_at_phase": "phase_1335",
      "status": "active"
    },
    {
      "signer_label": "future_threshold_release_authority",
      "signature_scheme": "threshold_bls_v1",
      "public_key_hex": "not_assigned",
      "added_at_phase": "future_sensitive_activation_phase",
      "status": "planned"
    }
  ],
  "effective_from_phase": "GAP-RELEASE-AUTHORITY-SET-NODE-SPEC-00",
  "genesis_sunset_disposition": "genesis_signs_initial_authority_set_then_successor_sets_self_rotate"
}
```
