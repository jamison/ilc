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

---

## Postscript — Obligation Status Update (Phase 1175, 2026-05-04)

This postscript records obligation resolution and forward routing after Window 1166-1175
closed. No obligation content is retroactively amended — this is a forward-only status
supplement.

| Obligation | Status at Phase 1154 | Status at Phase 1175 |
|------------|----------------------|----------------------|
| Canonical Lineage Contract | Planning spec only | **RESOLVED** — ADR-0037 accepted (`adr_0037_accepted_phase_1173`); covers 6 equivalence domains, PEC, merge policy, multi-slice encrustation, fork boundary |
| Atlas Tier-2 signing ceremony | Blocked (release-key ADR not open) | **UNBLOCKED** — ADR-0036 accepted (`adr_0036_accepted_phase_1173`); v0.2 candidate 41 nodes / 73 edges; explicit human authorization still required to execute |
| `CDL-085` (φ-bound) | SIM-gated, unopened | **OPEN** (Phase 1172) — SIM-SPECTRAL-05 passed; `EDGE_MINT_PHI_BOUND` unset pending CDL-085 prelock (Window 1176+) |
| ADR-0020 acceptance | `adr_0020_acceptance_review_priority_before_tier3_embedding_linkage` | **RESOLVED** — ADR-0020 accepted (`adr_0020_accepted_phase_1157`); governance prerequisite for Tier-3 met; runtime lane separate |
| ADR-0036 acceptance | Release-key ADR not yet open | **RESOLVED** — ADR-0036 accepted (`adr_0036_accepted_phase_1173`) |
| Truth-primitive permanence | Carry-forward | Carry-forward (unchanged) — community ratification required before Genesis sunset |
| Envelope transition policy | Planning level only | Carry-forward (unchanged) |
| Canon bundle signing failures | Tooling debt | Carry-forward (unchanged) |
| Contributor agreement | Counsel track | Carry-forward (unchanged) |
| License strategy | Counsel track | Carry-forward (unchanged) |
| Trademark / identity policy | Counsel track | Carry-forward (unchanged) |

### Post-Phase-1175 sequencing for remaining obligations

Recommended Window 1176+ routing for items remaining open:

1. **CDL-085 prelock** — Window 1176; establishes `EDGE_MINT_PHI_BOUND` candidate from
   SIM-SPECTRAL-05 Track B branchial separation (0.60).
2. **v0.2 signing ceremony** — Window 1176 (if explicit signing authorization issued).
3. **Remaining SIM-SPECTRAL-05 slices** — runtime-binding, economic-flow, gossip
   deferred to Window 1176+.
4. **Tier-3 runtime linkage** (`schema:*` / `runtime:*`) — ADR-0020 governance met;
   runtime lane not yet implemented; Window 1178+.
5. **CDL-001 (genesis_blocker / packaging track)** — required before any public launch
   claim; evaluation Window 1178+.
6. **Truth-primitive permanence community ratification** — pre-public-RC requirement.
7. **Counsel track** — contributor agreement, license, trademark/identity — parallel lane.

See launch roadmap v0.9 (`docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v0.9.md`)
for the canonical forward-planning summary.

`pre_public_rc_obligations_synthesis_postscript_phase_1175`
