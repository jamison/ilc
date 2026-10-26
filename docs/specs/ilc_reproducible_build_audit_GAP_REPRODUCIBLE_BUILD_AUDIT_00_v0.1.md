# ILC Reproducible Build Audit

**Phase:** GAP-REPRODUCIBLE-BUILD-AUDIT-00  
**Version:** v0.1  
**Date:** 2026-10-14  
**Status:** Complete, characterization only  
**Sensitivity:** NON-SENSITIVE  
**Output token:** `reproducible_build_audit_complete_GAP_REPRODUCIBLE_BUILD_AUDIT_00`

## Purpose

This audit characterizes whether current ILC release artifacts can be
reproduced byte-for-byte from the same source commit and toolchain. It does not
change the build system. It does not claim independent reproduction by a second
operator. It records what is already deterministic, what becomes deterministic
with pinning, and what still needs a later attestation phase.

Non-claims summary: this audit does not implement reproducible builds, publish
artifacts, mutate release authority, or activate any transport/economic surface.

## Canon Read Summary

- `pyproject.toml` uses `setuptools.build_meta` with build requirements
  `setuptools>=61.0` and `wheel`; there is no `maturin` backend.
- The public release workflow publishes a Python wheel and Python sdist, records
  SHA-256 and size, signs release-envelope preimages, performs PyPI fetchback,
  and later updates installer and ClawHub surfaces.
- `ArtifactNode.sha256` binds exact artifact bytes. `ArtifactNode.cid` binds the
  artifact metadata record. Optional `ArtifactNode.blake3` is already in the
  schema, but no current runtime/package dependency provides BLAKE3.
- `ilc_consensus/Cargo.toml` defines Rust library and binary artifacts including
  `ilc_native_submit_receiver_full`, `ilc_native_submit_client`, and
  `attribution_batch_ingest`; `ilc_consensus/Cargo.lock` exists and pins crate
  versions/checksums.

## Per-Component Verdicts

| Component | Empirical result | Phase verdict | Required pinning or remediation |
|---|---|---|---|
| Python wheel `ilc_core-0.4.33-py3-none-any.whl` | Two default isolated builds differed. With `SOURCE_DATE_EPOCH=0`, two isolated builds were byte-identical. | `reproducible_with_pinning` | Pin Python, setuptools, wheel, and build frontend versions; set `SOURCE_DATE_EPOCH`; build from the exact source commit with a clean tree. |
| Python sdist `ilc_core-0.4.33.tar.gz` | Two default isolated builds differed. With `SOURCE_DATE_EPOCH=0`, the sdist still differed. File contents matched, but generated tar member mtimes differed. | `not_reproducible` | Add or adopt an sdist path that normalizes generated tar member mtimes and gzip metadata, then re-test in `GAP-REPRODUCIBLE-BUILD-ATTESTATION-00`. |
| Rust library `libilc_consensus.rlib` | Empirical build comparison was not possible in this environment because `rustc` is not installed. | `not_reproducible` for current release-claim purposes | Install and pin Rust toolchain, target triple, linker, build flags, path remapping, and Cargo profile; then run a two-target-dir comparison. |
| Rust binary `ilc_native_submit_receiver_full` | Empirical build comparison was not possible in this environment because `rustc` is not installed. | `not_reproducible` for current release-claim purposes | Same Rust pins as above, plus binary-specific checks for host path, debug info, linker, and platform metadata. |
| Rust binary `ilc_native_submit_client` | Empirical build comparison was not possible in this environment because `rustc` is not installed. | `not_reproducible` for current release-claim purposes | Same Rust pins as above. |
| Rust binary `attribution_batch_ingest` | Empirical build comparison was not possible in this environment because `rustc` is not installed. | `not_reproducible` for current release-claim purposes | Same Rust pins as above. |

The Rust verdict is conservative: it means current evidence is insufficient to
claim reproducibility, not that Rust binaries are mathematically impossible to
make reproducible.

## Python Build Evidence

Default isolated double-build:

```text
base=/private/tmp/ilc_repro_audit_24_iso_1791967777
[python1]
ilc_core-0.4.33-py3-none-any.whl 1606960 09592e7cf7be6a7b540c241bdec82dba13d621adab17c2d926b8f57804cd73e0
ilc_core-0.4.33.tar.gz 1317081 7a79f1943b0042457aed639d47dc2452d7e0c451b399a7702f4356b3e600fc53
[python2]
ilc_core-0.4.33-py3-none-any.whl 1606960 13b0e9c4824f5ed4a3345249f2bc3faa93ed9c5715754581ae9d4bc82487dcea
ilc_core-0.4.33.tar.gz 1317076 40eb2966db09364ff1b5275533bde155d15c9d28acd53c5a21a56a504903065c
[compare]
ilc_core-0.4.33-py3-none-any.whl identical=False sha1=09592e7cf7be6a7b540c241bdec82dba13d621adab17c2d926b8f57804cd73e0 sha2=13b0e9c4824f5ed4a3345249f2bc3faa93ed9c5715754581ae9d4bc82487dcea
ilc_core-0.4.33.tar.gz identical=False sha1=7a79f1943b0042457aed639d47dc2452d7e0c451b399a7702f4356b3e600fc53 sha2=40eb2966db09364ff1b5275533bde155d15c9d28acd53c5a21a56a504903065c
```

