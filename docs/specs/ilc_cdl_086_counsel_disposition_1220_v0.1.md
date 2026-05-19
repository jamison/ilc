# CDL-086 Counsel Disposition Record 1220 v0.1

**Phase:** 1220
**Window:** 1218–1224
**Date:** 2026-05-06
**Status:** GENESIS-AUTHORIZED PROVISIONAL DISPOSITIONS — NOT COUNSEL-APPROVED LEGAL CONCLUSIONS
**Authority:** Human Genesis authority; Phase 1220 precondition 1

`cdl_086_counsel_disposition_recorded_phase_1220`

---

## 1. Purpose and Framing

This document records Genesis-authorized provisional dispositions for the five counsel items
required by CDL-086 prelock §5 condition 6. These dispositions are made by the Genesis
authority as constitutional calls. They are not counsel-approved legal conclusions. Exact
license instruments, trademark filings, CLA text, and commit-history export details require
formal counsel review before any public launch act is authorized.

No public launch act, public repository publication, public release artifact distribution,
or external contributor onboarding is authorized by this record. CDL-086 ratification
satisfies the governance precondition; separate constitutional act(s) remain required before
any launch-adjacent act.

---

## 1a. Phase 1388a Scoped Self-Counsel Addendum

Phase 1388a records a Genesis-authority self-counsel decision for the narrow
CDL-048 pre-production/testnet activation surface:

```text
counsel_clearance_cdl_048_activation_phase_1388a
self_counsel_decision_not_external_legal_opinion_phase_1388a
```

For this narrow surface only, the CDL-048 activation-relevant legal/governance
posture is no longer provisional for internal pre-production/testnet activation
purposes. The Phase 1388a decision is a Genesis-authority decision final for
that purpose.

This addendum does not convert the Phase 1220 counsel disposition into an
external counsel opinion. It does not authorize mainnet launch, public
repository publication, public release artifact distribution, public
claimability, external contributor onboarding, public conversions with
real-world economic value, or inviting external parties to use the conversion
path.

---

## 2. Disposition Record

### C1 — License Terms

**Disposition:** Genesis-authorized provisional adoption of mixed-zone license strategy.

**Call:** Adopt the mixed-zone license framework proposed in
`docs/research/ilc_genesis_lineage_fork_resistance_and_license_strategy_v0.1.md` §7 as the
governing strategic direction. Zone assignments:

| Zone | Bootstrap posture | Post-maturity posture |
|------|------------------|-----------------------|
| `ilc_core/` runtime, consensus, gossip network layer | Strong copyleft (AGPLv3) or source-available; bootstrap protection required | Permissive or GPL-family after maturity trigger; specific instrument pending counsel |
| ECU settlement and attribution runtime | Strongest copyleft or source-available / dual license | Later permissive or GPL-family after network maturity; specific instrument pending counsel |
| Genesis canonical artifacts (manifests, root envelope specs, authority-map specs, canonical lineage receipts) | Strict canonical-identity license; unmodified redistribution permitted; modification must identify as fork / non-canonical | Remains strict for identity purposes; relaxation only by explicit ratified constitutional decision |
| Core protocol interfaces, schemas, verification formats | Permissive or weak copyleft (Apache-2.0 / MIT compatible) | Apache-2.0 / MIT or equivalent after sunset |
| Explanatory public papers, non-operational research docs | Permissive documentation license (CC BY 4.0 or equivalent) | Remains permissive |
| Official transparency log, release registry, hosted canonical services | Controlled service terms | May remain controlled; not a code license |
| Name, logos, official network identity marks | Trademark policy; not a code license grant | No automatic sunset; governed by C3 below |

Exact license instruments (SPDX identifiers, license files, license headers) require counsel
review and approval before public RC artifact distribution. "MIT for all zones at public
release" is explicitly rejected. Fork-resistance memo §4 ranked mechanisms confirm that
runtime/ECU/gossip zones require stronger protection during bootstrap.

Maturity trigger: hybrid (validator diversity threshold + non-Genesis governance share +
ECU settlement maturity + transparency-log continuity); not a pure calendar trigger. Specific
thresholds require ratified constitutional decision.

**Status:** Provisional — exact legal instruments and SPDX expressions pending counsel.
**Blocks lifted by this item:** None. Counsel review remains required before public RC.

---

### C2 — Contributor Agreement

**Disposition:** Genesis-authorized provisional requirement for CLA-style contributor
agreement; DCO-only is insufficient if staged relicensing or license sunset remains possible.

**Call:** A CLA-style contributor agreement (inbound license grant permitting future
relicensing to match the C1 sunset trigger) is required before any external public
contribution is accepted. Alternatively, no external contributions are accepted until counsel
has completed the CLA review and a ratified contributor agreement is in place.

DCO (Developer Certificate of Origin) alone is explicitly rejected for this project as the
sole contributor mechanism while staged relicensing or license sunset remains a strategic
option. DCO certifies origin but does not grant the relicensing rights needed to execute a
license sunset transition.

The CLA text, signing mechanism, and governance integration must be drafted and approved by
counsel before external contributor onboarding begins.

The existing repository history (authored before public release under Genesis authority) must
also be addressed in the CLA framework; implicit retroactive application is not acceptable.

**Status:** Provisional — CLA text and mechanism pending counsel.
**Blocks lifted by this item:** None. Counsel review remains required before external
contributor onboarding.

---

### C3 — Trademark / Identity Policy

**Disposition:** Genesis-authorized provisional requirement for trademark and canonical
identity policy before any public launch act.

**Call:** The "ILC" name, official network identity names, logos, and identity assets are
reserved. A trademark/canonical identity policy must be established and published before any
public repository publication, public RC announcement, or external operator bootstrap. The
policy must include at minimum:

