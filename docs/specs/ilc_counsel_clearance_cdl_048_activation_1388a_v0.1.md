# ILC Counsel Clearance for CDL-048 Activation 1388a v0.1

**Phase:** 1388a
**Date:** 2026-05-19
**Status:** GENESIS-AUTHORITY SELF-COUNSEL DECISION — FINAL FOR CDL-048 PRE-PRODUCTION/TESTNET ACTIVATION SCOPE
**Authority:** Genesis authority under the self-counsel model recorded in the launch roadmap

```text
counsel_clearance_cdl_048_activation_phase_1388a
self_counsel_decision_not_external_legal_opinion_phase_1388a
```

## 1. Purpose

Phase 1388 failed closed because the Phase 1388 prompt required formal external
counsel sign-off, while the current project planning lane uses a Genesis-authority
self-counsel model for pre-production decisions.

This record supplies the missing internal self-counsel decision for the narrow
CDL-048 activation surface. It is final for the project's pre-production/testnet
activation purposes. It is not external legal advice, not attorney sign-off, and
not a licensed-practitioner opinion.

## 2. Scope of Clearance

This clearance applies only to a future Phase 1388 rerun that unlocks the
CDL-048 ECU-to-ILC conversion-path plumbing in the current pre-production,
closed-network/testnet context.

The clearance does not authorize:

- public claimability or public API activation;
- public source publication or public RC publication;
- mainnet launch;
- public ECU-to-ILC conversions with real-world economic value;
- inviting external parties to use the conversion path;
- external contributor onboarding;
- token sale, investment offer, or public value distribution;
- legal conclusion for any jurisdiction.

Phase 1389 remains a separate SENSITIVE public-claimability gate.

## 3. Token Classification Position

Genesis authority records the following internal position for the current
pre-production/testnet context:

- ILC has not been offered, sold, distributed, or marketed to external parties as
  an investment instrument or security.
- No public offering has occurred.
- No external party has been invited to rely on the CDL-048 conversion path.
- A Phase 1388 runtime unlock would authorize protocol plumbing only; it would
  not itself create a public value distribution or financial-instrument
  transaction.
- Public claimability and public verifier/API exposure remain separately gated.

This position is limited to current repo-controlled pre-production/testnet work.
It does not decide mainnet, public external-use, exchange, secondary-market,
consumer, tax, sanctions, or jurisdiction-specific classification questions.

## 4. Activation-Scope Decision

Genesis authority accepts the legal/governance risk of unlocking CDL-048
conversion-path plumbing for pre-production/testnet purposes after the Phase 1387
and Phase 1387a technical gates have passed.

This decision is final for that narrow internal purpose. It supersedes the
Phase 1388 blocked condition that treated "counsel clearance" as requiring
external counsel sign-off for this pre-production activation step.

The decision does not supersede broader public-launch counsel/IP/publication
obligations. Those remain open until separately closed.

## 5. Relationship to Existing Counsel Artifacts

| Artifact | Phase 1388a disposition |
|----------|-------------------------|
| `LICENSING.md` | Receives a scoped note: the self-counsel decision is final for CDL-048 pre-production/testnet activation only; it is not an external legal opinion. |
| `docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md` | Receives a scoped addendum: the CDL-048 activation surface is no longer provisional for testnet activation purposes only. |
| `docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md` | Remains inventory-only and does not authorize public publication. |
| `ilc_core/rc/public_rc_publication_claim_gate.py` | Remains a public-RC publication gate; Phase 1388a does not close the broader publication blocker. |

## 6. Phase 1388 Rerun Prerequisite

A future Phase 1388 rerun may treat this artifact as satisfying the
CDL-048 activation-specific counsel-clearance prerequisite, provided the rerun
also confirms:

- Phase 1387 PASS through the superseding v0.2 rerun report;
- Phase 1387a PASS through the public-economics admission firewall;
- CDL-048 runtime remains in a known gate-closed state before unlock;
- no new blocker has been introduced.

The rerun remains SENSITIVE and requires explicit `GO Phase 1388`.

## 7. Non-Authorization

Phase 1388a does not unlock CDL-048 runtime, mutate `ilc_core/`, mutate the CDL
register, activate public claimability, open Phase 1389, publish source, publish
public RC artifacts, invite external users, accept external contributors,
authorize mainnet launch, provide external legal advice, or record an attorney
opinion.

## 8. Graph Delta

`graph_delta=load_bearing_artifact_added:docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md -> value-path/self-counsel-clearance`
