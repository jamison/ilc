# ILC Release Signing Authority Reconciliation GAP-RELEASE-SIGN-00a v0.1

**Phase:** GAP-RELEASE-SIGN-00a
**Date:** 2026-09-04
**Status:** COMPLETE
**Target package:** `ilc-core==0.4.15`
**Target installable manifest:** `docs/specs/ilc_installable_release_manifest_ilc_core_0415_GAP_INVITE_SHORTCODE_DEPLOY_00_v0.1.json`

## §1 - Current Unsigned State

Direct read of the `_0415` installable manifest confirms both current package
artifacts remain unsigned before the release-signing chain.

| Artifact | Type | SHA-256 | Size bytes | Signing status | Download URL |
|---|---|---:|---:|---|---|
| `ilc-artifact:ilc-core-python-wheel-0415@phase-1627` | `python_wheel` | `sha256:058e2deec5656d25cc92de3d16acd8db01778f26c18e6405e06db48569ce7524` | 1451016 | `unsigned` | `https://files.pythonhosted.org/packages/18/dc/8dfef2e09b2892fb6c8b724e1fd41982dd1ce90d9b82b959a846e3e1ee28/ilc_core-0.4.15-py3-none-any.whl` |
| `ilc-artifact:ilc-core-python-sdist-0415@phase-1627` | `python_sdist` | `sha256:3aea9f609898a1f841de26a64cd8c9706be4a16094b14934879c78456232f21e` | 1183400 | `unsigned` | `https://files.pythonhosted.org/packages/06/1e/351517b9b0ec7f7da3c2c3f3a1de835f563dba7e4207f56eedc32cc6f421/ilc_core-0.4.15.tar.gz` |

## §2 - Schema Gap Record

The Phase 1213 release artifact manifest schema defines `signing_status` as a
required string field and restricts it to `signed`, `unsigned`, or `deferred`.
It does not define what cryptographic proof must accompany `signed`, and it
does not define a detached envelope schema.

The GAP-PUBLIC-INSTALL-01 installable extension inherits the same
`signing_status` values and adds installer metadata (`platform`, `arch`,
`channel`, `size_bytes`, `download_url`, and conditional
`min_python_version`). It contains no `signature_envelope`, `detached_sig`,
or `signed_by` artifact field.

Runtime validation in `ilc_core/rc/release_artifact_production_gate.py` accepts
`unsigned` as a valid state and records `release_envelopes_produced: False`
with `release_envelope_production_authorized: False` for the unsigned policy
path.

## §3 - Historical Constraints From Phases 1321 And 1447

Phase 1321 rehearsed the release-key envelope procedure only. It explicitly
recorded that release-key generation, release-envelope production, public-key
export, signing material creation, and real signing were not authorized or
performed. The rehearsal used dummy identifiers and records process shape, not
current release authority.

Phase 1447 is historical v0.3 signing-attestation context. It emitted
`release_artifacts_signed_phase_1447`, but the corresponding status module
records `PHASE_1447_MANIFEST_SIGNATURE = None`, `PHASE_1447_PUBLIC_REPOSITORY_PUBLISHED = False`,
and `PHASE_1447_EPOCH_TRANSITION_AUTHORIZED = False`. This token is not a
claim that the current `ilc_core_0415` wheel or sdist has been signed.

## §4 - CDL-086 Authority Scope

CDL-086 is ratified and supplies the governance basis for public-launch
release packaging, release artifacts, publication boundaries, and the
ADR-0036 release-key dependency. CDL-086 does not prescribe a specific
signature algorithm, key type, or detached envelope wire schema.

ADR-0036 supplies the relevant architecture: the operational release key traces
to Genesis authority, and a release envelope signed by that operational key
binds release version, package artifact hashes, optional star-map/runtime
artifact hashes, prior envelope hash, release-key registration reference, and a
Genesis root or authorized transition-envelope reference. GAP-RELEASE-SIGN-00b
may specify the exact envelope schema without amending CDL-086, provided it
stays inside this authority.

## §5 - Detached Envelope Intent Decision

**CONFIRMED:** In the reconciled ILC release system, `signing_status: "signed"`
means the artifact hash is covered by a detached release envelope published
alongside the installable manifest or referenced from the release packet.

This phase does not choose the final key type, signing algorithm, envelope
field names, or verification module API. Those details are explicitly assigned
to GAP-RELEASE-SIGN-00b, with the sensitive signing ceremony assigned to
GAP-RELEASE-SIGN-00c.

## §6 - Launch Gate Dependency

The current public RC launch gate scan did not find a B3 activation-matrix row
requiring `signing_status: "signed"` before public mirror push. Signing remains
on the current pre-RC signing lane, and this reconciliation does not authorize
publication, mirror push, or launch.

## §7 - Prerequisites Unlocked For GAP-RELEASE-SIGN-00b

This phase settles these points for GAP-RELEASE-SIGN-00b:

- The current `_0415` installable manifest is unsigned and must not be treated
  as signed until GAP-RELEASE-SIGN-00c completes.
- `signing_status: "signed"` requires a detached release envelope covering the
  artifact hash.
- Historical Phase 1447 v0.3 signing tokens are not current 0.4.15 signing
  tokens.
- CDL-086 and ADR-0036 authorize specifying a release-envelope schema, but do
  not themselves define the concrete schema.

Open questions for GAP-RELEASE-SIGN-00b:

- The exact envelope JSON schema and canonical payload boundaries.
- The release signing key algorithm and public-key identifier format.
- Whether each artifact gets an individual envelope or a release-set envelope
  containing per-artifact records.
- The verifier behavior for missing, malformed, mismatched, or future-version
  envelopes.

## Non-Claims

No key generation occurred. No release envelope was produced. No manifest field
was mutated. No signing status was changed. No release signing, manifest
signing, PyPI upload, yank, mirror generation, mirror push, public RC
activation, epoch transition, settlement, ECU minting, or ILC minting occurred.
