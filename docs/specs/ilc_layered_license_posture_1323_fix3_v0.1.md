# ILC Layered License Posture 1323 Fix3 v0.1

Status: implemented repository posture / counsel review expected later
Date: 2026-05-12
Phase: 1323 Fix3
Owner lane: license, IP, publication, public-RC release boundary

```text
phase_1323_fix3_layered_license_posture.v0.1
blanket_mit_license_removed_phase_1323_fix3
agpl_runtime_default_recorded_phase_1323_fix3
licensing_zone_table_committed_phase_1323_fix3
genesis_canonical_identity_zone_recorded_phase_1323_fix3
patent_pending_zone_reserved_phase_1323_fix3
whitepaper_mit_language_replaced_phase_1323_fix3
ip_series_confirmed_as_ip001_to_ip006_phase_1323_fix3
public_rc_remains_blocked_after_phase_1323_fix3
```

## 1. Purpose

Phase 1323 Fix3 removes the repository's stale blanket-MIT posture and applies
the layered license strategy already recorded by CDL-086 counsel disposition C1
and the Phase 1280 Fix1 IP/publication lane registry.

This is a risk-reduction implementation for the private repository and any
unintended disclosure. It does not constitute legal advice and does not claim
outside-counsel approval.

## 2. Source Checks

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| Current root license was MIT | `LICENSE`; `pyproject.toml`; `tests/test_license_presence_phase_997.py` | Confirmed before this fix. |
| CDL-086 rejected MIT-for-all and adopted mixed-zone direction | `docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md` C1 | Confirmed. |
| CDL-086 legal instruments remained counsel-pending at Phase 1220 | `docs/specs/ilc_cdl_086_ratification_evidence_1220_v0.1.md` | Confirmed. |
| IP/patent publication lane exists | `docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md` | Confirmed as `IP-001` through `IP-006`, not a current `P-series` or `L-series`. |
| Phase 1300 kept IP-001..IP-006 internal-only | `docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md` | Confirmed. |

## 3. Implemented License Posture

Phase 1323 Fix3 implements:

- root `LICENSE` as an ILC layered license notice, not MIT;
- root `LICENSING.md` as the repository zone table;
- `pyproject.toml` package metadata for `ilc-core` as `AGPL-3.0-only`;
- focused regression coverage for the layered posture, IP lane names,
  whitepaper MIT-language cleanup, and planning backfill;
- runtime/source-code default as AGPL-3.0-only during bootstrap;
- strict canonical-identity zone for Genesis, lineage, release, and
  authority-bearing artifacts;
- CC BY 4.0 style posture for explanatory public documentation;
- All Rights Reserved / Patent Pending posture for patent-sensitive material;
- no code-license grant for ILC marks, official network identity, hosted
  services, canonical release identity, or lineage claims;
- stale whitepaper/draft text that described ILC as MIT-licensed replaced with
  layered-license language.

## 4. IP Lane Clarification

The remembered legal/patent phase series exists in current repo canon as:

| Phase | Current name |
|-------|--------------|
| IP-001 | IP inventory and disclosure-control map |
| IP-002 | Merkle-Laplacian dual commitment provisional draft package |
| IP-003 | Proof of Structural Knowledge provisional draft package |
| IP-004 | Sealed spectral beacon and spectral routing provisional draft package |
| IP-005 | Homoiconic star map / star expansion provisional draft package |
| IP-006 | Publication clearance matrix |

No current repo evidence was found for an active `P-series` or `L-series`
naming convention. The license track is carried by CDL-086 C1-C5, Roadmap Gap 7,
and this Fix3 layered-license implementation.

## 5. Non-Authorization Boundary

This fix does not authorize:

- public RC claim;
- public launch claim;
- public repository publication;
- public package publication;
- source allowlist export execution;
- clean public tree materialization;
- release artifact production;
- release-key generation;
- release envelope production;
- release signing material generation;
- v0.2 signing;
- Genesis Atlas mutation, regeneration, or signing;
- CDL mutation or CDL-088 opening;
- external contributor onboarding;
- trademark filing;
- trademark/canonical identity policy publication;
- patent filing;
- paper publication, paper submission, preprint release, or public abstract
  release;
- publication clearance matrix execution;
- removal of `PUBLIC_RC_EXCLUDE` from IP/publication-sensitive material;
- public OpenClaw/ClawHub listing or installability claim;
- public claimability activation;
- public P2P, public fetch serving, public listener, or public sidecar serving;
- wallet write authority, ECU minting, ILC settlement, or withdrawal runtime.

## 6. Graph Delta

```text
graph_delta=load_bearing_artifact_changed:LICENSE -> release/publication/licensing
graph_delta=load_bearing_artifact_added:LICENSING.md -> release/publication/licensing
graph_delta=load_bearing_artifact_changed:pyproject.toml -> package/license-metadata
graph_delta=support_tests_changed:tests/test_license_presence_phase_997.py -> validation
graph_delta=support_tests_added:tests/test_phase_1323_fix3_layered_license_posture.py -> validation
graph_delta=support_only:docs/whitepaper/ilc_whitepaper_agent_edition_v0.1.md,docs/whitepaper/ilc_whitepaper_agent_edition_v0.1_1.md,docs/whitepaper/ilc_whitepaper_agent_edition_v0.2.md,docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md,docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.1.md,docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.1_1.md,docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.2.md,docs/whitepaper_drafts/ilc_whitepaper_working_draft_v6_0.md -> public-docs/licensing-language
graph_delta=support_only:docs/specs/ilc_layered_license_posture_1323_fix3_v0.1.md -> release/publication/licensing
graph_delta=support_only:docs/PLANNING_INDEX.md,docs/phases/STATUS.md,docs/specs/ilc_antigravity_context_capsule_v5.54.md,docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md,docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
```
