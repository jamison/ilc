# ILC Release Channel Index Node Spec

**Phase:** GAP-RELEASE-CHANNEL-INDEX-NODE-SPEC-00  
**Version:** v0.1  
**Date:** 2026-10-13  
**Status:** Spec-only candidate; no runtime activation, no release assertion mutation, no CDL mutation  
**Authority context:** CDL-121 open/prelocked homoiconic release object taxonomy; Row 21g `ReleaseAuthoritySetNode`; Row 21i optional `ReleaseAttestationEdge.signature_scheme`; current fetch-server release assertion endpoint

---

## 1. Purpose

`ReleaseChannelIndexNode` is the graph-native record that answers one narrow
question:

> For release channel X, which signed software-release assertion is currently
> authoritative?

The current public-RC read path is operationally served by
`TruthPrimitiveGraphStore.get_latest_release_assertion(channel)` through
`GET /.well-known/ilc/software-release/latest.json`. That endpoint returns the
full signed release assertion payload for a channel, defaulting to `public_rc`,
and the caller still verifies the returned assertion with
`validate_release_assertion()`.

This spec defines the graph object that can later represent the same channel to
latest-assertion mapping without relying on an HTTP fetch server as the index.
It is not a runtime wiring phase.

---

## 2. Node Kind

`ReleaseChannelIndexNode` is an immutable content-addressed graph node. It maps
a release channel label to the latest verified release assertion CID for that
channel.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `node_kind` | string | Literal `ReleaseChannelIndexNode` |
| `schema_version` | string | Literal `release_channel_index_node.v0.1` |
| `channel` | string | Release channel label, such as `public_rc`, `testnet`, `mainnet`, `dev`, or a later ratified channel |
| `latest_assertion_cid` | string | CID of the full signed software-release assertion currently authoritative for this channel |
| `latest_version` | string | Human-readable diagnostic version string, such as `0.4.33`; not the canonical authority |
| `indexed_at_phase` | string | Phase that created this index record |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `authority_set_cid` | string | CID of the `ReleaseAuthoritySetNode` used to verify the indexed assertion, once that object is materialized |
| `supersedes_index_cid` | string | CID of the previous `ReleaseChannelIndexNode` for the same channel |
| `software_release_node_cid` | string | CID of the `SoftwareReleaseNode` inside the assertion, if materialized separately from the full assertion |
| `signature_scheme` | string | Effective release attestation scheme, for example `ed25519_phase_1335`; must match assertion validation results |
| `index_reason` | string | Diagnostic reason for the index publication, such as `new_package_release` or `authority_rotation` |

Optional fields are omitted when absent. They are not set to `null`.

---

## 3. Validation Rules

A conforming `ReleaseChannelIndexNode` is valid only if all of the following are
true:

1. `channel` is a non-empty ASCII release-channel label using the same channel
   vocabulary as `SoftwareReleaseNode.release_channel`.
2. `latest_assertion_cid` resolves to a full signed release assertion payload,
   not merely a wheel hash, package version string, Git tag, or transport URL.
3. The referenced assertion passes `validate_release_assertion()` under the
   active release authority rules.
4. The referenced assertion's `SoftwareReleaseNode.release_channel` equals the
   index node `channel`.
5. If `latest_version` is present in the assertion, the diagnostic
   `latest_version` in the index must match it. The assertion CID remains the
   canonical authority if diagnostic strings disagree.
6. If `authority_set_cid` is present, it must identify a valid
   `ReleaseAuthoritySetNode` whose channel scope includes `channel` and whose
   active signer/scheme validates the assertion.
7. If `signature_scheme` is present, it must equal the effective scheme returned
   by release assertion validation. In v0.1, this is `ed25519_phase_1335` for
   current public-RC assertions.

Failure of any rule is fail-closed. Future runtime work should use specific
machine-readable tokens, but this spec does not assign new runtime errors.

---

## 4. Update And Supersession Semantics

Channel index updates are append-only. A new current index record is published
by creating a new `ReleaseChannelIndexNode`; the old node is not mutated.

Rules:

1. `supersedes_index_cid`, when present, points backward to the prior index node
   for the same `channel`.
