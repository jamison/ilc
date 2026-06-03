# ILC Third-Party Notices

Copyright (c) 2026 ILC contributors.

This repository contains ILC-authored source code plus third-party dependencies
and reference technologies. The ILC default runtime/source license is
`AGPL-3.0-only`, but third-party packages, vendored code, copied code, and
referenced upstream implementations remain under their own licenses.

```text
third_party_notice_recorded_public_rc_2026_06_03
third_party_original_licenses_preserved_public_rc_2026_06_03
mysticeti_reference_not_vendored_public_rc_2026_06_03
lmdb_dependency_notice_recorded_public_rc_2026_06_03
```

## Policy

The ILC license does not relicense third-party code. If a third-party package is
installed, bundled, copied, adapted, or vendored, its original copyright notice,
license text, and attribution requirements must be preserved in the applicable
source tree, binary distribution, container image, package, or release artifact.

The public ILC patent notice applies only to ILC-controlled patent rights. It
does not grant patent rights owned by third-party dependency authors or upstream
projects.

## Current Direct Package Dependencies

The current Python package metadata declares these direct dependencies:

```text
fastapi
uvicorn
pydantic
requests
httpx
numpy
cbor2
cryptography
grpcio
protobuf
PyNaCl
jsonschema
lmdb
```

The current Rust consensus crate declares these direct dependencies:

```text
blst
lmdb-rkv
quinn
tokio
prost
tonic
tonic-prost
serde
serde_json
sha2
thiserror
bincode
getrandom
rustls
fips204
fips205
bip39
rand_core
secret-sharing-rs
tempfile
rcgen
protox
tonic-prost-build
```

Package-manager metadata and shipped package license files control the exact
license terms for each dependency version. Public RC packaging must preserve the
license material provided by each installed dependency.

## LMDB

ILC currently uses LMDB through:

- Python package dependency `lmdb>=2.2.0`.
- Rust crate dependency `lmdb-rkv = 0.14`, which wraps LMDB for the Rust
  consensus crate.

LMDB is a third-party embedded database technology. ILC-authored LMDB adapters,
storage schemas, graph persistence logic, consensus use, and runtime controls
are ILC code under the applicable ILC license. The underlying LMDB project and
bindings remain under their upstream licenses, including OpenLDAP Public
License terms for LMDB and the package/crate license terms for the bindings.

## Mysticeti

ILC references and builds a sovereign consensus substrate inspired by Mysticeti.
The current repo does not vendor `mysticeti-core`; `ilc_consensus/Cargo.toml`
contains only a future-path comment for adding such a path dependency when an
extraction payload is prepared.

If Mysticeti code is ever copied, adapted, or vendored into the public ILC
source tree, the public package must preserve the applicable upstream notices.
The current public Mysticeti repository is Apache-2.0 licensed.

## Public RC Packaging Rule

Before public package publication, run a dependency-license notice pass over the
materialized public tree and generated dependency artifacts. The pass must check
that:

- `LICENSE`, `LICENSING.md`, `PATENTS.md`, and `THIRD_PARTY_NOTICES.md` ship in
  the public source package;
- direct Python and Rust dependency license metadata is retained;
- vendored or copied third-party source carries its original notice;
- no public wording implies that ILC owns, relicenses, or grants patent rights
  for third-party technologies.