- "ILC" mark and official network names may be used only with systems carrying valid
  Genesis-lineage proofs as defined by the canonical lineage contract
  (`genesis_canonical_lineage_contract_required_before_public_rc`).
- Forks must identify themselves as non-canonical and may not use the "ILC" name or
  official identity marks to represent canonical ILC participation.
- Impersonation or misleading use of canonical identity marks is prohibited.

This is the highest-organic-pull fork-resistance mechanism (ranked #1 by economic moat in
the fork-resistance memo when combined with rolling ECU recognition). Code may be forkable
under the applicable license; canonical ILC identity requires Genesis lineage.

**Status:** Provisional — policy text and trademark filing (if pursued) pending counsel.
**Blocks lifted by this item:** None. Policy must be formally drafted before public launch.

---

### C4 — Public Documentation License

**Disposition:** Genesis-authorized provisional adoption of two-tier documentation license.

**Call:** Documentation is not a single license zone. Two tiers apply:

**Tier 1 — Explanatory / research docs:** Whitepapers, public summaries, non-operational
research documents, and explanatory specs (content whose purpose is public understanding
and citation, not canonical identity or operational protocol specification). License: CC BY
4.0 (Creative Commons Attribution 4.0 International) or equivalent. Maximize public
understanding and citation.

**Tier 2 — Genesis canonical artifact docs:** Genesis intent attestation specs, signed root
envelope descriptions, authority-map specs, canonical lineage receipts, release-key binding
docs, CDL ratification evidence docs, and any document whose modification would produce a
misleading canonical identity claim. License: strict canonical-identity terms (same zone as
Genesis canonical artifacts in C1 above). Unmodified redistribution permitted; modification
must identify as fork / non-canonical.

The boundary between tiers must be explicitly marked per document. Not every document under
`docs/` belongs in Tier 1 by default. Assignment defaults: documents that are
operationally-load-bearing for lineage or identity claims route to Tier 2 unless explicitly
assigned to Tier 1.

**Status:** Provisional — license file content, marking conventions, and boundary
classification pending counsel.
**Blocks lifted by this item:** None. Counsel review remains required before public release.

---

### C5 — Existing Commit History Treatment

**Disposition:** Genesis-authorized provisional decision: clean allowlist-based public export;
private canonical repository history remains unpublished and intact.

**Call:**
- The private canonical repository history (all phases, walkthroughs, internal
  deliberations) is the authoritative internal archive. It is NOT rewritten, squashed,
  amended, or destroyed. It remains under Genesis custody.
- The public repository (when authorized by a separate constitutional act) is generated
  from an explicit allowlist-based export: only artifacts approved for public release are
  included.
- The public export starts from a clean public genesis commit. Internal phase-by-phase
  history is not published.
- The allowlist-export procedure must be defined and reviewed before execution. It must not
  silently omit canonical lineage artifacts or produce a public history that implies a
  different authorship, governance, or development sequence than the canonical record.

This approach preserves internal deliberative privilege, reduces exposure of non-public
planning, and presents a canonical public-genesis starting point consistent with
ILC's Genesis-lineage model.

**Status:** Provisional — allowlist-export procedure and tooling pending definition.
**Blocks lifted by this item:** None. Export procedure requires review before execution.

---

## 3. Summary Table

| Item | Call | Status |
|------|------|--------|
| C1 License terms | Mixed-zone strategy adopted as direction; exact instruments pending counsel | Provisional |
| C2 Contributor agreement | CLA-style required before external contributions; DCO-only rejected for relicensing path | Provisional |
| C3 Trademark / identity | Policy required before public launch; "ILC" reserved for Genesis-lineage systems | Provisional |
| C4 Documentation license | Two-tier: CC BY 4.0 (explanatory) + strict canonical-identity (Genesis artifacts) | Provisional |
| C5 Commit history | Clean allowlist-based public export; private canonical history preserved unpublished | Provisional |

---

## 4. What This Record Does and Does Not Do

**Does:**
- Satisfies CDL-086 prelock §5 condition 6 (counsel disposition requirement) with explicit
  Genesis-authorized provisional dispositions.
- Provides Phase 1220 execution with concrete, non-implicit dispositions for each counsel
  item.
- Establishes strategic direction the project may use for counsel briefing.

**Does not:**
- Constitute counsel approval of any license instrument, trademark filing, CLA text, or
  export procedure.
- Authorize public launch, public repository publication, public release artifact
  distribution, public RC announcement, or external contributor onboarding.
- Select final SPDX license identifiers.
- Complete trademark registration.
- Produce the allowlist export.
- Relieve counsel review obligation before any public-launch act.

---

## 5. Carry-Forward Obligations

These obligations remain open after CDL-086 ratification:

```text
counsel_license_instrument_selection_required_before_public_rc
counsel_cla_text_approved_required_before_external_contributors
counsel_trademark_policy_published_required_before_public_launch
allowlist_export_procedure_defined_required_before_public_repo_publication
genesis_canonical_lineage_contract_required_before_public_rc
```

---

## 6. Reference Documents

- `docs/research/ilc_genesis_lineage_fork_resistance_and_license_strategy_v0.1.md` — source
  of mixed-zone license framework and fork-resistance ranking
- `docs/specs/ilc_cdl_086_prelock_spec_1204_v0.1.md` — §5 condition 6 defines the 5 items
- `docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md` — Q5 resolution confirms counsel track
  is a ratification condition, not an opening prerequisite
- `docs/research/ilc_rights_licenses_and_gated_access_surfaces_memo_v0.1.md` — L1/L2/L3
  gated access context
