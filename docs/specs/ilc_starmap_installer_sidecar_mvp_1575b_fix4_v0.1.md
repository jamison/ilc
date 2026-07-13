# ILC StarMap Installer Sidecar MVP 1575b-Fix4 v0.1

## Purpose and Boundary

This document defines the minimum local StarMap Installer Sidecar MVP required before
the public-RC publication gate can consume bounded Atlas slice fixtures. The sidecar
name is `ilc.sidecar.starmap_installer`.

The MVP verifies unsigned local AtlasSliceManifest fixtures, materializes a
deterministic local node-record projection, and emits deterministic install receipts.
It does not sign production artifacts, fetch remote blobs, publish packages, operate
a public listing, activate public RC, clear economics guards, mint ECU, settle ILC,
or execute an epoch transition.

## Host Posture

The sidecar is CLI-compatible and can later be hosted by OpenClaw, Codex, or another
operator shell. Those hosts are not protocol substrates. The source of truth remains
the signed AtlasSliceManifest plus the canonical private repository until the public
RC gate explicitly produces signed publication artifacts.

## MVP Source of Truth

Phase 1575b-Fix4 consumes the two Phase 1575b-Fix3 fixture manifests:

- `tests/fixtures/starmap/core_public_rc_slice_fixture.json`
- `tests/fixtures/starmap/economic_soft_rc_slice_fixture.json`

Those files are AtlasSliceManifest JSON objects, not full remote blob packages. The
MVP therefore materializes deterministic node-record files from `content_entries`.
That is intentionally narrower than the Window 1576 full materializer, which will
resolve separately fetched node/content blobs.

## Future Public-RC Slice Package Fields

The full signed package profile must preserve these fields:

- `slice_id`
- `slice_version`
- `manifest_schema_version`
- `parent_manifest_hashes`
- `supersedes`
- `signer`
- `authority_scope`
- `authority_trace`
- `nodes`
- `edges`
- `permissions`
- `required_tests`
- `build_entrypoints`
- `exclusion_rules`
- `compatibility`
- `signature` or `signature_placeholder` for fixture-only tests

The Fix4 MVP maps the existing AtlasSliceManifest fields to local verification and
receipt evidence. It does not rewrite the fixture schema.

## Commands

The MVP exposes:

```text
ilc-starmap-installer verify <manifest>
ilc-starmap-installer materialize --dry-run <manifest>
ilc-starmap-installer materialize <manifest> --target <dir>
ilc-starmap-installer receipt <manifest>
```

The implementation is in `ilc_core/sidecars/starmap_installer.py`; the command wrapper
is `tools/ilc_starmap_installer.py`. A later native CLI phase may route these through
`ilc starmap ...` after the command namespace is selected.

## Versioning

Manifests are content-addressed records. Published manifests are never rewritten. A
later manifest supersedes an earlier one only by naming the earlier manifest hash and
carrying appropriate signer authority. A verifier must be able to validate the new
manifest without trusting transport.

## Overlap and Conflict Rule

Slice overlap is allowed only when the same `node_id` commits to the same hash. The
MVP dedupes that case. The same `node_id` with a different hash is a hard conflict
unless a future signed supersession authority explicitly authorizes the replacement.

The full profile must also reject the same `edge_id` with a different preimage and
must treat incompatible guard-state commitments as hard conflicts.

## Safety Rules

The MVP enforces these local safety rules:

- Manifest read size is capped at 10 MiB.
- Protocol JSON hashes use deterministic key ordering and compact separators.
- Floats are rejected before canonical receipt or manifest hashing.
- Materialization rejects absolute output paths, parent traversal, and filesystem root targets.
- Writes use temporary files followed by `os.replace`.
- Public fixture materialization rejects any node-record text containing `PUBLIC_RC_EXCLUDE`.
- The implementation uses no network access, private keys, subprocess shell invocation, or PRNG.

## Receipts

Install receipts include:

- `manifest_hash`
- `slice_id`
- `slice_version`
- `materialized_file_count`
- `content_hashes`
- `test_commands_declared`
- `installer_version`
- `created_at_policy`
- `receipt_sha256`

The MVP uses `created_at_policy=deterministic_test_fixture`. Wall-clock time is not
part of the canonical receipt hash.

## Public-RC Non-Claims

Phase 1575b-Fix4 does not publish a public sidecar repository, operate a public
package listing, sign Genesis artifacts, activate public serving, change repository
access policy, clear any economics guard, mint ECU, settle ILC, execute epoch
transition, or authorize Phase 1575c by itself.

## Retained Evidence

Retained evidence is written at:

```text
out/block6_starmap_installer_sidecar_fix4/evidence_records.json
```

The evidence records verification, dry-run materialization, and deterministic receipt
generation for the Core Public-RC Slice and Economic Soft-RC Slice fixtures.
