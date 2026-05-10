# ILC Window 1289-1302 Candidate Phase Grouping v0.1

**Status:** Locked by Phase 1289 sequence lock after human authorization.
**Recorded:** 2026-05-10.
**Authority:** This document is planning support for the Phase 1289 sequence
lock. The lock is `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`.

```text
window_1289_1302_candidate_phase_grouping_recorded_phase_1289
window_1289_1296_candidate_grouping_superseded_by_1289_1302_phase_1289
public_rc_candidate_standard_preserved_window_1289_1302
```

## Purpose

The earlier Phase 1288 Fix2 package drafted Window 1289-1296 as a narrow
preflight runway. The human reviewer then clarified that phase windows should
use the logical number of phases for the work area, not an artificial eight
phase width. Phase 1289 therefore expands the next window to 1289-1302.

This window remains an authority and surface-contract window. It does not make
a public RC claim, activate public serving, publish source, produce release
artifacts, mutate Genesis, open CDL-088, or sign v0.2.

## Human Escalation Discipline

If any phase discovers uncertain authority, contradictory canon, a widening
decision, or a scope question that cannot be resolved from committed documents,
it must stop and prompt the human reviewer.

```text
human_question_escalation_required_for_uncertain_authority
```

Default to the narrower no-authorization route. Phase 1291 also preserves no public endpoint or claimability activation by default.

This guidance does not activate public claimability, authorize public sidecar/projection serving, authorize ECU minting, authorize ILC settlement or withdrawal runtime, or authorize v0.2 signing.

## Candidate Phase Order

| Phase | Scope | Sensitivity | Primary blocker or lane |
|-------|-------|-------------|--------------------------|
| 1289 | Window 1289-1302 sequence lock | SENSITIVE | Opens the expanded window and fixes sensitive gates. |
| 1290 | Context Capsule v5.52 frontier refresh | NON-SENSITIVE | Refreshes canon before sensitive blocker work. |
| 1291 | Public claimability verifier contract preflight | SENSITIVE | Gap 13 verifier/API authority, no public endpoint by default. |
| 1292 | Verifier negative-path corpus and package-profile boundary | SENSITIVE | Gap 13 proof safety, forged receipts, roots, replay, exact numerics. |
| 1293 | PUBLIC_RC_EXCLUDE helper promotion/removal register | SENSITIVE | Gap 14 package attack-surface control. |
| 1294 | Claimability package allowlist rehearsal | SENSITIVE | Phase 1255 allowlist rehearsal, no source export or package publication. |
| 1295 | TransportPrincipal lifecycle, revocation, replay preflight | SENSITIVE | Gap 10 public path identity blocker. |
| 1296 | Hostile-network admission, ban, rate-limit, privacy plan | SENSITIVE | Gap 10 and Gap 11 hostile-network hardening. |
| 1297 | Sidecar public-safe projection schema | SENSITIVE | Public-safe projection field and privacy blocker. |
| 1298 | Sidecar bind, listener, peer-discovery authority preflight | SENSITIVE | Non-loopback/public sidecar serving blocker. |
| 1299 | Release allowlist, artifact, Genesis readiness preflight | SENSITIVE | Release and signing readiness, no artifacts by default. |
| 1300 | Counsel, IP, publication clearance inventory | SENSITIVE | IP-001 and IP-006 internal clearance, PUBLIC_RC_EXCLUDE by default. |
| 1301 | Deep no-activation assertion audit | SENSITIVE | Confirms no accidental public endpoint, release, signing, or economics. |
| 1302 | Window 1289-1302 closure gate | SENSITIVE | Classifies blockers as closed, open, or carried forward. |

## Carry-Forward Blockers

- Final public claimability verifier/API authority and release allowlist
  promotion.
- Actual TransportPrincipal public-path activation plus lifecycle, revocation,
  replay, admission, ban, and hostile-network hardening.
- Actual public sidecar/projection serving authorization, public-safe field
  schema, filtering, bind/listener policy, and peer-discovery policy.
- Counsel, license, CLA, trademark, patent, and publication authorization.
- Source allowlist export execution, public source publication, package
  publication, release artifacts, release keys, release envelopes, and release
  manifest instance production.
- Genesis Atlas mutation/regeneration/signing and v0.2 signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- Wallet withdrawal/transfer/spend, ECU minting, ILC settlement, and withdrawal
  runtime activation.

## Non-Claims

This grouping does not authorize public RC, public launch, public claimability,
public verifier/API serving, public P2P, public fetch serving, public
sidecar/projection serving, source export, source publication, package
publication, release artifact production, release keys, release envelopes,
Genesis mutation/signing, v0.2 signing, CDL mutation, CDL-088 opening, wallet
economics, ECU minting, ILC settlement, IP filing, or paper publication.
