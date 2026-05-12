# ILC Deep No-Activation Assertion Audit 1301 v0.1

Status: audit pass with blockers recorded / no new activation authority
Date: 2026-05-11
Phase: 1301
Owner lane: G8 public-RC no-activation gate

Required tokens:

```text
deep_no_activation_assertion_audit_phase_1301.v0.1
no_activation_audit_verdict_phase_1301=pass_or_blockers_recorded
public_endpoint_activation_absent_or_blocked_phase_1301
release_artifact_activation_absent_or_blocked_phase_1301
genesis_signing_activation_absent_or_blocked_phase_1301
wallet_ecu_ilc_activation_absent_or_blocked_phase_1301
public_rc_remains_blocked_after_phase_1301
phase_1302_window_1289_1302_closure_gate_next
```

Discovery tokens recorded by this audit:

```text
legacy_public_labeled_fastapi_routes_carry_forward_phase_1301
legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301
public_p2p_fetch_sidecar_activation_absent_or_blocked_phase_1301
public_rc_exclude_helpers_still_internal_phase_1301
source_export_publication_activation_absent_or_blocked_phase_1301
cdl_mutation_cdl088_activation_absent_phase_1301
phase_1302_requires_explicit_go_phase_1301
```

Verdict:

```text
no_activation_audit_verdict_phase_1301=pass_or_blockers_recorded
```

Phase 1301 was executed after explicit human authorization:

```text
GO Phase 1301
```

The authorization grants only a deep no-activation assertion audit. It does not
authorize public RC, source export, source publication, package publication,
release artifact production, release keys, release envelopes, Genesis Atlas
mutation/regeneration/signing, v0.2 signing, public claimability activation,
public verifier/API serving, public P2P/fetch/sidecar serving, CDL mutation,
CDL-088 opening, wallet withdrawal/transfer/spend semantics, ECU minting, or
ILC settlement.

---

## 0. Discovery Discipline

Phase 1301 used exact-token search only as a schema and completion check.
Exact-token `rg` found the required Phase 1301 tokens only in the Phase 1301
prompt before this packet was written. Broader concept discovery and direct
source reads were used before the audit verdict was recorded.

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Verified the Phase 1301 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md` and carried them into this packet, tests, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.52, and Roadmap v1.1. |
| Section 0b Concept-discovery search | Searched listener, bind, public endpoint, public serving, public P2P, public fetch, public sidecar, claimability API, verifier service, source export, release artifact, release key, envelope, Genesis, v0.2, wallet, ECU, ILC, CDL, CDL-088, `PUBLIC_RC_EXCLUDE`, package profile, sidecar projection, TransportPrincipal, and local skill preview terms. |
| Section 0c Contradiction and non-claim search | Searched enabled, activated, published, produced, generated, signed, mutated, opened, not authorized, blocked, local-only, no public, and public RC remains blocked terms. |
| Section 0d Source expansion and newly discovered tokens | Direct-read the runtime and planning hits listed below. The audit discovered legacy public-labeled FastAPI routes in `ilc_core/server.py`; they are recorded as carry-forward blockers for clean public RC packaging, not as public-RC activation authority. |

Direct-read planning sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md`
- `docs/specs/ilc_public_claimability_verifier_contract_preflight_1291_v0.1.md`
- `docs/specs/ilc_claimability_package_profile_allowlist_rehearsal_1292_v0.1.md`
- `docs/specs/ilc_public_rc_exclude_helper_promotion_removal_register_1293_v0.1.md`
- `docs/specs/ilc_claimability_package_allowlist_rehearsal_1294_v0.1.md`
- `docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md`
- `docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md`
- `docs/specs/ilc_sidecar_public_safe_projection_schema_1297_v0.1.md`
- `docs/specs/ilc_sidecar_bind_listener_peer_discovery_authority_preflight_1298_v0.1.md`
- `docs/specs/ilc_release_allowlist_artifact_genesis_readiness_preflight_1299_v0.1.md`
- `docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md`
- `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md`

Direct-read runtime sources:

