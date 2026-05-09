# ILC Public Claimability Verifier/API Boundary Preflight 1284 v0.1

Status: boundary preflight recorded / no public API
Date: 2026-05-09
Phase: 1284
Owner lane: G8 public-RC economic boundary

Required tokens:

```text
public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1
claimability_api_public_serving_not_enabled_phase_1284
claimability_verifier_authority_not_activated_phase_1284
wallet_withdrawal_transfer_spend_still_blocked_phase_1284
public_rc_exclude_internal_helper_required_phase_1284
```

Additional carry-forward tokens:

```text
public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api
phase_1285_transport_principal_public_path_activation_preflight_next
public_rc_remains_blocked_after_phase_1284
```

Verdict:

```text
public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api
```

Phase 1284 was executed after explicit human authorization:

```text
GO Phase 1284
```

That authorization is authority to perform this sensitive verifier/API boundary
preflight. It is not authority to expose a public verifier, expose a public or
non-loopback claimability API, enable public claimability, enable wallet
withdrawal, enable wallet transfer, enable wallet spend, grant wallet signing
authority, grant wallet ledger-write authority, mint ECU, settle ILC, publish
source, produce release artifacts, mutate Genesis Atlas, sign v0.2, mutate a
CDL row, open CDL-088, or make a public-RC claim.

---

## 0. Discovery Discipline

Phase 1284 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| §0a Known-token audit | Verified the Phase 1284 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1284_g8_public_claimability_verifier_api_boundary_preflight.md` and carried them into this packet, the walkthrough, STATUS, PLANNING_INDEX, Roadmap v1.1, and Capsule v5.51. |
| §0b Concept-discovery search | Searched claimability API, verifier, claim endpoint, public endpoint, non-loopback, wallet, withdrawal, transfer, spend, `PUBLIC_RC_EXCLUDE`, public-source allowlist, and release material. |
| §0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, local-only, no public, no listener, no spend, no ECU minting, no ILC settlement, public API, and endpoint terms. |
| §0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source granted public verifier/API authority. The newly carried tokens are `public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api`, `phase_1285_transport_principal_public_path_activation_preflight_next`, and `public_rc_remains_blocked_after_phase_1284`. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.51.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md`
- `docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md`
- `docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md`
- `docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md`
- `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md`
- `ilc_core/ledger/claimability_proof_binding_runtime.py`
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Boundary Decision

Phase 1284 records a verifier/API boundary only:

```text
claimability_api_public_serving_not_enabled_phase_1284
claimability_verifier_authority_not_activated_phase_1284
```

No public verifier service is authorized. No public claim endpoint, HTTP route,
FastAPI router, socket listener, non-loopback bind, wildcard bind, public host
bind, peer-discovery surface, public sidecar/projection serving path, wallet
write path, withdrawal endpoint, transfer endpoint, spend endpoint, ECU mint
endpoint, or ILC settlement endpoint is added.

No wallet write path is authorized.
No ECU mint endpoint is authorized.
No ILC settlement endpoint is authorized.

No new runtime helper was introduced in this phase. This was deliberate: adding
an API scaffold before public verifier authority exists would increase the
public-RC attack surface without closing the authority gap. The existing Phase
1274 and Phase 1275 helpers remain the local verifier substrates and retain
their public-RC exclusion markers.

The controlling boundary is:

```text
public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api
```

## 2. Permitted Current Surface

The only permitted current claimability surface is internal/offline verification
of the existing local proof-binding material:

- Phase 1274 conversion-sweeper receipt semantics.
- Phase 1275 claimability proof binding.
- Phase 1282 Fix1 forged-receipt, root-domain, Decimal-boundary, and exclusion
  hardening.
- Phase 1283 authority disposition: no activation and no public API.

The boundary object for any future public verifier must, at minimum, be derived
from the Phase 1275 proof-binding payload and preserve:

