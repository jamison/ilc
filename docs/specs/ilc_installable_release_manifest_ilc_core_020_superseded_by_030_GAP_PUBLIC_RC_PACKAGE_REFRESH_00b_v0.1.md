# ilc-core 0.2.0 Installable Manifest Supersession Note

**Phase:** GAP-PUBLIC-RC-PACKAGE-REFRESH-00b
**Date:** 2026-08-20
**Status:** superseded_by_0.3.0_manifest

## Superseded Artifact

The historical installable manifest remains schema-valid and unmodified:

- `docs/specs/ilc_installable_release_manifest_ilc_core_020_GAP_PUBLIC_INSTALL_01_v0.1.json`
- Release ID: `ilc-core-0.2.0`

## Active Replacement

The active public-RC installable manifest produced by this phase is:

- `docs/specs/ilc_installable_release_manifest_ilc_core_030_GAP_PUBLIC_RC_PACKAGE_REFRESH_00_v0.1.json`
- Release ID: `ilc-core-0.3.0`
- Wheel URL: `https://files.pythonhosted.org/packages/da/a0/313f2a4666f9ed4c8062d66201b8a2fe6fea4fea3c64a6c749d4b10046a7/ilc_core-0.3.0-py3-none-any.whl`
- Wheel SHA-256: `752f83e46736a8089e7d8095f140cd16802dbb78dd63ebb32c3279a62094b99c`
- Wheel size: `1382583` bytes
- Sdist URL: `https://files.pythonhosted.org/packages/0f/d3/32d2911446dfcc29cadc44f51ef599d0387728877125414cd0cf0dad05f0/ilc_core-0.3.0.tar.gz`
- Sdist SHA-256: `44c4e00d8c08f752752900f7f1df24f0c9995dadf90651dc9c9d95ccb3448ffb`
- Sdist size: `1108814` bytes

## Upload Receipt

The upload and fetchback evidence is recorded in:

- `docs/specs/ilc_pypi_upload_receipt_GAP_PUBLIC_RC_PACKAGE_REFRESH_00b_v0.1.json`

## Reason For Supersession

Part 3d issuance atomicity hardening changed load-bearing public-RC runtime behavior.
The public install path therefore moves from `ilc-core==0.2.0` to `ilc-core==0.3.0`
so package versioning reflects the new settlement and conservation capability.

## Non-Claims

- No release signature was produced in this phase.
- No CDL mutation was performed in this phase.
- No validator state was changed in this phase.
- No public RC launch, public mirror push, or epoch transition was performed in this phase.