- `ilc_core/asgi.py`
- `ilc_core/server.py`
- `ilc_core/graph/sidecar_query_runtime.py`
- `ilc_core/graph/sidecar_public_path_preflight.py`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
- `ilc_core/network/d2d/http_fetch_transport_runtime.py`
- `ilc_core/network/d2d/http_gossip_transport_runtime.py`
- `ilc_core/network/d2d/gossip_transport.py`
- `ilc_core/network/d2d/truth_primitive_fetch_runtime.py`
- `ilc_core/network/d2d/truth_primitive_gossip_runtime.py`
- `ilc_core/ledger/cdl048_conversion_sweeper_runtime.py`
- `ilc_core/ledger/claimability_proof_binding_runtime.py`
- `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py`
- `ilc_core/protocol/public_wallet_runtime.py`
- `ilc_core/protocol/public_receipt_runtime.py`
- `ilc_core/rc/local_skill_preview.py`
- `ilc_core/rc/package_profiles.py`
- `ilc_core/rc/package_profile_ci_gate.py`
- `ilc_core/rc/atlas_graph_discipline.py`
- `tools/check_sensitive_runtime_coding_taboos.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Activation Audit Matrix

| Surface | Source evidence | Phase 1301 disposition | Carry-forward blocker |
|---------|-----------------|------------------------|-----------------------|
| Legacy FastAPI route surface | `ilc_core/asgi.py` exposes `app = create_app()`. `ilc_core/server.py` includes `/mine`, `/gossip/receive`, `/peers/add`, `/v1/protocol/*`, and `/v1/public/*` route definitions. | Public endpoint activation is not cleanly absent; it is blocked for public RC. Token: `public_endpoint_activation_absent_or_blocked_phase_1301`. | `legacy_public_labeled_fastapi_routes_carry_forward_phase_1301`: public-RC packaging must exclude, replace, or explicitly gate these routes before any public source/package claim. |
| Public claimability verifier/API | Phase 1291 defines the contract only. `ilc_core/ledger/claimability_proof_binding_runtime.py` remains `PUBLIC_RC_EXCLUDE` and states it does not expose a public API, wallet write path, mint path, spend path, transfer path, withdrawal path, or settlement path. | Blocked. No public verifier service or claim endpoint is activated. | Final public claimability verifier/API authority and clean implementation remain open. |
| Package profile and OpenClaw/NemoClaw claimable profile | `ilc_core/rc/package_profiles.py` declares profile targets; `ilc_core/rc/package_profile_ci_gate.py` records `public_claimability_runtime_activated: False`, `public_rc_claimed: False`, and `public_repository_publication: False`. | Declaration exists, activation absent. | Clean materialized package export and helper replacement/stripping remain open. |
| `PUBLIC_RC_EXCLUDE` helpers | Sidecar public-path, TransportPrincipal public-path, CDL-048 conversion sweeper, and claimability proof-binding helpers remain marked `PUBLIC_RC_EXCLUDE`. | Helpers remain internal. Token: `public_rc_exclude_helpers_still_internal_phase_1301`. | Phase 1308/1319/1333 materialization gates must replace, strip, or defer them. |
| Sidecar query and projection serving | `ilc_core/graph/sidecar_query_runtime.py` is local/read-only and bounded. `ilc_core/graph/sidecar_public_path_preflight.py` says it does not open a listener, bind socket, serve projection data, or enable peer discovery. | Public sidecar/projection serving blocked. | Privacy filter implementation, bind/listener/peer-discovery authority, and public-safe serving implementation remain open. |
| Public P2P and fetch | TransportPrincipal helper rejects public P2P/fetch and remains `PUBLIC_RC_EXCLUDE`. `truth_primitive_gossip_runtime.py` is outbound-only and starts no server. HTTP fetch/gossip runtimes contain explicit `start()` listener code, but the window did not activate public serving or public RC deployment. | Public P2P/fetch activation absent or blocked. Token: `public_p2p_fetch_sidecar_activation_absent_or_blocked_phase_1301`. | Rust/public transport integration, hostile-network controls, and public serving authority remain open. |
| Source export and publication | Phase 1299 and Phase 1300 record source allowlist export, repository publication, and package publication as not executed/not authorized. | Blocked. Token: `source_export_publication_activation_absent_or_blocked_phase_1301`. | Clean materialized public tree, counsel/IP/publication clearance, and export execution gate remain open. |
| Release artifacts, keys, envelopes | Phase 1299 records no artifact, no manifest instance, no keys, and no envelope. | Blocked. Token: `release_artifact_activation_absent_or_blocked_phase_1301`. | Release dry run and final production/key/envelope gates remain open. |
| Genesis Atlas and v0.2 signing | `ilc_core/rc/atlas_graph_discipline.py` includes non-authorization boundaries. Phase 1299 records Genesis Atlas not mutated/signed and v0.2 signing not authorized. | Blocked. Token: `genesis_signing_activation_absent_or_blocked_phase_1301`. | ATLAS-G tail, signing-root envelope, and explicit signing ceremony authority remain open. |
| Wallet, ECU, ILC economics | `public_wallet_runtime.py` exposes read/status/export-style surfaces only. `ecu_ilc_lifecycle_runtime.py` records `claimability_state: deferred`; `commit_settled_epoch` is internal wallet-store update machinery, not public withdrawal/transfer/spend authority. CDL-048 and claimability proof-binding force wallet withdrawal/transfer/spend, ECU mint, and ILC settlement flags to false. | Blocked. Token: `wallet_ecu_ilc_activation_absent_or_blocked_phase_1301`. | Wallet withdrawal/transfer/spend semantics, wallet signing authority, ECU minting, and ILC settlement remain open. |
| CDL mutation and CDL-088 | CDL-087 is ratified; CDL-088 remains unopened. Phase 1301 does not mutate the CDL register. | Absent. Token: `cdl_mutation_cdl088_activation_absent_phase_1301`. | Phase 1302 closure may classify blockers only; any future CDL mutation requires explicit authority. |

---

## 2. Key Finding: Legacy Public-Labeled Routes

Phase 1301 cannot honestly state that no public-labeled endpoint code exists in
the repository. `ilc_core/server.py` already contains route definitions whose
names include public-facing concepts, including `/v1/public/init/admission`,
`/v1/public/receipt`, `/v1/public/receipts`, `/v1/public/lifecycle/*`, and
`/v1/public/wallet/*`.

The correct no-activation assertion is narrower and safer:

```text
legacy_public_labeled_fastapi_routes_carry_forward_phase_1301
legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301
```

Those routes are not evidence that Phase 1289-1301 executed a public RC, source
export, package publication, release artifact, Genesis signing, v0.2 signing,
CDL mutation, or wallet/ECU/ILC activation. They are evidence that any future
public-RC materialized tree must explicitly exclude, replace, or gate the legacy
FastAPI server surface before a public package or public endpoint claim is
valid.

This is consistent with the architecture gate: public RC packages must come from
a clean materialized public tree, not from flipping private fail-closed flags.

---

## 3. No-Activation Boundary

Phase 1301 records:

```text
public_endpoint_activation_absent_or_blocked_phase_1301
release_artifact_activation_absent_or_blocked_phase_1301
genesis_signing_activation_absent_or_blocked_phase_1301
wallet_ecu_ilc_activation_absent_or_blocked_phase_1301
public_rc_remains_blocked_after_phase_1301
```

No source allowlist export execution, materialized export manifest production,
public repository publication, public package publication, release artifact
production, release artifact manifest instance production, release-key
generation, release envelope production, release signing material generation,
public RC claim, public launch claim, public claimability activation, public
verifier service activation, public claim endpoint activation, public P2P
exposure, public fetch serving activation, public sidecar/projection serving,
non-loopback sidecar bind, wildcard bind, public host bind, public listener,
peer discovery, TransportPrincipal public-path activation, credential lifecycle
policy activation, public revocation registry activation, public replay cache
activation, admission policy activation, ban registry activation, public
rate-limit state activation, privacy policy activation, helper promotion,
marker removal, helper stripping, CDL mutation, CDL-088 opening, Genesis Atlas
mutation, Genesis Atlas regeneration, Genesis Atlas signing, v0.2 signing, IP
filing, paper publication, wallet withdrawal, wallet transfer, wallet spend,
wallet signing authority, wallet ledger-write authority, ECU minting, ILC
settlement, immutable diagnostic mutation, or production `commit.epoch`
emission authorization occurred in this phase.

Exact non-claim phrase guard:

```text
source allowlist export execution
materialized export manifest production
public repository publication
public package publication
release artifact production
release artifact manifest instance production
release-key generation
release envelope production
release signing material generation
public RC claim
public launch claim
public claimability activation
public verifier service activation
public claim endpoint activation
public P2P exposure
public fetch serving activation
public sidecar/projection serving
non-loopback sidecar bind
wildcard bind
public host bind
public listener
peer discovery
TransportPrincipal public-path activation
credential lifecycle policy activation
public revocation registry activation
public replay cache activation
admission policy activation
ban registry activation
public rate-limit state activation
privacy policy activation
helper promotion
marker removal
helper stripping
CDL mutation
CDL-088 opening
Genesis Atlas mutation
Genesis Atlas regeneration
Genesis Atlas signing
v0.2 signing
IP filing
paper publication
wallet withdrawal
wallet transfer
wallet spend
wallet signing authority
wallet ledger-write authority
ECU minting
ILC settlement
```

---

## 4. Residual Blockers

Public RC remains blocked after Phase 1301 by:

- Legacy public-labeled FastAPI routes in `ilc_core/server.py` that must be
  excluded, replaced, or explicitly gated before any clean public-RC package or
  public endpoint claim.
- Final public claimability verifier/API authority and public endpoint
  implementation.
- `PUBLIC_RC_EXCLUDE` helper replacement, stripping, or deferral through clean
  materialized package gates.
- Public-safe privacy filter implementation/review, replay/nullifier policy,
  and duplicate-claim registry policy.
- TransportPrincipal public-path activation authority, including
  post-ratification CDL-087 helper replacement, lifecycle policy, revocation
  registry, replay cache, admission, ban, rate-limit, and privacy controls.
- Sidecar public projection serving authority, including public-safe field
  serving, bind/listener policy, and peer-discovery policy.
- Counsel-approved license, CLA, trademark, IP, and publication clearance.
- Source allowlist export execution and public source/package publication.
- Release artifact production, release-key generation, release envelope
  production, and release manifest instance production.
- Genesis Atlas mutation/regeneration/signing if needed and explicit v0.2
  signing authorization.
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy.
- Wallet withdrawal/transfer/spend semantics, wallet signing authority, wallet
  ledger-write authority, ECU minting, ILC settlement, and withdrawal runtime
  activation.

---

## 5. Next Phase

The next locked phase is:

```text
phase_1302_window_1289_1302_closure_gate_next
```

Phase 1302 is sensitive and requires explicit `GO Phase 1302`.

Carry-forward token:

```text
phase_1302_requires_explicit_go_phase_1301
```

---

## 6. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md -> release/publication
graph_delta=support_tests_added:tests/test_phase_1301_deep_no_activation_assertion_audit.py -> validation
graph_delta=support_only:docs/phases/phase_1301_deep_no_activation_assertion_audit_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

---

## 7. Verification

Verification commands:

```text
.venv/bin/python -m pytest tests/test_phase_1301_deep_no_activation_assertion_audit.py tests/test_window_1289_1302_prompt_drafts.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1301_deep_no_activation_assertion_audit_walkthrough.md docs/specs/ilc_antigravity_context_capsule_v5.52.md docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md tests/test_phase_1301_deep_no_activation_assertion_audit.py
```

Results:

```text
.venv/bin/python -m pytest tests/test_phase_1301_deep_no_activation_assertion_audit.py tests/test_window_1289_1302_prompt_drafts.py
21 passed
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
PASS: sensitive runtime coding taboos
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
clean
git diff --check -- docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1301_deep_no_activation_assertion_audit_walkthrough.md docs/specs/ilc_antigravity_context_capsule_v5.52.md docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md tests/test_phase_1301_deep_no_activation_assertion_audit.py
clean
```