2. A prior node must not be edited to add a mutable `superseded_by` field.
   `superseded_by` may exist only as a derived index, materialized view, or
   separate graph relation.
3. Channel cardinality rule: at most one non-superseded
   `ReleaseChannelIndexNode` is current for a channel at any time.
4. Competing non-superseded index nodes for the same channel are a rotation or
   publication race. A verifier must fail closed until a later governance rule,
   channel-index tiebreaker, or authority-set rotation rule selects the
   canonical record.
5. Historical index nodes remain valid historical evidence and may be used to
   verify releases that were current during their effective period.

This closes the immediate schema gap identified by Row 21h: stale authority
records, replayed authority sets, and future downgrade attempts need a canonical
current-channel index before threshold-BLS activation can be safe.

---

## 5. Relationship To Current Fetch Server

The current fetch server behavior remains unchanged:

- `GET /.well-known/ilc/software-release/latest.json` is the operational read
  path for the current architecture.
- The endpoint accepts zero or one `channel` query parameter and defaults to
  `public_rc`.
- The endpoint obtains the payload from
  `TruthPrimitiveGraphStore.get_latest_release_assertion(channel)`.
- The endpoint serves the full signed assertion payload and rejects missing,
  invalid, oversized, or unserializable assertions.

`ReleaseChannelIndexNode` is the graph-native representation of the same
channel to latest-assertion mapping. A future implementation phase may make
upgrade discovery read channel-index nodes directly from the graph, while still
requiring `validate_release_assertion()` before a release is trusted.

---

## 6. Relationship To Release Authority Sets

Row 21g defines `ReleaseAuthoritySetNode`; Row 21i defines optional
`ReleaseAttestationEdge.signature_scheme` behavior. `ReleaseChannelIndexNode`
connects those ideas to channel state:

- current public-RC records may omit `authority_set_cid` while the authority set
  is not yet materialized as a live graph object;
- future records should include `authority_set_cid` once authority-set nodes are
  published;
- the index can carry the current assertion CID and the authority-set CID used
  to validate it;
- future downgrade protection depends on comparing new assertions against the
  canonical current index and its authority-set lineage.

This spec does not activate `threshold_bls_v1`. `threshold_bls_v1` remains a
known inactive scheme and must continue to fail closed until a later SENSITIVE
activation phase resolves the Row 21h carry-forward gaps.

---

## 7. Candidate Public-RC Shape

```json
{
  "node_kind": "ReleaseChannelIndexNode",
  "schema_version": "release_channel_index_node.v0.1",
  "channel": "public_rc",
  "latest_assertion_cid": "bafyreig47oqtnwxvd6feryuaw72qximlvzqb2e4oxz4c25dscmsogrurga",
  "latest_version": "0.4.32",
  "indexed_at_phase": "GAP-RELEASE-CHANNEL-INDEX-NODE-SPEC-00",
  "signature_scheme": "ed25519_phase_1335",
  "index_reason": "document_current_release_assertion_channel_mapping"
}
```

This is an illustrative shape only. It does not publish a live index node and
does not change the current public-RC assertion.

---

## 8. Future Implementation Work

Future phases should define and implement:

1. graph-native storage and retrieval of current channel index records;
2. verifier behavior for competing non-superseded index records;
3. authority-set lookup from `authority_set_cid`;
4. stale/replayed authority-set rejection using the channel index;
5. downgrade detection once more than one active release authority scheme exists;
6. a migration bridge from the current HTTP fetch path to direct graph-index
   discovery.

A natural follow-on phase is
`GAP-RELEASE-CHANNEL-INDEX-NODE-IMPL-00`.

---

## 9. Non-Claims

This phase does not authorize or claim:

- `ilc_core/` runtime changes;
- upgrade-check graph-index wiring;
- a live `ReleaseChannelIndexNode` publication;
- a live assertion rewrite;
- package upload, install, or apply behavior;
- public mirror push or repository visibility change;
- VPS mutation;
- signing ceremony or key change;
- `threshold_bls_v1` activation;
- CDL-121 ratification or any CDL mutation;
- graph/Atlas/LMDB live write;
- wallet, ECU, ILC, settlement, epoch, validator, jury, Werner-credit, public-RC,
  mainnet, or production minting mutation.
