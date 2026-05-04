# ILC Pre-Public-RC Obligations Synthesis 1154 v0.1

Status: obligations register; planning only
Phase: 1154
Date: 2026-05-04

`pre_public_rc_obligations_synthesis_committed_phase_1154`

---

## 1. Purpose

This document consolidates pre-public-RC obligations carried from Phases 1146-1153. It
records routing, current disposition, and remaining gaps. It does not make legal
conclusions, choose license terms, open governance decisions, or authorize public release.

---

## 2. Obligations Register

| Obligation | Token | This window disposition | Remaining gap |
|------------|-------|-------------------------|---------------|
| Canonical Lineage Contract | `genesis_canonical_lineage_contract_required_before_public_rc` | Planning spec drafted in Phase 1153 | Formal ADR opening and acceptance/ratification route |
| Truth-primitive permanence | `truth_primitive_permanence_requires_community_ratification_before_genesis_sunset` | Recorded as governance carry-forward; no CDL mutation | Community ratification event or CDL before Genesis sunset |
| Envelope transition policy | `public_rc_envelope_hash_transition_policy_required` | Addressed in Phase 1153 planning spec | Formal transition envelope policy in ADR/CDL/release process |
| Contributor agreement | `contributor_agreement_required_before_public_repo` | Registered as pre-public repo requirement | Counsel/human drafting and adoption |
| License strategy | counsel track | Registered as parallel counsel lane | Counsel review before public repo; no terms selected here |
| Trademark / identity policy | counsel track | Registered as parallel counsel lane | Human + counsel policy before public launch |
| Canon bundle signing failures | tooling debt | Carried forward from Phase 1147 | Repair `test_canon_bundle_audit_artifact.py` and `test_canon_bundle_pipeline_report.py` root cause |
| ADR-0008 acceptance | `adr_0008_tier2_blocked_status_proposed_not_accepted` | Blocked in Phase 1148 | ADR acceptance review before Tier-2 promotion |
| ADR-0020 acceptance | `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage` | Priority-blocked in Phase 1148 | Acceptance review before Tier-3 embedding linkage |
| ADR-0012/0022/0023 acceptance batch | proposed ADR batch | Blocked in Phase 1148 | Window 1157+ acceptance review batch |
| Atlas Tier-2 signing ceremony | conditional tail slot | v0.2 candidate remains unsigned unless Phase 1156 authorized | Operational release-key ADR or Genesis exceptional signing authorization |

---

## 3. Current Disposition By Lane

### Governance / Canon

- `CDL-085` remains SIM-gated and unopened.
- Truth-primitive permanence requires community-ratified treatment before Genesis sunset.
- Proposed ADRs are not promoted into the canonical star map until accepted.

### Release / Lineage

- Genesis Canonical Lineage Contract planning spec exists.
- Public RC envelope transition policy is drafted at planning level only.
- Operational release key ADR is not open in this window.

### Counsel / Public Repo

- Contributor agreement, license strategy, and trademark/identity policy require human and
  counsel review before public repo or public launch.
- This document makes no legal recommendation.

### Tooling

- Canon bundle signing failures remain known pre-existing tooling debt.
- Signed v0.1 Genesis artifacts remain immutable.

---

## 4. Next Routing

Recommended Window 1157+ routing:

1. ADR-0020 acceptance review priority before Tier-3 embedding linkage.
2. ADR-0012/0022/0023/0008 acceptance review batch.
3. Formal Genesis Canonical Lineage Contract ADR opening.
4. Release-key ADR scoping and operational release-key binding.
5. SIM-SPECTRAL-04 execution planning from the Phase 1152 program spec.
6. Counsel-track kickoff for contributor agreement, license, and trademark/identity
   policy.

---

## 5. Non-Claims

This synthesis does not:

- authorize public repo publication;
- select license terms;
- make legal conclusions;
- open or ratify any CDL;
- accept any proposed ADR;
- authorize Phase 1156 signing;
- modify runtime semantics.

---

`pre_public_rc_obligations_synthesis_committed_phase_1154`