- `public_claimability_activated=false`
- `non_loopback_claimability_api_enabled=false`
- `wallet_withdrawal_enabled=false`
- `wallet_transfer_enabled=false`
- `wallet_spend_enabled=false`
- `ecu_mint_authorized=false`
- `ilc_settlement_authorized=false`
- `transport_principal_required_before_non_loopback=true`

This phase does not declare the full Phase 1275 payload public-safe. Field-level
public disclosure, privacy filtering, nullifier/claim-registry semantics,
TransportPrincipal binding, replay prevention for submitted public claims, and
release allowlist promotion remain separate gates.

Field-level public disclosure, privacy filtering, nullifier/claim-registry
semantics, TransportPrincipal binding, replay prevention for submitted public
claims, release allowlist promotion, and the fact that local conversion-key
replay checks are not sufficient for public claim submission semantics remain
open future public-presentation preconditions.

## 3. `PUBLIC_RC_EXCLUDE` Boundary

The current local helpers are not public RC launch surfaces:

```text
PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface
```

This phase records:

```text
public_rc_exclude_internal_helper_required_phase_1284
```

The marker applies to the existing local claimability helpers until a later
explicit public-RC allowlist review promotes or replaces them:

- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
- `ilc_core/ledger/claimability_proof_binding_runtime.py`

Phase 1255 source allowlist rules already exclude header-marked internal
helpers by default. Phase 1284 does not remove, relax, or supersede that rule.
Phase 1255 source allowlist rules already exclude header-marked internal helpers.

## 4. Activation Preconditions Carried Forward

A future public claimability verifier/API activation still needs all of the
following before it can be treated as public-RC eligible:

| Gate | Current Phase 1284 disposition |
|------|--------------------------------|
| Explicit public verifier/API authority | Not activated by Phase 1284. |
| Public-safe claim presentation schema | Not defined as public-safe by Phase 1284. |
| Replay/double-claim prevention for public submissions | Not closed by Phase 1284; existing local conversion-key replay checks are necessary but not sufficient for public claim submission semantics. |
| TransportPrincipal or equivalent identity binding before non-loopback API | Required before any non-loopback claimability API. |
| Public endpoint implementation and hostile-network hardening | Not authorized by Phase 1284. |
| Release allowlist promotion of internal helpers | Not authorized by Phase 1284. |
| Wallet withdrawal, transfer, spend, signing, or ledger-write authority | Still blocked. |
| ECU minting and ILC settlement | Still unauthorized. |

Wallet authority remains blocked:

```text
wallet_withdrawal_transfer_spend_still_blocked_phase_1284
```

The next locked phase is:

```text
phase_1285_transport_principal_public_path_activation_preflight_next
```

Phase 1285 is sensitive and requires explicit `GO Phase 1285`.

## 5. Non-Claims

Phase 1284 does not authorize or perform:

- public claimability activation
- public claimability API activation
- public or non-loopback claimability endpoint
- public verifier service
- public claim endpoint
- HTTP route, FastAPI route, socket listener, non-loopback bind, wildcard bind,
  public host bind, or peer-discovery surface
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

Public RC remains blocked after Phase 1284:

```text
public_rc_remains_blocked_after_phase_1284
```

Remaining blocker classes include TransportPrincipal public-path activation,
sidecar public projection/privacy serving, release publication and v0.2 signing
authorization, counsel/IP/public release authority, source allowlist export
execution, release artifact production, release keys/envelopes, Genesis Atlas
signing, CDL-088, ECU minting, ILC settlement, and wallet
withdrawal/transfer/spend semantics.

---

## 6. Graph Delta

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_public_claimability_verifier_api_boundary_preflight_1284_v0.1.md -> ecu/ilc/public_rc
graph_delta=support_tests_added:tests/test_phase_1284_public_claimability_verifier_api_boundary_preflight.py -> validation
graph_delta=support_only:docs/phases/phase_1284_public_claimability_verifier_api_boundary_preflight_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier
```
