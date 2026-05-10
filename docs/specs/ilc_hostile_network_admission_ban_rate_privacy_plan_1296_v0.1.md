# ILC Hostile-Network Admission Ban Rate Privacy Plan 1296 v0.1

**Phase:** 1296
**Date:** 2026-05-10
**Status:** hostile-network plan recorded; no activation
**Window lock:** `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`

```text
hostile_network_admission_ban_rate_privacy_plan_phase_1296.v0.1
hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation
transport_principal_admission_policy_not_activated_phase_1296
transport_principal_ban_registry_not_activated_phase_1296
transport_principal_rate_limit_state_not_activated_phase_1296
transport_principal_privacy_policy_not_activated_phase_1296
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
werner_overlay_not_activated_phase_1296
public_p2p_not_activated_phase_1296
public_fetch_serving_not_enabled_phase_1296
public_sidecar_projection_serving_not_enabled_phase_1296
public_rc_remains_blocked_after_phase_1296
phase_1297_sidecar_public_safe_projection_schema_next
```

## 1. Verdict

Phase 1296 executes after explicit human authorization:

```text
GO Phase 1296
```

The active 1289-1302 sequence lock controls this phase. Phase 1296 records a
hostile-network admission, ban, rate-limit, and privacy plan only. It does not
activate a public TransportPrincipal path, public P2P, public fetch serving,
public sidecar/projection serving, or any wallet/ECU/ILC economic surface.

```text
hostile_network_plan_verdict_phase_1296=plan_recorded_no_activation
```

This phase closes a planning gap, not an activation gap. The current
TransportPrincipal helpers remain internal, fail-closed, and `PUBLIC_RC_EXCLUDE`.
The Phase 1277 helper is still not directly promotable because CDL-087 is now ratified while the helper still carries the old pre-ratification false gate.

## 2. Section 0 Discovery Results

| Section | Result |
|---------|--------|
| Section 0a Known-token audit | Verified Phase 1296 authority against `docs/PLANNING_INDEX.md`, Capsule v5.52, STATUS, the 1289-1302 lock/guidance, Phase 1295 lifecycle/revocation/replay preflight, Phase 1285 public-path activation preflight, the transport/value forward plan, current TransportPrincipal helper code, and the CDL register. |
| Section 0b Concept-discovery search | Searched hostile-network, admission, ban, local-ban, rate-limit, limiter, privacy, correlation, AgentID, client_ip, requester_id, TransportPrincipal, principal, public path, public P2P, public fetch, sidecar projection, Werner, topology pressure, flow governor, and CDL-088 concepts. |
| Section 0c Contradiction and non-claim search | Searched blocked, deferred, not authorized, not activated, not enabled, local-only, devnet, no public, no listener, no bind, no public P2P, no public fetch, no helper promotion, no marker removal, no wallet spend, no ECU minting, no ILC settlement, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Source expansion confirmed that Phase 1296 must preserve the Phase 1295 stale-helper blocker, keep `requester_id`/`client_ip`/`AgentID` fallback forbidden, and route Werner topology pressure only to future evidence or admission-budget policy after separate authorization. |

