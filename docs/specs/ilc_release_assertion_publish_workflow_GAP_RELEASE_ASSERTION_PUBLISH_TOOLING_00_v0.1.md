# ILC Release Assertion Publish Tooling Workflow

**Phase:** GAP-RELEASE-ASSERTION-PUBLISH-TOOLING-00
**Version:** v0.1
**Date:** 2026-10-06
**Status:** Tooling workflow; dry-run only

## Purpose

This document defines the local tooling boundary for constructing ILC-native
software release assertions. It prepares the later SENSITIVE release assertion
publish ceremony, but does not itself authorize live publication.

The tooling builds JSON containing:

1. `SoftwareReleaseNode`
2. `ArtifactNode`
3. `BuildRecipeNode`
4. `ReleaseAttestationEdge`
5. a fixture-signed `native_submit_envelope` for dry-run provenance testing

The output is compatible with `ilc upgrade check` because each
`ReleaseAttestationEdge` includes `artifact_id`, `artifact_sha256`,
`signed_preimage_sha256`, `signer_public_key_hex`, and `signature_hex`.

## Tool

The command is:

```bash
python3 tools/publish_release_assertion.py \
  --version <VERSION> \
  --artifact-sha256 <64 lowercase hex> \
  --artifact-cid <CIDv1> \
  --artifact-size <positive integer> \
  --source-commit <40-or-64 lowercase hex> \
  --dry-run
```

Optional inputs:

- `--artifact-id`: override the derived
  `ilc-artifact:ilc-core-python-wheel-<version>@phase-1626` value.
- `--build-recipe-cid`: override the derived build recipe CIDv1.
- `--changelog-hash`: set the release-node changelog hash.
- `--release-date`: set a deterministic UTC `...Z` release timestamp.
- `--fixture-signing-key-hex`: fixture BLS secret for native-submit envelope
  dry-run signing.
- `--fixture-release-signing-key-hex`: fixture Ed25519 release secret for
  dry-run release-attestation signing.
- `--output`: atomically write the JSON output to a local file.

## Authority Boundary

This phase uses fixture key material only. The output is a construction and
validation artifact, not a live release assertion.

The later SENSITIVE ceremony phase must replace fixture signing with the
authorized release signing ceremony and, if authorized there, native QUIC
submission and well-known endpoint update.

## Atomic Output

When `--output` is supplied, the tool writes with:

1. `tempfile.mkstemp(dir=output_dir)`
2. write + flush + `os.fsync`
3. `os.chmod(..., 0o600)`
4. `os.replace(temp_path, output_path)`

Partial direct writes to the target path are forbidden.

## Verification Boundary

The dry-run JSON can be validated by the existing upgrade checker when the
checker is fixture-patched to trust the fixture Ed25519 public key. The runtime
upgrade checker in production remains anchored to the Phase 1335 release
authority key.

The native-submit envelope is included as provenance evidence only. Release
authority remains Ed25519 release-attestation verification.

## Non-Claims

This workflow does not:

- use a real Genesis key;
- submit to the native QUIC receiver;
- mutate LMDB;
- update the NGINX or well-known HTTPS cache;
- publish to PyPI, GitHub, or any mirror;
- change repository visibility;
- mutate any CDL.

## Later Ceremony Handoff

`GAP-RELEASE-ASSERTION-PUBLISH-CEREMONY-00` is the first phase that may perform
live release assertion publication. It must re-establish all live preconditions,
use the authorized release signing procedure, pin the receiver TLS fingerprint if
native QUIC submission is in scope, and record live publish receipts.
