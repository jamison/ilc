# CDL-001 Genesis Blocker Scoping 1188 v0.1

**Phase:** 1188
**Date:** 2026-05-04
**Status:** scoping only — no CDL opening

`cdl_001_genesis_blocker_scoping_committed_phase_1188`

---

## 1. Purpose

The launch roadmap identifies a `genesis_blocker` packaging/release track as required
before any public launch claim. This document scopes that blocker and the questions that
must be resolved before a formal constitutional opening.

This is a planning artifact only. It does not open a CDL, ratify a CDL, mutate the CDL
register, authorize public repo publication, or select license terms.

---

## 2. Identifier Collision Notice

The current CDL register already contains a historical ratified `CDL-001` for canonical
signer lineage definition. Therefore, the roadmap phrase "CDL-001 genesis_blocker" must
be reconciled before any future opening:

- It may be a public-launch blocker lane anchored to the existing CDL-001 lineage trust
  root.
- It may require a new fresh CDL number rather than reusing `CDL-001`.
- It may require a naming update in roadmap artifacts before opening.

This scoping phase deliberately does not alter the existing CDL-001 row.

---

## 3. Scope Questions

### Q1 — Release Artifact Scope

What constitutes a public release artifact?

Candidate surfaces:

- binary packages;
- Docker/container images;
- signed Genesis capsule bundle;
- star map release envelope;
- source release tarball;
- public repository tag;
- operator bootstrap bundle;
- all of the above.

Opening requirement: define which artifacts are public-release artifacts and which are
internal engineering custody artifacts.

### Q2 — Public Launch Trigger

What conditions constitute "public launch" for the blocker?

Candidate triggers:

- first public repository;
- first external contributor invitation;
- first public network node;
- first public announcement;
- first signed public Genesis v0.x/v1.0-rc release;
- first distribution of bootstrap artifacts to non-Genesis operators.

Opening requirement: define launch trigger(s) precisely enough that agents cannot bypass
the blocker by calling a public act "pre-release."

### Q3 — RC Milestone Relationship

Is the blocker a prerequisite for RC2, RC3, or public launch only?

Recommended answer for opening deliberation: it should not block internal RC2 work. It
should block any public launch claim, public repo publication, public release artifact,
or external operator bootstrap.

### Q4 — Packaging Governance

What governance applies to release tooling, signing keys, and distribution channels?

Required coverage:

- ADR-0036 operational release key binding;
- ADR-0037 Genesis Canonical Lineage Contract consistency;
- release envelope canonical JSON and hash stability;
- public distribution channel integrity;
- version equivalence checks between signed release envelope and canonical Genesis
  lineage metadata.

### Q5 — Counsel Track Dependency

Does the blocker require counsel sign-off before opening or before ratification?

Recommended answer for opening deliberation: counsel engagement should be a prerequisite
for ratification and public launch, but the blocker may be opened before counsel closure
if it explicitly records legal/counsel items as ratification conditions.

Counsel track surfaces:

- license terms;
- contributor agreement;
- trademark and identity policy;
- public documentation license;
- treatment of existing commit history under the selected license regime.

---

## 4. Proposed Blocker Scope

The public-launch blocker should cover:

- public release artifact definition and governance;
- human-authorized public launch gate conditions;
- integration with license/contributor/trademark counsel track;
- release key chain governance for public distribution;
- Genesis capsule bundle inclusion criteria;
- versioning posture for internal custody artifacts versus public release candidates;
- public documentation versus canonical identity artifact licensing boundary.

---

## 5. Opening Prerequisites

Recommended prerequisites before opening the blocker lane:

- CDL-085 ratified (`cdl_085_ratified_phase_1185`);
- RC2 gate status reviewed;
- v0.2 signing status reviewed;
- Tier-3 runtime linkage status reviewed;
- initial counsel engagement started or explicitly scheduled;
- identifier collision resolved: reuse existing CDL-001 lineage anchor, open a fresh CDL
  number, or rename the blocker lane before opening.

---

## 6. Estimated Sequencing

Opening target:

- Window 1191+ after Phase 1190 closure and counsel-track routing review.

Ratification target:

- pre-public-RC and before any external announcement, public repo publication, public
  release artifact, or external operator bootstrap.

---

## 7. Non-Claims

This scoping document does not:

- open CDL-001 or any fresh CDL;
- amend the existing ratified CDL-001 signer-lineage row;
- accept any ADR;
- authorize public repository publication;
- select license terms;
- make legal conclusions;
- authorize v0.2 signing;
- generate release keys.

---

## 8. Scoping Token

`cdl_001_genesis_blocker_scoping_committed_phase_1188`
