# ILC Layered Licensing and Rights Posture

Status: current project posture, subject to explicit project amendment

## 1. Purpose

ILC uses a layered license posture because the repository contains different
classes of material: runtime code, protocol interfaces, Genesis/canonical
identity artifacts, explanatory documentation, patent-sensitive research, and
network identity marks.

A blanket MIT license is not the current project posture. The root `LICENSE`
file is a layered notice, and this file is the repository zone table.

This is a Genesis-authority self-counsel governance posture, not external legal
advice. The current repository should not continue to present itself as blanket
MIT.

## 2. Zone Table

| Zone | Examples | Current posture | Notes |
|------|----------|-----------------|-------|
| Runtime/source code | `ilc_core/`, `ilc_consensus/`, runtime helpers, validators, gossip, package verification, sidecars, CLIs, tests unless otherwise marked | AGPL-3.0-only during bootstrap | Intended to preserve network-service reciprocity and reduce proprietary/SaaS capture risk during bootstrap. |
| Core protocol interfaces and schemas | Public verification formats, protocol schemas, harness interfaces | AGPL-3.0-only by repository default unless a later file-level notice grants a permissive interface license | Future counsel/governance may split these into Apache-2.0/MIT-compatible terms for interoperability. No such split is granted by default today. |
| Genesis canonical artifacts | Genesis root/envelope specs, authority-map specs, canonical lineage receipts, release-key binding records, CDL ratification evidence, public canonical manifests | Strict canonical-identity terms | Unmodified redistribution is permitted for verification and archival use. Modified versions must be clearly marked as forked/non-canonical and must not claim canonical ILC status. |
| Explanatory public documentation | Whitepapers, public summaries, non-operational research explainers | CC BY 4.0 style attribution terms, unless the document is load-bearing for canonical identity or marked otherwise | Documentation that supports canonical lineage or release identity stays in the stricter canonical-identity zone by default. |
| Patent-sensitive research | `docs/research/patent_pending/`, internal patent drafts, invention-disclosure notes, unpublished filing packets | All Rights Reserved - Patent Pending | No use, copy, modification, distribution, sublicense, or public disclosure is granted unless a later explicit written permission or project policy says otherwise. |
| Third-party dependencies and vendored/copied upstream code | Python dependencies, Rust crates, LMDB bindings, any future copied or vendored upstream source | Original upstream license controls for that third-party material | The ILC license does not relicense third-party code. Preserve upstream notices and license files in public source packages, binary bundles, containers, and other release artifacts. |
| Official registry, transparency log, hosted canonical services | Release registry, canonical explorer, hosted verifier endpoints, transparency services | Controlled service terms | Service availability, API use, and hosted canonical status are not granted by the code license. |
| Name, logos, official network identity marks | `ILC`, official network names, logos, canonical release identity | Trademark/canonical-identity policy; no grant by code license | Forks may not imply canonical ILC status, Genesis lineage, official release status, or network identity without valid lineage proofs and authorization. |
| Internal-only, private, or public-RC-excluded material | Files carrying internal exclusion markers, private planning, raw chats, local monitoring outputs, unpublished sensitive docs | No public release grant by default | Public-RC export requires explicit allowlist review and marker discipline. |

## 3. Runtime Package Metadata

The `ilc-core` package metadata declares `AGPL-3.0-only` because the Python
package is a runtime/source-code package. That metadata does not grant rights to
Genesis canonical artifacts, patent-sensitive research, trademarks, hosted
services, or public-release claims.

The `ilc_consensus` Rust crate also declares `AGPL-3.0-only` unless a later
explicit governance decision splits a narrower interoperability component under
a different license.

## 4. Genesis Canonical Identity Terms

Genesis and canonical-lineage materials may be copied and redistributed
unmodified for verification, archival, audit, and interoperability purposes.

If any Genesis/canonical artifact is modified, the modified artifact must:

- identify itself as modified, forked, or non-canonical;
- not claim to be canonical ILC unless later re-authorized by the ILC governance
  process;
- not use ILC official network identity, release identity, marks, or lineage
  claims in a misleading way.

This protects the "fork the code, not the graph" invariant: code may be reused
under its applicable license, but canonical ILC identity requires valid Genesis
lineage.

## 5. Patent-Sensitive Material

Patent-sensitive material is not covered by the AGPL default or by the
documentation zone. If material is marked patent pending, internal IP planning,
or private/internal for IP/publication reasons, no public license is granted for
that material unless a later explicit permission says otherwise.

Public runtime/source-code material may practice pending or intended patent
claims. The public open-source implementation is licensed under AGPL-3.0-only,
including any patent rights expressly granted by that license for the licensed
contributor version. That public grant is not a blanket patent license for
proprietary, closed-source, non-AGPL, certified, hosted, indemnified, or
otherwise broader implementations.

The public patent notice is `PATENTS.md`. The internal decision record is:

`docs/specs/ilc_public_rc_dual_license_patent_posture_decision_2026_06_03.md`

Commercial licensing is expected to be available for uses beyond the public
open-source grant, including proprietary or non-AGPL implementations, private
integrations, sublicensing, indemnity, certification, official deployment
support, and hosted-service arrangements.

The active internal IP/publication planning lane is `IP-001` through `IP-006`.
Those lanes are internal by default and do not themselves authorize filing,
publication, preprint release, source export, or public repository publication.

## 5a. Third-Party Dependencies

Third-party dependencies are not relicensed by the ILC root license. The public
third-party notice is `THIRD_PARTY_NOTICES.md`.

Permissively licensed dependencies may be used in the AGPL-licensed ILC package
when their original notices are preserved. This includes the current LMDB
dependency path (`lmdb` for Python and `lmdb-rkv` for Rust). If vendor source
or any other third-party code is copied or vendored later, public RC packaging
must preserve the upstream license notice before shipping.

## 6. Contributor and Relicensing Posture

The project expects a future contributor agreement or equivalent inbound-rights
mechanism before accepting external contributions, because staged relicensing or
license sunset may be required after network maturity.

Until that policy exists, external contributor intake is not authorized by this
file.

## 6a. Dual-License Public RC Posture

The current public-RC posture is:

```text
full_public_agpl_package_plus_commercial_alternative_license_for_proprietary_or_non_agpl_use
dual_license_decision_recorded_public_rc_2026_06_03
```

This means patent-practicing runtime modules may ship in the public AGPL package
as an adoption-oriented implementation, while the project preserves separate
commercial licensing for proprietary or non-AGPL use. This posture avoids
blocking public adoption while keeping a commercial path for organizations that
cannot or do not want to operate under AGPL obligations.

## 7. Genesis Counsel and Governance Review

This file implements the current project posture. Future Genesis governance review may modify:

- exact SPDX expressions;
- per-file or per-directory license notices;
- contributor agreement text;
- trademark/canonical identity policy;
- patent-zone licensing after filing or grant;
- eventual license sunset or dual-license mechanics.

Such later review may amend this file.

## 8. Phase 1388a CDL-048 Pre-Production Activation Scope

Phase 1388a records a Genesis-authority decision for the narrow
CDL-048 pre-production/testnet activation surface.

That decision is final for the project's internal CDL-048 conversion-path
plumbing activation purposes in the current closed-network/testnet context. It
does not necessarily constitute a legal opinion and does not by itself authorize
public claimability, public repository publication, external contributor onboarding, mainnet launch, or public token distribution/offering/listing surfaces.
