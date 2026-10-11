# ILC Homoiconic Release Object Spec

**Phase:** GAP-HOMOICONIC-RELEASE-OBJECT-SPEC-00  
**Version:** v0.1  
**Date:** 2026-10-05  
**Status:** Spec-only candidate; no CDL mutation and no runtime activation  
**Authority context:** CDL-075 CIDv1 graph persistence, the committed public release workflow, and the post-1575c homoiconic release distribution lane

---

## 1. Purpose

This document specifies the graph data model for representing ILC software
releases as first-class ILC graph objects. A release is not merely a file at a
URL. It is a content-addressed graph object with explicit artifact, build, and
attestation lineage.

The v0.1 model defines four canonical object kinds:

1. `SoftwareReleaseNode`
2. `ArtifactNode`
3. `BuildRecipeNode`
4. `ReleaseAttestationEdge`

Required-section index: `SoftwareReleaseNode`, `ArtifactNode`,
`BuildRecipeNode`, `ReleaseAttestationEdge`, `hash linkage`, `CIDv1`, and
`Non-claims`.

This spec is intentionally non-executable. It prepares the later
`GAP-HOMOICONIC-RELEASE-OBJECT-CDL-00` governance phase and later distributed
artifact fetch phases.

---

## 2. Authority And Compatibility

CDL-075 ratifies CIDv1 graph persistence for truth primitive graph records,
including canonical node records, CIDv1 derivation, LMDB node/edge layout, and
idempotent write semantics. This release-object spec reuses that graph-native
content-addressing posture for release metadata.

The existing public release workflow remains authoritative for package
publication until a later phase replaces or supplements it. In particular:

- artifact bytes are still checked by SHA-256 and size;
- release envelopes use `SIGNED_PREIMAGE_DOMAIN =
  "ILC_RELEASE_ARTIFACT_SIGNATURE_V1"`;
- signed preimages are SHA-256 digests of canonical JSON release-envelope
  material;
- the operational release signature algorithm is Ed25519 under the Phase 1335
  release key lineage;
- PyPI and GitHub remain delivery and mirror channels until a later authorized
  fetch/deployment phase demotes them.

`ReleaseAttestationEdge.signature` is compatible with the existing Ed25519
release-envelope ceremony. Future CDL work may add threshold or quorum release
authority, but this spec does not do so.

---

## 3. Common Encoding Rules

All release-object graph records use deterministic JSON-compatible maps unless a
later CDL ratifies a DAG-CBOR-only encoding.

Common constraints:

- `node_kind` and `edge_type` values are exact ASCII strings.
- All hashes are lowercase hex.
- `cid` fields are strict CIDv1 strings derived from canonical graph record
  bytes under the ratified ILC CIDv1 profile.
- `sha256` is 64 lowercase hex characters over the exact artifact bytes.
- `blake3`, when present, is 64 lowercase hex characters over the exact
  artifact bytes.
- `size_bytes` is a non-negative integer.
- Timestamps use UTC ISO-8601 strings with a trailing `Z`.
- Optional fields are omitted when absent rather than set to `null`, unless a
  future CDL explicitly requires nullable semantics.
- Private keys, API tokens, package-index credentials, VPS credentials, and
  local filesystem secrets must never appear in any release object.

---

## 4. SoftwareReleaseNode Schema

`SoftwareReleaseNode` represents a named software release as an ILC graph node.
It binds version identity, release channel, source commit, artifact membership,
build recipe, changelog, and release-key attestation.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `node_kind` | string | Literal `SoftwareReleaseNode` |
| `schema_version` | string | Literal `software_release_node.v0.1` |
| `package_name` | string | Package or component name, for example `ilc-core` |
| `version` | string | Semantic version string released by this node |
| `release_channel` | string | `public_rc`, `testnet`, `mainnet`, `dev`, or later ratified channel |
| `release_date` | string | UTC ISO-8601 release timestamp |
| `source_commit` | string | Git commit that produced the release artifacts |
| `artifact_cids` | array[string] | One or more `ArtifactNode.cid` values included in this release |
| `build_recipe_cid` | string | CIDv1 of the governing `BuildRecipeNode` |
| `release_key_pubkey` | string | Public release-signing key identifier or key hex under the release workflow |
| `release_signature_ref` | string | Reference to the release envelope or attestation edge carrying the signature |
| `changelog_hash` | string | SHA-256 of the release changelog text or file |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `prior_release_cid` | string | CIDv1 of the prior `SoftwareReleaseNode` in the package lineage |
| `genesis_lineage_ref` | string | Release lineage authority reference, such as ADR-0037 |
| `release_notes_cid` | string | CIDv1 of a longer release notes object |
| `supersedes_release_cids` | array[string] | Release objects superseded by this release |

