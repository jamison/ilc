# ILC Public Install Distribution Reconciliation GAP-PUBLIC-INSTALL-00 v0.1

**Phase:** GAP-PUBLIC-INSTALL-00
**Date:** 2026-08-05
**Status:** COMPLETE
**Sensitivity:** NON-SENSITIVE

`public_install_state_reconciled_GAP_PUBLIC_INSTALL_00`
`pyproject_version_corrected_GAP_PUBLIC_INSTALL_00`
`install_layer_separation_documented_GAP_PUBLIC_INSTALL_00`

## 1. Distribution Inventory

Current public software distribution state, based on committed phase evidence:

| Surface | Current state | Evidence |
|---|---|---|
| PyPI package | `ilc-core 0.2.0` wheel and sdist uploaded in Phase 1575o-release | `docs/phases/phase_1575o_release_pypi_yank_upload_walkthrough.md` |
| Committed source package metadata | `pyproject.toml` now declares `name = "ilc-core"` and `version = "0.2.0"` | `pyproject.toml` |
| Compiled binary distribution | Not present | No binary release artifact is committed for this lane |
| Root ILC `install.sh` software-delivery script | Not present in `tools/install.sh` or `ilc_core/cli/install.sh` | GAP-PUBLIC-INSTALL-02 scope |
| Sidecar-local install script | `ilc-graphics-sidecar/install.sh` exists, but installs only the graph-viz sidecar into an existing repo venv | Not the public ILC software-delivery installer |
| Graph onboarding command | `ilc install --from-invite` exists and rejects `http://` and `https://` sources | `ilc_core/cli/main.py` |

The current install baseline is therefore: PyPI wheel/sdist exists for
`ilc-core 0.2.0`; no root public install script, binary downloader, or update
command exists yet.

## 2. Package Name Fact

The public Python package name is `ilc-core`.

The plain `ilc` package name is blocked for this account. Phase 1575o recorded
that PyPI Warehouse rejected the plain `ilc` name with:

```text
400 Bad Request: The name 'ilc' is too similar to an existing project.
```

This package-name fact does not affect the console script name: the installed
package exposes the `ilc` command through `pyproject.toml`.

## 3. Version State

`pyproject.toml` was corrected in this phase from `0.1.0` to `0.2.0` so source
installs match the already uploaded `ilc-core 0.2.0` package evidence.

Phase 1575o-Fix1 build artifacts:

| Artifact | Size bytes | SHA-256 |
|---|---:|---|
| `/tmp/ilc-core-020-dist-fix1/ilc_core-0.2.0-py3-none-any.whl` | `1000828` | `80e53ea18aea0a7c474400a41e20f346c00ee3e36e8f0dd60f233cca2b0e2f1d` |
| `/tmp/ilc-core-020-dist-fix1/ilc_core-0.2.0.tar.gz` | `783493` | `95c73d42799d3a662b14c4b81da8781df861c222f1e04c458dd1b4ac318e2ab4` |

Phase 1575o-release recorded the PyPI version-specific endpoint result for
`ilc-core 0.2.0` and the token
`pypi_ilc_core_020_clean_wheel_uploaded_phase_1575o`. GAP-PUBLIC-INSTALL-00 did
not perform network revalidation and did not upload, yank, or modify PyPI state.

`ilc_core/__init__.py` declares no `__version__` constant at this phase, so there
is no in-package version string to reconcile.

## 4. Two-Layer Separation

ILC install language is split into two non-overlapping layers:

| Layer | Command or future artifact | Responsibility | Must not do |
|---|---|---|---|
| Software delivery | Future root `install.sh` from GAP-PUBLIC-INSTALL-02 | Download a wheel or binary, verify its hash/signature, install it, and place `ilc` on PATH | Graph hydration, invite redemption, LMDB graph writes, settlement, wallet writes |
| Graph onboarding | Existing `ilc install --from-invite <path>` | Read a local invite bundle, verify invite/bootstrap evidence, verify local manifest witness, and materialize local graph slice files | Download software, fetch remote invite URLs, install packages, mutate PyPI or release state |

`install.sh` is not `ilc install`. `ilc install --from-invite` is not a software
installer. Successor phases must preserve this boundary in CLI names, docs,
tests, and non-claims.

## 5. Platform Priority

GAP-PUBLIC-INSTALL-01 through -05 should target platforms in this order:

1. `linux-amd64`
2. `linux-arm64`
3. `darwin-arm64`
4. `darwin-amd64`
5. Windows follow-on after Unix-like installer semantics are proven