Direct-read basis:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
- `docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md`
- `docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md`
- `docs/specs/ilc_window_1257_1264_handoff_1264_v0.1.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `ilc_core/network/d2d/transport_principal_pre_public_path.py`
- `ilc_core/network/d2d/transport_principal_public_path_preflight.py`
- `tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py`
- `tests/test_phase_1295_transport_principal_lifecycle_revocation_replay_preflight.py`

## 3. Current Runtime Readback

The Phase 1267 TransportPrincipal helper already derives authenticated
TransportPrincipal keys:

| Key | Current shape | Phase 1296 disposition |
|-----|---------------|------------------------|
| Admission key | `tp_admission:<sha256>` | Future admission policy input only; no admission service is activated. |
| Ban key | `tp_ban:<sha256>` | Future ban-registry input only; no ban registry is activated. |
| Rate-limit key | `tp_rate:<sha256>` | Future limiter input only; no public rate-limit state is activated. |
| Replay key | `tp_replay:<sha256>` | Future replay cache input only; Phase 1295 already records replay cache not activated. |

The helper rejects `requester_id`, JSON body requester identity, `client_ip`,
`AgentID`, agent id, harness identity, and disguised fallback material. Phase
1296 keeps that rule as a launch invariant:

```text
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
```

The Phase 1277 public-path helper remains an internal preflight scaffold. It
does not open sockets, bind listeners, serve public fetch, serve public
sidecar/projection, or activate public P2P. It remains `PUBLIC_RC_EXCLUDE` and
not directly promotable after Phase 1295.

## 4. Future Admission Policy Contract

Future public-path admission must be keyed only by authenticated TransportPrincipal material. The minimum future contract is:

- Input: validated post-CDL-087 TransportPrincipal public-path envelope.
- Authority: explicit public-path activation authorization and public credential
  issuer authority.
- Deny if credential kind is unsupported, missing, stale, expired, revoked,
  replayed, banned, privacy-incompatible, outside an epoch window, or not bound
  to a permitted public-path issuer.
- Deny if public P2P, public fetch, public sidecar/projection, release,
  claimability, wallet, ECU, or ILC flags are false but the request asks for
  those surfaces.
- Deny if state dependencies are unavailable and cannot fail closed.
- Never fall back to `requester_id`, JSON body identity, `client_ip`,
  `AgentID`, agent id, harness identity, OpenClaw identity, or Tailscale
  identity as the admission key.

Phase 1296 does not activate this policy:

```text
transport_principal_admission_policy_not_activated_phase_1296
```

Phrase guard: future controls require bounded state, epoch/sequence validity,
and fail-closed behavior before activation.

## 5. Future Ban Registry Contract

Future ban state must be a bounded, authenticated, epoch/sequence-scoped policy
surface. The minimum future contract is:

- Ban subject: authenticated `tp_ban:<sha256>` material, never IP or AgentID.
- Ban record: canonical JSON with deterministic key ordering and `allow_nan=False`.
- Authority: explicit issuer/signature policy for local ban, federated ban, and
  emergency ban classes.
- Duration: epoch/sequence validity, not wall-clock protocol time.
- Propagation: bounded update size, bounded registry cardinality, replay-safe
  ingestion, and fail-closed unavailable-registry behavior.
- Removal: explicit appeal/removal/sunset path to avoid permanent accidental
  exclusion from a rotating-principal system.
- Privacy: ban records must not reveal permanent AgentID, stake, wallet,
  economic position, or private graph position by default.

Phase 1296 does not activate this registry:

```text
transport_principal_ban_registry_not_activated_phase_1296
```

## 6. Future Rate-Limit State Contract

Future rate limiting must be hostile-network safe before any public path is
claimed. The minimum future contract is:

- Limiter key: authenticated `tp_rate:<sha256>` only.
- Windowing: epoch/sequence counters for protocol policy, not OS wall clock.
- Bounds: maximum principals, buckets, in-flight requests, pending envelopes,
  and registry update items.
- Overflow behavior: deterministic fail-closed rejection, not unbounded memory
  accumulation.
- State loss: explicit cold-start and cross-instance consistency policy.
- Abuse profile: invalid envelopes, replay storms, credential churn,
  high-cardinality principal creation, slowloris-style request bodies, and
  retry amplification must have test coverage before activation.
- Compatibility: static 429-style limits can be fallback abuse controls, but
  not a substitute for authenticated TransportPrincipal admission.

Phase 1296 does not activate this state:

```text
transport_principal_rate_limit_state_not_activated_phase_1296
```

## 7. Future Privacy Policy Contract

Future privacy mode must preserve the key ladder:

- AgentID is a permanent epistemic identity and must not become the default
  transport handle.
- TransportPrincipal should be short-lived or rotating.
- Passive observers must not learn stake, wallet balance, economic position, or
  graph position from the transport credential alone.
- Public-safe sidecar projection must be field-filtered before any public
  serving path exists.
- Rate-limit, ban, and admission records must minimize correlation across
  epochs unless a later governance decision explicitly authorizes stronger
  linkability.

Phase 1296 does not activate this policy:

```text
transport_principal_privacy_policy_not_activated_phase_1296
```

## 8. Werner Interaction Boundary

The transport/value forward plan says Werner topology pressure should prefer
organic control first: routing reputation, routing weight, admission budget,
cache/mirror priority, and work allocation before any ECU creation. Phase 1296
therefore records Werner as a future possible admission-budget signal, not an
active runtime control:

```text
werner_overlay_not_activated_phase_1296
```

No Werner CDL is opened here. No direct Werner ECU creation, heat-based ECU
minting, credit advance, or settlement mutation is authorized.

## 9. Hostile-Network Validation Matrix

Future activation must add deterministic tests or simulation evidence for:

| Attack surface | Required future proof |
|----------------|-----------------------|
| Missing credential | Fail closed before admission, ban, or rate-limit state mutates. |
| Fallback identity injection | Reject `requester_id`, `client_ip`, `AgentID`, agent id, and harness identity. |
| Expired or future credential | Reject using epoch/sequence checks. |
| Revoked principal | Reject from authenticated bounded registry state. |
| Replay storm | Reject from bounded replay/nullifier state. |
| Ban evasion by rotation | Preserve privacy while limiting cheap churn. |
| High-cardinality spam | Bound principal/bucket creation and fail closed on overflow. |
| Slow request bodies | Bound untrusted payload size and stream processing. |
| Privacy correlation | Prove no default AgentID/stake/wallet leakage. |
| Werner pressure misuse | Prove topology pressure cannot mint ECU or silently widen admission authority. |

## 10. Carry-Forward

Public RC remains blocked after Phase 1296 by:

- final public claimability verifier/API authority and public endpoint
  authorization;
- public-safe helper replacement or later explicit helper promotion
  prerequisites;
- public-safe disclosure schema, privacy filtering, replay/nullifier policy,
  and duplicate-claim registry;
- TransportPrincipal public-path activation authority, including the
  post-ratification CDL-087 helper replacement, lifecycle policy, revocation
  registry, replay cache, admission policy, ban registry, rate-limit state, and
  privacy policy;
- actual public sidecar/projection serving authority, including public-safe
  field schema, filtering, bind/listener policy, and peer-discovery policy;
- counsel/license/CLA/trademark/IP/publication clearance;
- source allowlist export execution and public source/package publication;
- release artifact production, release-key generation, release envelope
  production, and release manifest instance production;
- Genesis Atlas mutation/regeneration/signing if needed and v0.2 signing
  authorization;
- CDL-088 opening or any reciprocal scoring/ECU-escrow admission policy;
- wallet withdrawal/transfer/spend semantics, wallet signing authority,
  wallet ledger-write authority, ECU minting, ILC settlement, and withdrawal
  runtime activation.

The next locked phase remains sensitive:

```text
phase_1297_sidecar_public_safe_projection_schema_next
```

## 11. Non-Claims

```text
transport_principal_admission_policy_not_activated_phase_1296
transport_principal_ban_registry_not_activated_phase_1296
transport_principal_rate_limit_state_not_activated_phase_1296
transport_principal_privacy_policy_not_activated_phase_1296
requester_id_client_ip_agentid_fallback_still_forbidden_phase_1296
werner_overlay_not_activated_phase_1296
public_p2p_not_activated_phase_1296
public_fetch_serving_not_enabled_phase_1296
public_sidecar_projection_serving_not_enabled_phase_1296
public_rc_remains_blocked_after_phase_1296
```

Phase 1296 does not authorize:

- TransportPrincipal public-path activation;
- admission policy activation;
- ban registry activation;
- public rate-limit state activation;
- privacy policy activation;
- Werner overlay activation;
- public credential issuer authority;
- public revocation registry activation;
- public replay cache activation;
- public P2P exposure;
- public fetch serving;
- public sidecar/projection serving;
- non-loopback bind, wildcard bind, public host bind, listener, or peer discovery;
- helper promotion;
- `PUBLIC_RC_EXCLUDE` marker removal;
- materialized export manifest production;
- source allowlist export execution;
- public repository publication;
- public package publication;
- public release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- public launch claim;
- public claimability runtime activation;
- public claimability API activation;
- public verifier service;
- public claim endpoint;
- wallet withdrawal, wallet transfer, or wallet spend;
- wallet signing authority or wallet ledger-write authority;
- ECU minting;
- ILC settlement or withdrawal runtime activation;
- CDL mutation;
- CDL-088 opening;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- IP filing or paper publication.

## 12. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md -> transport/identity
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1289_g8_window_1289_1302_sequence_lock.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1296_g8_hostile_network_admission_ban_rate_privacy_plan.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1297_g8_sidecar_public_safe_projection_schema.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1298_g8_sidecar_bind_listener_peer_discovery_authority_preflight.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1299_g8_release_allowlist_artifact_genesis_readiness_preflight.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1300_g8_counsel_ip_publication_clearance_inventory.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md -> planning/prompts
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1302_g8_window_1289_1302_closure_gate.md -> planning/prompts
graph_delta=support_tests_added:tests/test_phase_1296_hostile_network_admission_ban_rate_privacy_plan.py -> validation
graph_delta=support_tests_changed:tests/test_window_1289_1302_prompt_drafts.py -> validation/frontier
graph_delta=support_only:docs/phases/phase_1296_hostile_network_admission_ban_rate_privacy_plan_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
