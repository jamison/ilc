# CDL-086 Prelock Specification 1204 v0.1

**Phase:** 1204
**Window:** 1200-1208
**Date:** 2026-05-05
**Status:** PRELOCKED — not ratified
**Authority:** `GO Phase 1204`; Phase 1194 opening; Phase 1203 Q1-Q5 deliberation

`cdl_086_prelock_committed_phase_1204`

---

## 1. Identity

CDL-086 is the **Public-Launch Packaging Blocker**.

- Opening phase: 1194
- Opening token: `cdl_086_public_launch_packaging_blocker_opened_phase_1194`
- Opening spec: `docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md`
- Deliberation phase: 1203
- Deliberation token: `cdl_086_deliberation_committed_phase_1203`
- Deliberation spec: `docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md`

This prelock records resolved scope and ratification conditions. It does not ratify
CDL-086 and does not mutate the CDL register.

---

## 2. Q1-Q5 Resolutions

Phase 1203 resolved all five opening questions without human blockers.

| Q | Resolution |
|---|------------|
| Q1 — Release artifact scope | Public release artifacts are any ILC artifact distributed or advertised outside Genesis/internal engineering custody as a release, installable, bootstrap, verification, or canonical-reference surface. Binding examples: source release tarball, public repository tag, binary package, container image, signed Genesis capsule bundle, star-map release envelope, operator bootstrap bundle, and public documentation bundle. |
| Q2 — Public launch trigger | CDL-086 triggers on first public repository publication, external contributor invitation, public network node, public announcement, signed public Genesis release, bootstrap distribution to non-Genesis operators, or equivalent external-reliance act. Preview/alpha/internal/community labels do not bypass the blocker. |
| Q3 — RC milestone relationship | CDL-086 does not block internal RC2 engineering work. It gates public-launch/RC3-facing acts: public launch claims, public repository publication, public release artifacts, public RC announcements, and external operator bootstrap. |
| Q4 — Packaging governance | Governance binds to ADR-0036 release-key and release-envelope rules, ADR-0037 lineage/fork/version-equivalence rules, CDL-001 signer-lineage trust root, CDL-085 provenance-equivalence limit, and deterministic canonicalization rules. |
| Q5 — Counsel track dependency | Counsel closure is a ratification and public-launch condition, not an opening or deliberation prerequisite. License, contributor agreement, trademark/identity policy, documentation license, and commit-history treatment must be counsel-approved or explicitly deferred by later human-authorized constitutional decision before ratification. |

---

## 3. Prelocked Boundary

CDL-086 blocks:

- public launch claims;
- public repository publication;
- public release artifact distribution;
- public RC announcements;
- external contributor onboarding advertised as public participation;
- external operator bootstrap;
- any external-reliance act relabeled as preview, alpha, internal preview, community
  preview, or pre-release.

CDL-086 does not block:

- internal RC2 implementation work;
- private tests;
- private documentation;
- internal planning docs;
- local release-candidate experiments not distributed or advertised externally;
- Phase 1201/1202 runtime implementation work;
- Phase 1204 prelock itself.

---

## 4. Dependency Chain

CDL-086 ratification depends on:

- `CDL-001` — ratified signer-lineage trust-root canon;
- `ADR-0036` — Operational Release Key / Genesis Binding;
- `ADR-0037` — Genesis Canonical Lineage Contract;
- `CDL-085` — ratified Werner φ-bound provenance equivalence limit;
- `launch_roadmap_v1_0_published_phase_1192`;
- `cdl_086_public_launch_packaging_blocker_opened_phase_1194`;
- `cdl_086_deliberation_committed_phase_1203`.

---

## 5. Ratification Conditions

Before CDL-086 can be ratified, a later sensitive constitutional phase must provide:

1. Release artifact manifest schema.
2. Distribution channel integrity checklist.
3. ADR-0036 release-key registration and release-envelope procedure.
4. ADR-0037 public verification path from release artifact to signed Genesis lineage.
5. Public repository publication authorization boundary.
6. Counsel disposition for license, contributor agreement, trademark/identity policy,
   public documentation license, and existing commit-history treatment.
7. Non-bypass language for preview/alpha/internal/community labels.
8. v0.2 signing status and sequencing against public artifact release.
9. Human authorization for any public launch claim or public release artifact distribution.

Counsel items may be satisfied by counsel approval or by a later explicit human-authorized
constitutional deferral. No implicit deferral is allowed.

---

## 6. Non-Claims

This prelock does not ratify CDL-086 and does not:

- mutate `docs/specs/ilc_constitutional_decision_log_v0.1.md`;
- authorize a public launch claim;
- authorize public repository publication;
- authorize public release artifact distribution;
- select license terms;
- create legal conclusions;
- complete counsel review;
- execute v0.2 signing;
- generate or register release keys;
- produce a release envelope;
- mutate `ilc_core/`;
- mutate signed Genesis v0.1.

---

## 7. Prelock Token

`cdl_086_prelock_committed_phase_1204`