The current `ilc-core 0.2.0` artifact is a Python wheel/sdist, not a per-platform
compiled binary. Platform-specific release records become necessary when a
binary installer or bundled Rust artifacts are introduced.

## 6. Release Manifest Gap Inventory

Phase 1213 required fields:

| Field | Present in 1213 schema | Installable-manifest disposition |
|---|---|---|
| `artifact_id` | Yes | Retain |
| `artifact_type` | Yes | Retain, but extend allowed values |
| `canonical_hash` | Yes | Retain |
| `lineage_reference` | Yes | Retain |
| `produced_phase` | Yes | Retain |
| `ratification_token` | Yes | Retain |
| `signing_status` | Yes | Retain |

Phase 1213 allowed artifact types:

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

Installable manifest fields missing from 1213:

| Field | Required by GAP-PUBLIC-INSTALL-01 | Reason |
|---|---|---|
| `platform` | Yes | Distinguish `linux`, `darwin`, and future Windows artifacts |
| `arch` | Yes | Distinguish `amd64`, `arm64`, and follow-on architectures |
| `channel` | Yes | Support `stable`, `rc`, and `dev` selection |
| `size_bytes` | Yes | Bound downloads and verify expected artifact length |
| `download_url` | Yes | Provide software-delivery location for installers |
| `min_python_version` | Yes for wheel path | Preserve `requires-python = ">=3.10"` install constraint |

Allowed artifact-type gaps:

| Artifact type | Present in 1213 | Needed for installable manifest |
|---|---|---|
| `python_wheel` | No | Yes |
| `python_sdist` | No | Yes if sdist remains part of distribution |
| `install_script` | No | Yes for root software-delivery script |
| `cli_binary` | Yes | Retain for future binary artifacts |

GAP-PUBLIC-INSTALL-01 should extend or wrap the 1213 schema rather than silently
overloading `source_release_tarball` or `cli_binary` for wheel/script records.

## 7. Existing Release Manifest Lineage Summary

| Phase | Artifact | Role |
|---|---|---|
| 1213 | `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md` | Minimum release artifact manifest schema; no public distribution authorization |
| 1320 | `docs/specs/ilc_release_artifact_manifest_instance_rehearsal_1320_v0.1.md` and `.json` | Dry-run rehearsal around 1213; produced no artifacts |
| 1334 | `docs/specs/ilc_release_artifact_production_gate_1334_v0.1.json` | Produced one unsigned `source_release_tarball` candidate and validated the 1213 shape |
| 1447 | `docs/specs/ilc_release_artifact_signing_manifest_1447_v0.1.md` | Bound release artifact classes to the Phase 1446 root envelope; launch-readiness manifest signature remained null |
| 1575c-Fix3 | `release_artifacts/genesis_v05/manifest.json` | Private release-publication manifest for signed Genesis v0.5 JSON packages |
| 1575o-Fix1 / 1575o-release | Phase walkthroughs and receipts | Built, scanned, uploaded, and recorded `ilc-core 0.2.0` wheel/sdist evidence |

`release_artifacts/genesis_v05/manifest.json` contains portable signed JSON
package files and verification companions. It is not a wheel/binary installer
manifest and does not contain `platform`, `arch`, `channel`, `download_url`, or
`min_python_version`.

## 8. Console Script Inventory

`pyproject.toml` currently declares nine console scripts:

```text
ilc
ilc-canon-verify
ilc-canon-summary
ilc-canon-export
ilc-canon-bundle-validate
ilc-canon-bundle-sign
ilc-canon-bundle-pipeline
ilc-canon-bundle-replay
ilc-canon-cluster-a-replay-proof
```

These match the Phase 1575o-Fix1 clean-wheel walkthrough script inventory.

## 9. Non-Claims

| Non-claim | Status |
|---|---|
| PyPI upload or re-upload | Not performed |
| PyPI yank | Not performed |
| Root `install.sh` implementation | Not performed |
| `ilc update` implementation | Not performed |
| Binary build or cross-compilation | Not performed |
| Graph onboarding runtime change | Not performed |
| Network I/O | Not performed |
| CDL mutation | Not performed |
| Guard clearance | Not performed |
| Public mirror push | Not performed |
| Public RC activation | Not performed |
| Mainnet activation | Not performed |
| Epoch transition | Not performed |
| ECU minting or transfer | Not performed |
| ILC minting or settlement | Not performed |
| Wallet write | Not performed |

## 10. Mirror Disposition

`pyproject.toml` is included in the public mirror under existing policy. The
version correction aligns committed source metadata with the previously recorded
`ilc-core 0.2.0` PyPI evidence. No public mirror push occurs in this phase.

```text
mirror_disposition=not_stale_version_correction_only
```
