# Release Artifact Manifest Schema 1213 v0.1

**Phase:** 1213
**Window:** 1209-1217
**Date:** 2026-05-05
**Status:** SCHEMA COMMITTED - CDL-086 NOT RATIFIED
**Authority:** CDL-086 prelock §5 condition 1

`release_artifact_manifest_schema_committed_phase_1213`

---

## 1. Purpose

This schema defines the minimum machine-verifiable manifest for any ILC public release
artifact. It is a ratification-prep artifact for CDL-086 and does not authorize public
repository publication, public release artifact distribution, public launch claims, or
CDL-086 ratification.

---

## 2. Required Fields

Every public release artifact manifest MUST contain exactly these required semantic fields:

| Field | Type | Rule |
|-------|------|------|
| `artifact_id` | string | Unique lowercase identifier: `ilc-artifact:<slug>@phase-<positive integer>` |
| `artifact_type` | string | One of the allowed artifact types in §3 |
| `canonical_hash` | string | `sha256:<64 lowercase hex characters>` |
| `lineage_reference` | string | Either `genesis:<genesis_v>` or `artifact:<artifact_id>@<canonical_hash>` |
| `produced_phase` | integer | Positive phase number where the artifact was produced |
| `ratification_token` | string | Governing CDL/ADR/token basis; non-empty |
| `signing_status` | string | One of `signed`, `unsigned`, `deferred` |

`NaN`, `Infinity`, `-Infinity`, empty strings, SHA-512 and MD5, uppercase hash hex, free-text
lineage strings, and artifact types outside §3 are invalid.

---

## 3. Allowed Artifact Types

The allowed artifact type list is exhaustive:

```text
runtime_module
genesis_bundle
cli_binary
documentation_bundle
source_release_tarball
public_repository_tag
container_image
star_map_release_envelope
operator_bootstrap_bundle
verification_bundle
```

Any unlisted type is invalid until a later ratified governance artifact updates this list.

---

## 4. Canonical Hash Format

The canonical hash format is:

```text
sha256:<lowercase hex, exactly 64 characters>
```

Only SHA-256 is valid for this manifest schema. Hashes must be over the canonical artifact
bytes defined by the artifact-producing process. If the artifact is a JSON machine surface,
the producing process must use deterministic JSON serialization with sorted keys and
non-finite numbers rejected.

---

## 5. Lineage Reference Format

Valid lineage references are:

```text
genesis:<genesis_v>
artifact:<artifact_id>@<canonical_hash>
```

Examples:

```text
genesis:v0.1
artifact:ilc-artifact:runtime-module@phase-1213@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

Free-text lineage references are invalid.

---

## 6. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "additionalProperties": false,
  "properties": {
    "artifact_id": {
      "pattern": "^ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*$",
      "type": "string"
    },
    "artifact_type": {
      "enum": [
        "runtime_module",
        "genesis_bundle",
        "cli_binary",
        "documentation_bundle",
        "source_release_tarball",
        "public_repository_tag",
        "container_image",
        "star_map_release_envelope",
        "operator_bootstrap_bundle",
        "verification_bundle"
      ],
      "type": "string"
    },
    "canonical_hash": {
      "pattern": "^sha256:[0-9a-f]{64}$",
      "type": "string"
    },
    "lineage_reference": {
      "oneOf": [
        {
          "pattern": "^genesis:v[0-9]+(\\.[0-9]+)*$",
          "type": "string"
        },
        {
          "pattern": "^artifact:ilc-artifact:[a-z0-9][a-z0-9-]*@phase-[1-9][0-9]*@sha256:[0-9a-f]{64}$",
          "type": "string"
        }
      ]
    },
    "produced_phase": {
      "minimum": 1,
      "type": "integer"
    },
    "ratification_token": {
      "minLength": 1,
      "type": "string"
    },
    "signing_status": {
      "enum": [
        "signed",
        "unsigned",
        "deferred"
      ],
      "type": "string"
    }
  },
  "required": [
    "artifact_id",
    "artifact_type",
    "canonical_hash",
    "lineage_reference",
    "produced_phase",
    "ratification_token",
    "signing_status"
  ],
  "type": "object"
}
```

---

## 6.1 Public RC Packaging Gate Carry-Forward

This schema is the minimum manifest schema. A future public-RC release packet
that contains or references source/package artifacts must also reference clean
source export evidence from the public RC packaging gate recorded in
`docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md`.

The release packet must not describe a source/package artifact as public-RC
clean unless the corresponding materialized public tree has:

- zero `PUBLIC_RC_EXCLUDE` markers;
- zero imports of stripped helper modules;
- deterministic file hashes;
- marker-scan and import-scan evidence;
- legacy untagged-file review state;
- counsel/IP/publication clearance status;
- explicit non-claims for any still-deferred public path or economics gate.

```text
release_artifact_packet_must_reference_clean_export_gate
public_rc_package_export_must_be_public_tree_clean_not_flag_flip
legacy_untagged_docs_default_review_required_before_public_export
```

---

## 7. Non-Claims

This schema does not ratify CDL-086, approve counsel items, authorize public release,
authorize public repository publication, authorize v0.2 signing, or produce a release
artifact.
