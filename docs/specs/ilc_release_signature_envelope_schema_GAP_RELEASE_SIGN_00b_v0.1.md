# ILC Release Signature Envelope Schema GAP-RELEASE-SIGN-00b v0.1

**Phase:** GAP-RELEASE-SIGN-00b
**Date:** 2026-09-04
**Status:** COMPLETE
**Authority:** CDL-086, ADR-0036, and `GAP-RELEASE-SIGN-00a`
**Target release:** `ilc-core==0.4.15`

## §1 - Authority And Inheritance

This schema defines the detached signature envelope format for installable ILC
release artifacts. It extends the Phase 1213 release artifact manifest schema
and the GAP-PUBLIC-INSTALL-01 installable manifest extension by reference only.
It does not mutate either schema file.

`GAP-RELEASE-SIGN-00a` confirmed that future
`signing_status: "signed"` claims mean an artifact hash is covered by a
detached release envelope. ADR-0036 requires release envelopes to bind release
version, package artifact hashes, release-key registration reference, and
Genesis lineage context. This phase defines the machine schema and unsigned
builder surface. GAP-RELEASE-SIGN-00c remains the sensitive signing ceremony.

## §2 - Envelope JSON Format

One envelope JSON object signs one installable manifest artifact record.

```json
{
  "artifact_id": "ilc-artifact:ilc-core-python-wheel-0415@phase-1627",
  "artifact_sha256": "058e2deec5656d25cc92de3d16acd8db01778f26c18e6405e06db48569ce7524",
  "genesis_lineage_ref": "adr-0037:genesis-canonical-lineage-contract",
  "prior_release_envelope_ref": "none:first-public-rc-release",
  "release_id": "ilc-core-0.4.15",
  "release_key_registration_ref": "adr-0036:public-rc-operational-release-key-registration",
  "schema_version": "GAP_RELEASE_SIGN_00b_v0.1",
  "signature_hex": "<128-char lowercase Ed25519 signature hex>",
  "signed_at": "1970-01-01T00:00:00Z",
  "signed_preimage_algorithm": "sha256_of_canonical_json",
  "signed_preimage_domain": "ILC_RELEASE_ARTIFACT_SIGNATURE_V1",
  "signed_preimage_sha256": "<64-char lowercase SHA-256 hex>",
  "signer_public_key_hex": "<64-char lowercase Ed25519 public key hex>",
  "signing_algorithm": "Ed25519"
}
```

Mandatory constraints:

- `schema_version` is exactly `GAP_RELEASE_SIGN_00b_v0.1`.
- `release_id` is exactly the release identifier whose manifest contains the
  artifact, for example `ilc-core-0.4.15`.
- `artifact_id` matches one manifest artifact id.
- `artifact_sha256` matches the manifest artifact `canonical_hash` without the
  `sha256:` prefix.
- `release_key_registration_ref` binds the signature to the ADR-0036 operational
  release-key registration authority.
- `genesis_lineage_ref` binds the signature to the ADR-0037 Genesis canonical
  lineage contract.
- `prior_release_envelope_ref` binds the signature to the previous release
  envelope hash, or to the explicit first-release sentinel
  `none:first-public-rc-release`.
- `signing_algorithm` is exactly `Ed25519`.
- `signer_public_key_hex` is 64 lowercase hex characters for signed envelopes.
- `signature_hex` is 128 lowercase hex characters for signed envelopes.
- `signed_at` is the deterministic non-wall-clock placeholder
  `1970-01-01T00:00:00Z`.
- `signed_preimage_algorithm` is exactly `sha256_of_canonical_json`.
- `signed_preimage_domain` is exactly `ILC_RELEASE_ARTIFACT_SIGNATURE_V1`.
- `signed_preimage_sha256` is the SHA-256 digest of the canonical signed
  preimage payload defined in §3.

Unsigned ceremony skeletons may use empty `signer_public_key_hex` and
`signature_hex` only when a validator is explicitly called with
`allow_unsigned_placeholders=True`. Signed-envelope validation rejects those
placeholders by default.

## §3 - Signed Preimage Construction

The Ed25519 signing ceremony signs the 32-byte SHA-256 digest of this canonical
JSON payload:

```json
{
  "artifact_id": "<artifact-id>",
  "artifact_sha256": "<64-char lowercase sha256>",
  "genesis_lineage_ref": "adr-0037:genesis-canonical-lineage-contract",
  "prior_release_envelope_ref": "none:first-public-rc-release",
  "release_id": "<release-id>",
  "release_key_registration_ref": "adr-0036:public-rc-operational-release-key-registration",
  "schema_version": "GAP_RELEASE_SIGN_00b_v0.1",
  "signed_at": "1970-01-01T00:00:00Z",
  "signed_preimage_domain": "ILC_RELEASE_ARTIFACT_SIGNATURE_V1",
  "signing_algorithm": "Ed25519"
}
```

Canonicalization is:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")
```

Then `sha256(canonical_bytes).digest()` is the ceremony signing input, and
`sha256(canonical_bytes).hexdigest()` is stored as `signed_preimage_sha256`.

The explicit domain, release-id, release-key-registration, Genesis-lineage, and
prior-envelope bindings prevent an artifact hash signature from being silently
replayed as a different release-signing surface, release set, authority chain,
or release lineage.

## §4 - Envelope Set Format

A release envelope set for version `0.4.15` is published as
`ilc_core_0415_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json` by
GAP-RELEASE-SIGN-00c.

```json
{
  "envelopes": {
    "<artifact-id>": {
      "...": "one envelope object"
    }
  },
  "schema_version": "GAP_RELEASE_SIGN_00b_v0.1",
  "version": "0.4.15"
}
```

The envelope-set keys must exactly equal the manifest artifact ids when checked
against a manifest. Each envelope's `release_id` must equal `ilc-core-<version>`.

## §5 - Integration With Manifest `signing_status`

An installable manifest artifact may move from `signing_status: "unsigned"` to
`signing_status: "signed"` only after GAP-RELEASE-SIGN-00c produces an envelope
set covering every artifact and tests prove each envelope is structurally valid
and bound to the exact manifest artifact id and hash.

This schema does not embed signatures into the installable manifest. The
envelope set is detached and companion-published.

## Non-Claims

No private key was generated or accessed. No real signature was produced. No
manifest instance was mutated. No `signing_status` field was changed. No PyPI
upload, package yank, mirror generation, mirror push, public RC activation,
epoch transition, settlement, ECU minting, or ILC minting occurred.