Canonical identity:

The `SoftwareReleaseNode.cid` is derived from the canonical graph record for the
node. The CID must not be derived from the wheel, sdist, binary tarball, or a
transport URL alone. Artifact bytes are represented by `ArtifactNode` records.

---

## 5. ArtifactNode Schema

`ArtifactNode` represents one concrete artifact byte sequence: a wheel, sdist,
binary tarball, installer script, or other release materialization.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `node_kind` | string | Literal `ArtifactNode` |
| `schema_version` | string | Literal `artifact_node.v0.1` |
| `cid` | string | CIDv1 of the canonical artifact record |
| `sha256` | string | SHA-256 of exact artifact bytes |
| `size_bytes` | integer | Artifact byte count |
| `package_name` | string | Package or component name |
| `package_version` | string | Artifact version |
| `artifact_type` | string | `wheel`, `sdist`, `binary_tarball`, `installer`, or later ratified type |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `blake3` | string | BLAKE3 digest of exact artifact bytes |
| `platform` | string | Platform tag, for example `macos-aarch64` or `linux-x86_64` |
| `python_abi` | string | Python ABI tag for wheels |
| `rust_target` | string | Rust target triple for native binaries |
| `source_urls` | array[string] | Non-authoritative retrieval hints; every fetched byte sequence must still match hash and CID |
| `pypi_filename` | string | Legacy PyPI filename hint |
| `github_release_asset` | string | Legacy GitHub asset name hint |

Transport boundary:

`source_urls` are hints only. They do not confer authority. A consumer must
verify `sha256`, `size_bytes`, and the release attestation before installing or
executing artifact bytes.

---

## 6. BuildRecipeNode Schema

`BuildRecipeNode` records the build intent and reproducibility boundary for one
or more artifacts.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `node_kind` | string | Literal `BuildRecipeNode` |
| `schema_version` | string | Literal `build_recipe_node.v0.1` |
| `source_commit` | string | Git commit built |
| `build_toolchain` | string | Toolchain descriptor, for example Python/Rust versions and build backend |
| `build_env_hash` | string | SHA-256 over the pinned build environment manifest |
| `build_command` | string | Deterministic command or script entrypoint used for the build |
| `reproducibility_hash` | string | SHA-256 over the reproducibility recipe or normalized build receipt |
| `build_date` | string | UTC ISO-8601 build timestamp |
| `builder_agent_id` | string | AgentID of the builder or release operator |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `container_image_digest` | string | Container image digest if a containerized build was used |
| `lockfile_hashes` | object | Map of dependency lockfile path to SHA-256 |
| `source_tree_hash` | string | Digest over an exported source tree snapshot |
| `known_nondeterminism` | array[string] | Explicitly documented nondeterministic inputs, if any |
| `reproducibility_verdict` | string | `reproducible`, `not_reproducible`, `partially_reproducible`, or `not_audited` |

Reproducibility boundary:

This node describes build inputs and claims. It does not prove that another
agent reproduced the build. Independent reproduction evidence belongs in later
attestation records defined by `GAP-REPRODUCIBLE-BUILD-ATTESTATION-00` or a
successor CDL.

---

## 7. ReleaseAttestationEdge Schema

`ReleaseAttestationEdge` states that a release includes an artifact, and binds
that statement to the release signing authority.

Required fields:

