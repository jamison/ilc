# ILC Copyright Counsel Disposition - Phase 1420

**Status:** Genesis-authority self-counsel disposition for ADR-0041 Section 5
**Phase:** 1420
**Date:** 2026-05-21
**Scope:** Public-RC interim copyright/publication boundary for external
artifact ingestion

```text
copyright_counsel_disposition_complete_phase_1420
self_counsel_verbatim_storage_boundary_phase_1420
self_counsel_d2d_distribution_boundary_phase_1420
copyright_counsel_not_external_legal_opinion_phase_1420
license_not_public_before_repo_authorized_public_phase_1420
```

## Authority And Status

This artifact is a Genesis-authority self-counsel decision for ILC project
planning. It is not an external legal opinion, not attorney sign-off,
not commercial legal advice, and not a jurisdiction-specific copyright opinion.

It resolves the J-008 `COPYRIGHT_COUNSEL_DISPOSITION` evidence obligation for
the conservative public-RC interim scope only. It does not patch
`ilc_core/epistemic/jury_activation_gate.py`; Phase 1425 remains responsible for
gate-source verification and any static gate patch after all blocking tracks are
re-verified.

## Claim Verification

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| ADR-0041 Section 5 records the copyright boundary token | `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` | confirmed: `verbatim_distribution_via_d2d_requires_counsel_review_before_public_activation` |
| J-008 gate source still reports `COPYRIGHT_COUNSEL_DISPOSITION` as `NOT_MET` | `ilc_core/epistemic/jury_activation_gate.py` | confirmed |
| Prior ILC counsel artifacts use self-counsel language and reject external-opinion claims | `docs/specs/ilc_counsel_clearance_1388_v0.1.md`, `docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md`, `docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md`, `docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md` | confirmed |
| No earlier Phase 1420 copyright counsel disposition artifact exists | `docs/specs/` search | confirmed |

## Disposition

### 1. Verbatim Full-Text Storage

Public-RC ingestion must not store verbatim full-text bytes of third-party
copyrighted artifacts by default.

The authorized interim path for external artifacts is:

- cryptographic hash;
- public bibliographic or source metadata where permitted;
- extracted claims;
- source spans or source references sufficient for audit;
- license or rights-status metadata when available.

Verbatim full-text storage is allowed only when one of these conditions is
documented before storage:

- the project owns the relevant rights;
- the artifact is public domain;
- the artifact carries an explicit license authorizing the storage use;
- the artifact is open-access under terms compatible with the storage use;
- a later external legal review or jurisdiction-specific statutory exception
  clears the use.

Absent one of those documented conditions, verbatim storage remains
deferred to a separately counsel-cleared path.

```text
self_counsel_verbatim_storage_boundary_phase_1420
```

### 2. D2D Distribution And Serve-Credit

This disposition does not authorize verbatim D2D distribution of copyrighted
material.

For public-RC scope, D2D serve-credit may cover:

- content-addressed hashes;
- metadata records;
- extracted claim records;
- source-span records;
- project-owned bytes;
- public-domain bytes;
- bytes with explicit compatible license or open-access authorization.

Verbatim third-party copyrighted bytes must not be distributed to other network
agents through D2D serve-credit unless the byte distribution path is
separately cleared by license evidence, public-domain status, compatible open-access terms,
or later external legal review.

```text
self_counsel_d2d_distribution_boundary_phase_1420
```

### 3. Fair-Use, Fair-Dealing, Research, And TDM Exceptions

The project records no blanket fair-use, fair-dealing, research-exemption, or
text-and-data-mining authorization for public-RC verbatim storage or D2D
distribution.

Official references confirm the conservative posture:

- The U.S. Copyright Office describes fair use as fact-specific and not a
  substitute for legal advice.
- European Commission guidance describes text-and-data-mining exceptions as
  conditional and recognizes rights reservations or opt-outs under the DSM
  Copyright Directive.

Therefore, public-RC ingestion must not rely on a generic fair-use, research, or
TDM assumption to store or distribute full copyrighted artifacts. The public-RC
allowed path remains hash, metadata, extracted claims, and source spans unless
rights evidence clears the broader use.

External legal review remains a post-public-RC or pre-public-verbatim
distribution requirement if the project later wants a broader jurisdictional
position.

## License And Publication Boundary

The license must not go public before the repository is authorized public.
Phase 1420 does not publish the repository, source package, release artifact,
public RC, or public license.

```text
license_not_public_before_repo_authorized_public_phase_1420
```

## J-008 Evidence

Phase 1420 records the required evidence that the ADR-0041 Section 5 copyright
boundary has a project-authority disposition:

```text
copyright_counsel_disposition_complete_phase_1420
```

The J-008 gate source remains unchanged in this phase. `COPYRIGHT_COUNSEL_DISPOSITION`
still reports `NOT_MET` in `jury_activation_gate.py` until Phase 1425 performs
the pre-gate verification and any authorized static gate-source patch.

## Non-Authorizations

This disposition does not:

- provide an external legal opinion;
- provide attorney sign-off;
- authorize verbatim D2D distribution of copyrighted material;
- authorize default verbatim full-text storage of third-party copyrighted
  artifacts;
- authorize public repository publication;
- authorize public package publication;
- authorize license publication before repo-public authorization;
- activate open public ingestion;
- activate production jury assignment;
- activate reviewer payment;
- distribute ECU;
- write ledger, treasury, wallet, graph, registry, or CDL state;
- patch `jury_activation_gate.py`.

```text
copyright_counsel_not_external_legal_opinion_phase_1420
```

## References Consulted

- U.S. Copyright Office, Fair Use Index:
  `https://www.copyright.gov/fair-use/`
- European Commission, Stakeholder consultation on AI and copyright compliance:
  `https://digital-strategy.ec.europa.eu/en/faqs/stakeholder-consultation-ai-and-copyright-compliance`

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_copyright_counsel_disposition_1420_v0.1.md -> j008/copyright_counsel_disposition
```
