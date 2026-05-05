# CDL-086: Public-Launch Packaging Blocker

**Status:** OPEN
**Opened:** Phase 1194 (2026-05-05)
**Authority:** Phase 1188 public-launch blocker scoping / launch roadmap v1.0 /
ratified CDL-001 signer-lineage canon / ADR-0036 / ADR-0037 / CDL-085

`cdl_086_public_launch_packaging_blocker_opened_phase_1194`

---

## 1. Problem Statement

ILC has an internal testbed frontier and a signed Genesis v0.1, but it does not yet have a
ratified public-launch packaging contract. Before any public launch claim, public repository
publication, public release artifact distribution, external operator bootstrap, or public
RC announcement, ILC needs a constitutional blocker that defines which packaging,
distribution, signing, counsel, and lineage conditions must be satisfied.

Phase 1188 identified roadmap label drift: the phrase "CDL-001 genesis_blocker /
packaging track" had drifted from the original ratified CDL-001 signer-lineage trust-root
scope. CDL-001 is already ratified signer-lineage canon and is not available for reuse.
This opening therefore uses a fresh CDL number.

This opening does not ratify the blocker. It opens the constitutional lane for
deliberation.

---

## 2. Scope

CDL-086 opens the following constitutional question:

> What public-launch packaging, release-artifact, signing, distribution, counsel, and
> lineage conditions must be satisfied before ILC may make any public launch claim or
> distribute any public release artifact?

The opening scope includes:

- public release artifact definition;
- public launch trigger conditions;
- RC milestone relationship;
- release packaging and distribution governance;
- release key chain and envelope requirements;
- Genesis capsule bundle inclusion criteria;
- dependency on ratified CDL-001 signer-lineage canon;
- dependency on ADR-0036 Operational Release Key;
- dependency on ADR-0037 Genesis Canonical Lineage Contract;
- dependency on CDL-085 and the active provenance-equivalence limit;
- counsel track as a ratification condition.

---

## 3. Opening Questions

### Q1 — Release Artifact Scope

Which artifacts count as public release artifacts?

Candidate surfaces:

- source release tarball;
- public repository tag;
- binary packages;
- Docker/container images;
- signed Genesis capsule bundle;
- star map release envelope;
- operator bootstrap bundle;
- public documentation bundle.

Opening posture: CDL-086 must distinguish public release artifacts from internal
engineering custody artifacts.

### Q2 — Public Launch Trigger

Which events trigger the blocker?

Candidate triggers:

- first public repository publication;
- first external contributor invitation;
- first public network node;
- first public announcement;
- first signed public Genesis v0.x/v1.0-rc release;
- first distribution of bootstrap artifacts to non-Genesis operators.

Opening posture: CDL-086 must prevent bypass through relabeling a public act as
"pre-release" or "internal preview."

### Q3 — RC Milestone Relationship

Does the blocker apply to RC2, RC3, public launch, or all three?

Opening posture: CDL-086 should not block internal RC2 engineering work. It should block
public launch claims, public repository publication, public release artifacts, and external
operator bootstrap until ratified conditions are satisfied.

### Q4 — Packaging Governance

What governance applies to release tooling, signing keys, and distribution channels?

Required deliberation surfaces:

- ADR-0036 release key registration;
- ADR-0036 release envelope binding;
- ADR-0037 version equivalence and fork boundary;
- canonical JSON and hash stability for release artifacts;
- public distribution channel integrity;
- verification path from public artifact back to signed Genesis lineage.

### Q5 — Counsel Track Dependency

What counsel-track conditions are required before ratification or launch?

Candidate surfaces:

- license terms;
- contributor agreement;
- trademark and identity policy;
- public documentation license;
- treatment of existing commit history under selected license regime.

Opening posture: counsel closure is a ratification and public-launch condition, not a
blocker to opening this CDL.

---

## 4. Dependencies

CDL-086 depends on:

- `CDL-001` — ratified signer-lineage canon;
- `ADR-0036` — Operational Release Key / Genesis Binding;
- `ADR-0037` — Genesis Canonical Lineage Contract;
- `CDL-085` — ratified Werner φ-bound provenance equivalence limit;
- Phase 1188 scoping token:
  `cdl_001_genesis_blocker_scoping_committed_phase_1188`;
- roadmap v1.0 token:
  `launch_roadmap_v1_0_published_phase_1192`.

---

## 5. Ratification Preconditions

Before CDL-086 can be ratified, a later phase must resolve at minimum:

1. exact release artifact list;
2. exact launch-trigger definition;
3. exact RC2/RC3/public-launch boundary;
4. release key registration and release envelope requirements;
5. distribution channel integrity requirements;
6. license, contributor agreement, trademark, and public documentation license posture;
7. signed Genesis lineage verification requirements;
8. v0.2 signing status and whether public release can proceed before or after v0.2 signing;
9. public repository publication authorization boundary;
10. non-bypass language for "preview", "alpha", "internal", or "community" labels.

---

## 6. Non-Claims

This opening does not:

- ratify CDL-086;
- authorize a public launch claim;
- authorize public repository publication;
- select license terms;
- create legal conclusions;
- complete counsel review;
- execute v0.2 signing;
- generate or register release keys;
- produce a release envelope;
- mutate `ilc_core/`;
- mutate signed Genesis v0.1.

---

## 7. Opening Token

`cdl_086_public_launch_packaging_blocker_opened_phase_1194`