Manual inspection showed wheel file contents were equal and only `.dist-info`
ZIP timestamps differed:

```text
ilc_core-0.4.33.dist-info/METADATA content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 20)
ilc_core-0.4.33.dist-info/RECORD content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 22)
ilc_core-0.4.33.dist-info/WHEEL content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 20)
ilc_core-0.4.33.dist-info/entry_points.txt content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 20)
ilc_core-0.4.33.dist-info/licenses/LICENSE content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 20)
ilc_core-0.4.33.dist-info/top_level.txt content_equal=True time1=(2026, 10, 14, 8, 50, 2) time2=(2026, 10, 14, 8, 50, 20)
diff_count 6
```

With `SOURCE_DATE_EPOCH=0`:

```text
base=/private/tmp/ilc_repro_audit_24_sde_1791967855
[python1]
ilc_core-0.4.33-py3-none-any.whl 1606960 5eb9c13384d4376cac91dc045028807419555902893e8c6cdb520b65b3c96e97
ilc_core-0.4.33.tar.gz 1317093 7406f3d1fc2fb26625d99140eb80265763b608e30dce45e4eb750b3dbab90b32
[python2]
ilc_core-0.4.33-py3-none-any.whl 1606960 5eb9c13384d4376cac91dc045028807419555902893e8c6cdb520b65b3c96e97
ilc_core-0.4.33.tar.gz 1317086 368ea2ee02af61fa38fac3d8f46b3ac28080a22034aaa2d7407b0648c94c96ec
[compare]
ilc_core-0.4.33-py3-none-any.whl identical=True sha1=5eb9c13384d4376cac91dc045028807419555902893e8c6cdb520b65b3c96e97 sha2=5eb9c13384d4376cac91dc045028807419555902893e8c6cdb520b65b3c96e97
ilc_core-0.4.33.tar.gz identical=False sha1=7406f3d1fc2fb26625d99140eb80265763b608e30dce45e4eb750b3dbab90b32 sha2=368ea2ee02af61fa38fac3d8f46b3ac28080a22034aaa2d7407b0648c94c96ec
```

The `SOURCE_DATE_EPOCH=0` sdist still differed because generated tar member
mtimes differed even when member contents matched:

```text
ilc_core-0.4.33 content_equal=True size1=0 size2=0 mtime1=1791967864.3536294 mtime2=1791967883.317344 mode1=493 mode2=493
ilc_core-0.4.33/PKG-INFO content_equal=True size1=17753 size2=17753 mtime1=1791967864.3526793 mtime2=1791967883.3133469 mode1=420 mode2=420
ilc_core-0.4.33/ilc_core content_equal=True size1=0 size2=0 mtime1=1791967863.5222166 mtime2=1791967882.8517025 mode1=493 mode2=493
ilc_core-0.4.33/ilc_core.egg-info content_equal=True size1=0 size2=0 mtime1=1791967863.5453656 mtime2=1791967882.8570566 mode1=493 mode2=493
diff_count 52
```

## Rust Build Evidence

The Rust comparison command could not run because the audit environment lacks
`rustc`:

```text
zsh:6: command not found: rustc
```

Carry-forward token:
`reproducible_build_empirical_validation_deferred_to_GAP_REPRODUCIBLE_BUILD_ATTESTATION_00`.

The current Rust source is nevertheless suitable for a later reproducibility
test plan because `ilc_consensus/Cargo.lock` is present. The later phase must
pin at least:

- Rust toolchain version and target triple;
- Cargo version and locked dependency graph;
- linker and platform;
- build profile and feature set;
- path remapping, for example `--remap-path-prefix`, if debug/path material is
  included;
- binary list and expected artifact names.

## BLAKE3 Feasibility

`ArtifactNode.blake3` is already an optional schema field, so BLAKE3 is feasible
as a future additional byte digest alongside SHA-256. It is not active in the
current package profile: `pyproject.toml` has no `blake3` dependency and the
current release verification path uses SHA-256 plus metadata CIDv1. Adding
BLAKE3 should be a follow-on release-object extension, not an implicit change to
Row 23 `ilc upgrade apply`.

## Follow-On Requirements

`GAP-REPRODUCIBLE-BUILD-ATTESTATION-00` should:

1. Pin Python, build frontend, setuptools, wheel, and `SOURCE_DATE_EPOCH`.
2. Add or select an sdist creation path that normalizes generated tar and gzip
   metadata.
3. Install a pinned Rust toolchain and run two independent target-dir builds for
   the Rust library and each release binary.
4. Produce signed or hashed reproduction attestations that bind source commit,
   build recipe, toolchain manifest, artifact hash, and reproducer identity.
5. Keep attestation separate from release authority: reproduction evidence may
   support trust, but it must not silently authorize package publication,
   validator activation, settlement, minting, or public-RC claims.

## Non-claims

This phase does not implement reproducible builds. It does not publish a
package, update PyPI, update ClawHub, push a public mirror, alter `ilc_core/`,
alter `ilc_consensus/`, open or ratify a CDL, activate release-object transport,
activate Werner credit, mutate VPS state, create wallet authority, activate
settlement, mint ILC, or claim mainnet/public-RC activation.
