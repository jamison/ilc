# CDL-086 Ratification Evidence 1220 v0.1

**Phase:** 1220
**Window:** 1218-1224
**Date:** 2026-05-06
**Status:** RATIFIED
**Authority:** `GO Phase 1220`; `ILC_CDL_MUTATION_AUTHORIZED=1`; `ILC_CDL_MUTATION_PHASE=1220`

`cdl_086_ratified_phase_1220`

---

## 1. Ratification Statement

CDL-086, the Public-Launch Packaging Blocker, is ratified in Phase 1220.

Ratification satisfies the governance precondition for the blocker lane. It does not
authorize public launch, public repository publication, public release artifact distribution,
public RC announcement, external contributor onboarding, external operator bootstrap, v0.2
signing, release-key generation, or any equivalent launch-adjacent act.

The counsel disposition basis is
`docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md`. That record contains
Genesis-authorized provisional dispositions, not counsel-approved legal conclusions.

---

## 2. Prelock Condition Disposition

CDL-086 prelock §5 listed nine ratification conditions. Their Phase 1220 disposition:

| # | Condition | Phase 1220 disposition |
|---|-----------|------------------------|
| 1 | Release artifact manifest schema | SATISFIED by `release_artifact_manifest_schema_committed_phase_1213` and `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`. |
| 2 | Distribution channel integrity checklist | SATISFIED by `distribution_channel_integrity_checklist_committed_phase_1213` and `docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md`. |
| 3 | ADR-0036 release-key registration and release-envelope procedure | GOVERNANCE BASIS SATISFIED by accepted ADR-0036; operational release-key generation and v0.2 signing remain separately authorization-gated. |
| 4 | ADR-0037 public verification path from release artifact to signed Genesis lineage | GOVERNANCE BASIS SATISFIED by accepted ADR-0037; public verification procedure remains subject to the no-publication boundary below. |
| 5 | Public repository publication authorization boundary | SATISFIED as a blocking boundary: no public repository publication is authorized by CDL-086 ratification. |
| 6 | Counsel disposition for license, contributor agreement, trademark/identity policy, public documentation license, and existing commit-history treatment | SATISFIED by explicit Genesis-authorized provisional dispositions in `ilc_cdl_086_counsel_disposition_1220_v0.1.md`; counsel review remains a carry-forward before public launch-adjacent acts. |
| 7 | Non-bypass language for preview/alpha/internal/community labels | SATISFIED: CDL-086 continues to block equivalent external-reliance acts regardless of preview/alpha/internal/community relabeling. |
| 8 | v0.2 signing status and sequencing against public artifact release | SATISFIED as a sequencing record: v0.2 signing remains deferred pending explicit signing authorization; no signing occurs in Phase 1220. |
| 9 | Human authorization for any public launch claim or public release artifact distribution | SATISFIED as a blocking boundary: no such authorization is present or granted by this ratification. |

---

## 3. Counsel Disposition C1-C5

The five counsel items are recorded in full in
`docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md`.

Summary:

| Item | Disposition | Legal status |
|------|-------------|--------------|
| C1 — License terms | Mixed-zone license strategy adopted provisionally; "MIT for all zones at public release" rejected; exact instruments pending counsel. | Not counsel-approved. |
| C2 — Contributor agreement | CLA-style contributor agreement required before external contributions if staged relicensing/sunset remains possible; DCO-only rejected as sole mechanism. | Not counsel-approved. |
| C3 — Trademark / identity policy | Trademark and canonical identity policy required before public launch; ILC identity reserved for Genesis-lineage systems. | Not counsel-approved. |
| C4 — Public documentation license | Two-tier documentation model: permissive explanatory/research docs plus strict canonical-identity terms for Genesis artifacts and lineage receipts. | Not counsel-approved. |
| C5 — Existing commit history treatment | Clean allowlist-based public export; private canonical repository history remains unpublished and intact. | Not counsel-approved. |

---

## 4. Carry-Forward Obligations

The following obligations remain open after ratification:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
```

These obligations are launch-adjacent blockers. They are not waived by CDL-086 ratification.

---

## 5. Non-Authorization Boundary

CDL-086 ratification does not authorize:

- public launch claims;
- public repository publication;
- public release artifact distribution;
- public RC announcement;
- external contributor onboarding;
- external operator bootstrap;
- v0.2 signing;
- release-key generation or registration;
- release envelope production;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation;
- runtime mutation.

Any later act in those categories requires a separate constitutional authorization path.

---

## 6. References

- `docs/specs/ilc_cdl_086_public_launch_packaging_blocker_opening_1194_v0.1.md`
- `docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md`
- `docs/specs/ilc_cdl_086_prelock_spec_1204_v0.1.md`
- `docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md`
- `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
- `docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md`
- `docs/adr/ADR_0036_Operational_Release_Key_Genesis_Binding.md`
- `docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md`

