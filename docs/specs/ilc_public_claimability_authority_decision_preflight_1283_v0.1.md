# ILC Public Claimability Authority Decision Preflight 1283 v0.1

Status: authority preflight recorded / no public activation
Date: 2026-05-09
Phase: 1283
Owner lane: G8 public-RC economic boundary

Required tokens:

```text
public_claimability_authority_decision_preflight_phase_1283.v0.1
public_claimability_activation_requires_explicit_human_authorization_phase_1283
public_claimability_activation_not_authorized_by_default_phase_1283
wallet_withdrawal_transfer_spend_still_blocked_phase_1283
claimability_human_question_escalation_required_phase_1283
public_claimability_authority_verdict_phase_1283=no_activation_no_public_api
phase_1284_claimability_verifier_api_boundary_preflight_next
public_rc_remains_blocked_after_phase_1283
```

Verdict:

```text
public_claimability_authority_verdict_phase_1283=no_activation_no_public_api
```

Phase 1283 was executed after explicit human authorization to run the phase:

```text
GO Phase 1283
```

That authorization is authority to perform this sensitive preflight. It is not
authority to activate public claimability, expose a public or non-loopback
claimability API, enable wallet withdrawal, enable wallet transfer, enable
wallet spend, grant wallet signing authority, grant wallet ledger-write
authority, mint ECU, settle ILC, publish source, produce release artifacts, or
make a public-RC claim.

---

## 0. Discovery Discipline

Phase 1283 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval.
Authority analysis used direct repo reads and broader concept discovery before
the decision packet was written.

| Check | Result |
|-------|--------|
| §0a Known-token audit | Verified the Phase 1283 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1283_g8_public_claimability_authority_decision_preflight.md` and carried them into this packet, the walkthrough, STATUS, PLANNING_INDEX, Roadmap v1.1, and Capsule v5.51. |
| §0b Concept-discovery search | Searched public claimability, claim endpoint, verifier, API, wallet withdrawal, wallet transfer, wallet spend, wallet signing, ledger-write authority, ECU minting, ILC settlement, CDL-048, conversion sweeper, settled runtime root, wallet-state root, balance receipt, package profile, allowlist export, and release material. |
| §0c Contradiction and non-claim search | Searched denial terms including blocked, not authorized, not activated, deferred, local-only, no public, no wallet, no ECU minting, no ILC settlement, `PUBLIC_RC_EXCLUDE`, source allowlist, release artifact, and public-RC claim. |
| §0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source granted public claimability activation authority. The newly carried tokens are `public_claimability_authority_verdict_phase_1283=no_activation_no_public_api`, `phase_1284_claimability_verifier_api_boundary_preflight_next`, and `public_rc_remains_blocked_after_phase_1283`. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_window_1273_1280_handoff_1280_v0.1.md`
- `docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md`
- `docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md`
- `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md`
- `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md`
- `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
- `ilc_core/ledger/claimability_proof_binding_runtime.py`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/package_profile_ci_gate.py`
- `ilc_core/rc/local_skill_preview.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Decision Basis

The current claimability implementation evidence is materially stronger after
Phases 1274, 1275, and 1282 Fix1:

- CDL-048 conversion-sweeper skeleton exists with exact Decimal and epoch
  guards, receipt hashing, replay protection, deadline checks, and false public
  activation flags.
- Claimability proof binding exists over settled runtime root, wallet-state
  root, latest balance receipt, history digest, epoch identifier, canonical
  agent identity, and conversion receipt semantics.
- Phase 1282 Fix1 hardened forged-receipt resistance, root namespace
  separation, latest balance receipt Decimal-string boundaries, and
  `PUBLIC_RC_EXCLUDE` marking.

That evidence is sufficient for local proof-binding continuation. It is not
sufficient to activate public claimability because the public verifier/API
boundary is not yet closed, public endpoint authority is absent, release
allowlist review has not promoted the internal helpers, and wallet
withdrawal/transfer/spend semantics remain intentionally blocked.
The release allowlist review has not promoted the internal helpers.

The controlling default from the active sequence lock remains:

```text
default_to_no_authorization_when_canon_is_ambiguous
```

Phase 1283 therefore records no public activation:

```text
public_claimability_activation_requires_explicit_human_authorization_phase_1283
public_claimability_activation_not_authorized_by_default_phase_1283
wallet_withdrawal_transfer_spend_still_blocked_phase_1283
```

---

## 2. Authority Disposition

Phase 1283 does not grant public claimability authority.

The exact disposition is:

```text
public_claimability_authority_verdict_phase_1283=no_activation_no_public_api
```

Implications:

- The Phase 1274 and Phase 1275 helpers remain internal phase helpers and
  retain their `PUBLIC_RC_EXCLUDE` launch-surface exclusion.
- No public or non-loopback claimability API is authorized.
- No public claim endpoint, HTTP route, socket listener, non-loopback bind, or
  public verifier service is added.
- No wallet withdrawal, transfer, spend, signing, or ledger-write authority is
  granted.
- No ECU mint, ILC settlement, withdrawal runtime, or value-transfer runtime is
  authorized.
- No source export, release artifact, release key, release envelope, Genesis
  Atlas mutation, v0.2 signing, CDL mutation, or CDL-088 opening is authorized.

The human question is carried forward rather than silently resolved in favor of
activation:

```text
claimability_human_question_escalation_required_phase_1283
```

The future activation question is:

```text
Is a narrow public claimability activation path authorized, and if so what
public verifier/API surface is permitted for the public-RC package?
```

Until that question is answered with explicit activation scope, the only
authorized next step is a verifier/API boundary preflight.

---

## 3. Phase 1284 Route

The next locked phase is:

```text
phase_1284_claimability_verifier_api_boundary_preflight_next
```

Phase 1284 must remain sensitive and must not expose a public endpoint by
default. If it introduces any helper, route scaffold, verifier shape, manifest,
or API boundary record, the default posture is internal-only and
`PUBLIC_RC_EXCLUDE` unless a later explicit public-RC allowlist review promotes
or replaces the helper.

Minimum Phase 1284 questions:

- What exact public verifier input object, if any, is acceptable?
- Which proof roots and receipts are public-safe to present?
- How is replay/double-claim prevention represented without enabling wallet
  withdrawal, transfer, or spend?
- What TransportPrincipal or equivalent identity binding is required before any
  non-loopback claimability API?
- Which helper files remain excluded from the public RC package?

---

## 4. Non-Claims

Phase 1283 does not authorize or perform:

- public claimability activation
- public claimability API activation
- public or non-loopback claimability endpoint
- public verifier service
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement or withdrawal runtime activation
- public P2P exposure
- public fetch serving
- public sidecar/projection serving
- source allowlist export execution
- public repository publication
- public package publication
- release-key generation
- release envelope production
- public release artifact production
- v0.2 signing
- Genesis Atlas mutation, regeneration, or signing
- CDL mutation
- CDL-088 opening
- public RC claim
- public launch claim
- IP filing
- paper publication
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1283:

```text
public_rc_remains_blocked_after_phase_1283
```

Remaining blocker classes include public claimability verifier/API boundary,
TransportPrincipal public-path activation, sidecar public projection/privacy
serving, release publication and v0.2 signing authorization, counsel/IP/public
release authority, source allowlist export execution, release artifact
production, release keys/envelopes, Genesis Atlas signing, CDL-088, ECU
minting, ILC settlement, and wallet withdrawal/transfer/spend semantics.

---

## 5. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_tests_added:tests/test_phase_1283_public_claimability_authority_decision_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1283_public_claimability_authority_decision_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
```