| Field | Type | Meaning |
|---|---|---|
| `edge_type` | string | Literal `RELEASE_ATTESTS_ARTIFACT` |
| `schema_version` | string | Literal `release_attestation_edge.v0.1` |
| `source` | string | `SoftwareReleaseNode.cid` |
| `target` | string | `ArtifactNode.cid` |
| `artifact_sha256` | string | SHA-256 of exact artifact bytes |
| `signed_preimage_domain` | string | Literal `ILC_RELEASE_ARTIFACT_SIGNATURE_V1` unless later amended |
| `signed_preimage_sha256` | string | SHA-256 of canonical release-envelope preimage payload |
| `signing_algorithm` | string | Literal `Ed25519` for the current release workflow |
| `signer_public_key_hex` | string | Phase 1335 release public key or later ratified release key |
| `signature_hex` | string | Ed25519 signature over raw 32 bytes decoded from `signed_preimage_sha256` |
| `attestation_date` | string | UTC ISO-8601 attestation timestamp |

Optional fields:

| Field | Type | Meaning |
|---|---|---|
| `release_envelope_ref` | string | Path, CIDv1, or URL hint for the release envelope set |
| `prior_release_envelope_ref` | string | Prior release envelope lineage reference |
| `release_key_registration_ref` | string | Release-key authority reference |
| `genesis_lineage_ref` | string | Genesis lineage authority reference |

Signature compatibility:

For the current workflow, `signed_preimage_sha256` is computed by
`compute_signed_preimage_sha256()` from the release helper. Operators sign the
raw 32 bytes decoded from that hex string. Consumers must not interpret
`signature_hex` as a signature over the artifact file, the printable hex string,
or the full release node JSON.

---

## 8. Hash linkage

The release-object chain is:

```text
source_commit
  -> BuildRecipeNode
  -> ArtifactNode(s)
  -> ReleaseAttestationEdge(s)
  -> SoftwareReleaseNode
```

Rules:

1. `BuildRecipeNode.source_commit` identifies the exact source commit.
2. `BuildRecipeNode.build_env_hash` and `reproducibility_hash` bind the
   declared build recipe.
3. `ArtifactNode.sha256` and optional `ArtifactNode.blake3` bind the exact
   artifact bytes.
4. `ArtifactNode.cid` identifies the canonical artifact metadata record, not a
   transport URL.
5. `ReleaseAttestationEdge.source` points to the `SoftwareReleaseNode.cid`.
6. `ReleaseAttestationEdge.target` points to the `ArtifactNode.cid`.
7. `ReleaseAttestationEdge.artifact_sha256` must equal the corresponding
   `ArtifactNode.sha256`.
8. `SoftwareReleaseNode.artifact_cids` must include every artifact attested by
   the release's current `ReleaseAttestationEdge` set.
9. Consumers must verify the attestation signature and artifact hash before any
   install or execution step.
10. CIDv1 derivation follows the ratified CDL-075 graph persistence authority
    until a release-object CDL ratifies a narrower profile.

The chain deliberately separates artifact bytes from graph records. A wheel may
be fetched from PyPI, GitHub, a peer, IPFS/CAS, a local cache, or a future ILC
fetch layer, but it is installable only when the bytes match the graph-rooted
artifact hash and release attestation.

---

## 9. Privacy And Secret Boundary

Release objects may contain public keys, public signatures, hashes, version
metadata, build recipes, and non-secret source references.

Release objects must not contain:

- private release keys;
- operator seed phrases;
- BLS, Ed25519, ML-DSA, or SPHINCS+ secret keys;
- PyPI API tokens;
- GitHub tokens;
- VPS SSH credentials;
- local absolute secret paths;
- unredacted environment dumps.

If a build recipe needs to mention a secret-dependent process, it records only a
public receipt, public key reference, or signed output.

---

## 10. Non-claims

This spec does not:

- mutate the CDL register;
- ratify new release-object authority;
- implement runtime writers or readers;
- publish any package;
- push or refresh the public mirror;
- replace PyPI, GitHub, or the current installer path;
- activate distributed artifact fetch;
- activate Werner serving credit;
- activate release quorum governance;
- create wallet, ECU, ILC, epoch, settlement, validator, VPS, public RC, or
  mainnet state;
- authorize any secret material to be committed.

---

## 11. Next Phase

The next governance phase is `GAP-HOMOICONIC-RELEASE-OBJECT-CDL-00`. It must
confirm the next available CDL number at execution time, decide whether these
node and edge kinds are ratified directly or through a narrower release-object
authority, and preserve the non-activation boundary unless a separate activation
phase is explicitly authorized.
