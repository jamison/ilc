# ILC Layered Licensing and Rights Posture

Status: current project posture, subject to explicit project amendment

```text
ilc_layered_license_posture_v0.1
mit_for_all_zones_rejected_layered_license_posture
agpl_default_runtime_license_posture
genesis_canonical_identity_license_zone
public_docs_cc_by_4_0_zone
patent_pending_all_rights_reserved_zone
trademark_identity_not_granted_by_code_license
self_counsel_governance_review_future_modification_expected
```

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
| Runtime/source code | `ilc_core/`, runtime helpers, validators, gossip, package verification, sidecars, CLIs, tests unless otherwise marked | AGPL-3.0-only during bootstrap | Intended to preserve network-service reciprocity and reduce proprietary/SaaS capture risk during bootstrap. |
| Core protocol interfaces and schemas | Public verification formats, protocol schemas, harness interfaces | AGPL-3.0-only by repository default unless a later file-level notice grants a permissive interface license | Future counsel/governance may split these into Apache-2.0/MIT-compatible terms for interoperability. No such split is granted by default today. |
| Genesis canonical artifacts | Genesis root/envelope specs, authority-map specs, canonical lineage receipts, release-key binding records, CDL ratification evidence, public canonical manifests | Strict canonical-identity terms | Unmodified redistribution is permitted for verification and archival use. Modified versions must be clearly marked as forked/non-canonical and must not claim canonical ILC status. |
| Explanatory public documentation | Whitepapers, public summaries, non-operational research explainers | CC BY 4.0 style attribution terms, unless the document is load-bearing for canonical identity or marked otherwise | Documentation that supports canonical lineage or release identity stays in the stricter canonical-identity zone by default. |
| Patent-sensitive research | `docs/research/patent_pending/`, internal patent drafts, invention-disclosure notes, unpublished filing packets | All Rights Reserved - Patent Pending | No use, copy, modification, distribution, sublicense, or public disclosure is granted unless a later explicit written permission or project policy says otherwise. |
| Official registry, transparency log, hosted canonical services | Release registry, canonical explorer, hosted verifier endpoints, transparency services | Controlled service terms | Service availability, API use, and hosted canonical status are not granted by the code license. |
| Name, logos, official network identity marks | `ILC`, official network names, logos, canonical release identity | Trademark/canonical-identity policy; no grant by code license | Forks may not imply canonical ILC status, Genesis lineage, official release status, or network identity without valid lineage proofs and authorization. |
| Internal-only, private, or public-RC-excluded material | Files marked `PUBLIC_RC_EXCLUDE`, private planning, raw chats, local monitoring outputs, unpublished sensitive docs | No public release grant by default | Public-RC export requires explicit allowlist review and marker discipline. |

## 3. Runtime Package Metadata

The `ilc-core` package metadata declares `AGPL-3.0-only` because the Python
package is a runtime/source-code package. That metadata does not grant rights to
Genesis canonical artifacts, patent-sensitive research, trademarks, hosted
services, or public-release claims.

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
or `PUBLIC_RC_EXCLUDE` for IP/publication reasons, no public license is granted
for that material unless a later explicit permission says otherwise.

The active internal IP/publication planning lane is `IP-001` through `IP-006`.
Those lanes are internal by default and do not themselves authorize filing,
publication, preprint release, source export, or public repository publication.

## 6. Contributor and Relicensing Posture

The project expects a future contributor agreement or equivalent inbound-rights
mechanism before accepting external contributions, because staged relicensing or
license sunset may be required after network maturity.

Until that policy exists, external contributor intake is not authorized by this
file.

## 7. Self-Counsel and Governance Review

This file implements the current project posture so the repository no longer
appears to be blanket MIT. Future Genesis governance review may modify:

- exact SPDX expressions;
- per-file or per-directory license notices;
- contributor agreement text;
- trademark/canonical identity policy;
- patent-zone licensing after filing or grant;
- eventual license sunset or dual-license mechanics.

Such later review may amend this file, but it does not change the current need
to avoid blanket MIT exposure.

## 8. Phase 1388a CDL-048 Pre-Production Activation Scope

Phase 1388a records a Genesis-authority self-counsel decision for the narrow
CDL-048 pre-production/testnet activation surface:

```text
counsel_clearance_cdl_048_activation_phase_1388a
self_counsel_decision_not_external_legal_opinion_phase_1388a
```

That decision is final for the project's internal CDL-048 conversion-path
plumbing activation purposes in the current closed-network/testnet context. It
is not an external legal opinion and does not by itself authorize public
claimability, public repository publication, external contributor onboarding,
mainnet launch, or public token distribution/offering/listing surfaces.
