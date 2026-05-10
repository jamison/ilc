# ILC Sidecar Public-Safe Projection Schema 1297 v0.1

Status: schema recorded / no serving
Date: 2026-05-10
Phase: 1297
Owner lane: G8 public-RC sidecar projection boundary

Required tokens:

```text
sidecar_public_safe_projection_schema_phase_1297.v0.1
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
privacy_filtering_contract_recorded_phase_1297
sidecar_public_projection_fields_not_served_phase_1297
public_sidecar_projection_serving_not_enabled_phase_1297
public_rc_remains_blocked_after_phase_1297
phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next
```

Verdict:

```text
sidecar_public_safe_projection_schema_verdict_phase_1297=schema_recorded_no_serving
```

Phase 1297 was executed after explicit human authorization:

```text
GO Phase 1297
```

The authorization grants only this public-safe projection schema packet and
privacy filtering contract. It does not authorize public sidecar/projection
serving, public projection endpoint serving, non-loopback bind, wildcard bind,
public host bind, listener, socket listener, HTTP route, peer discovery, public
P2P, public fetch serving, public claimability, public verifier service, wallet
withdrawal, wallet transfer, wallet spend, ECU minting, ILC settlement, source
allowlist export, public repository publication, public package publication,
release artifacts, release keys, release envelopes, Genesis Atlas mutation,
Genesis Atlas regeneration, Genesis Atlas signing, v0.2 signing, CDL mutation,
CDL-088 opening, public RC, public launch, IP filing, or paper publication.

---

## 0. Discovery Discipline

Phase 1297 used exact-token search only as a schema and completion check.
Exact-token `rg` was not treated as sufficient context retrieval. Boundary
analysis used direct repo reads and broader concept discovery before this
packet was written.

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Verified the Phase 1297 required tokens from `docs/antigravity_tasks/antigravity_prompt__phase_1297_g8_sidecar_public_safe_projection_schema.md` and carried them into this packet, tests, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.52, and Roadmap v1.1. |
| Section 0b Concept-discovery search | Searched sidecar projection, public-safe schema, field filtering, privacy, projection endpoint, non-loopback, listener, bind, peer discovery, AgentID, wallet, stake, graph position, public serving, and related older terms. |
| Section 0c Contradiction and non-claim search | Searched blocked, not authorized, not enabled, local-only, no public, no listener, no bind, no wallet spend, no ECU minting, no ILC settlement, and public RC remains blocked. |
| Section 0d Source expansion and newly discovered tokens | Direct-read all relevant hits listed below. No committed source grants public sidecar/projection serving authority. The newly carried schema tokens are the Phase 1297 required tokens plus the carry-forward denial boundary from Phase 1278 and Phase 1286. |

Direct-read sources:

- `docs/PLANNING_INDEX.md`
- `docs/specs/ilc_antigravity_context_capsule_v5.52.md`
- `docs/phases/STATUS.md`
- `docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md`
- `docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md`
- `docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md`
- `docs/specs/ilc_hostile_network_admission_ban_rate_privacy_plan_1296_v0.1.md`
- `ilc_core/graph/sidecar_public_path_preflight.py`
- `ilc_core/graph/sidecar_query_runtime.py`

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

---

## 1. Runtime Readback

The current runtime surfaces are local, bounded, and non-serving:

- `ilc_core/graph/sidecar_query_runtime.py` is a read-only in-process query
  runtime. It exports canonical JSON with `sort_keys=True`, `allow_nan=False`,
  and compact separators; rejects Python `float`; rejects non-finite
  `Decimal`; and enforces byte/result bounds.
- `ilc_core/graph/sidecar_public_path_preflight.py` is marked
  `PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface`.
  Its file header records no listener, bind, or serving surface.
- `sidecar_public_path_preflight.py` deliberately does not open a listener,
  bind a socket, serve projection data, or enable peer discovery.
- The Phase 1278 helper still records `sidecar_public_serving_not_enabled_phase_1278`,
  `no_new_public_listener_phase_1278`, `non_loopback_bind_not_enabled_phase_1278`,
  `public_projection_endpoint_not_enabled_phase_1278`, and
  `sidecar_projection_privacy_review_required_phase_1278`.

Phase 1297 does not change runtime code. It records the public-safe schema that
a future explicitly authorized public-serving phase would have to implement.

---

## 2. Public-Safe Projection Envelope

The future public-safe projection envelope is deny-by-default. A field is not
public unless a later activation phase explicitly allowlists it and binds it to
the privacy filter contract below.

Candidate envelope shape:

```text
PublicSafeSidecarProjectionEnvelope
  schema_version: sidecar_public_safe_projection_schema_phase_1297.v0.1
  projection_profile: explicit public-safe profile id
  projection_kind: one of aggregate_summary, proof_reference, release_manifest_reference
  projection_epoch: ratified epoch or sequence identifier, not wall-clock time
  source_artifact_root_ref: canonical digest reference, not a raw private graph
  privacy_profile: explicit deny-by-default privacy profile id
  field_policy_ref: digest or version of the field allowlist/redaction policy
  query_result_count: bounded non-negative integer
  query_result_bytes: bounded non-negative integer
  records: bounded sequence of public-safe records
  authorization_flags: all activation flags false until a later serving phase
```

Future canonicalization requirements:

- Protocol or machine-verifiable JSON must use deterministic key ordering.
- JSON used for hashing or verification must use `sort_keys=True` and
  `allow_nan=False`; compact separators are required where byte stability
  matters.
- Public numeric fields must not use Python `float`.
- Any external numeric input converted to `Decimal` must reject `NaN`,
  `Infinity`, and `-Infinity` before arithmetic or comparison.
- Protocol time must be epoch or sequence based, not wall-clock time.
- Public response construction must enforce hard maximum record count, byte
  count, and traversal depth before serialization.

---

## 3. Field Classification

Field classification is deny-by-default. Phase 1297 records the classification;
it does not serve any fields.

```text
sidecar_public_projection_fields_not_served_phase_1297
```

| Class | Field family | Phase 1297 disposition |
|-------|--------------|------------------------|
| Allow candidate | `schema_version`, `projection_profile`, `projection_kind`, `projection_epoch`, `source_artifact_root_ref`, `privacy_profile`, `field_policy_ref`, `query_result_count`, `query_result_bytes` | May become public only if a later phase authorizes serving and the field is bounded, canonical, and non-identifying. |
| Allow candidate | Aggregate counts over release-eligible artifacts | May become public only when counts cannot reveal private graph membership or private workload shape. |
| Allow candidate | Public proof or manifest digest references | May become public only when the referenced artifact is already release-eligible and source allowlist export has been explicitly authorized. |
| Redact or pseudonymize candidate | Graph node handles, edge handles, query ids, projection slice ids | Must be redacted, salted, epoch-scoped, or release-allowlisted before any public serving. Raw stable identifiers are not public. |
| Redact or pseudonymize candidate | Centrality rank, graph position, convergence trace membership, path-to-Genesis evidence | Must be removed or transformed to coarse, bounded, non-identifying aggregate form unless an explicit public artifact allowlist permits disclosure. |
| Redact or pseudonymize candidate | TransportPrincipal id, credential fingerprint, principal rate/admission/ban/replay keys | Must not be exposed raw. Any future public reference must be rotating, unlinkable, and authorized by a TransportPrincipal public-path activation phase. |
| Redact or pseudonymize candidate | Serving peer, host, listener, peer-discovery, network timing, IP, OpenClaw identity, Tailscale identity | Must not be exposed raw. Phase 1298 must decide bind/listener/peer-discovery authority before any serving. |
| Deny | AgentID, agent id, harness identity, private graph membership, private node/edge ids, raw projection records | Not public in Phase 1297. |
| Deny | Wallet root, wallet balance, balance receipt, withdrawal, transfer, spend, stake, reward, ECU, ILC, settlement, economic position | Not public in Phase 1297. No wallet/ECU/ILC semantics are authorized. |
| Deny | admission policy state, ban registry state, rate-limit state, replay cache, hostile-network scoring, abuse keys | Not public in Phase 1297. Phase 1296 recorded these as future contracts only. |
| Deny | Release keys, release envelopes, signing material, Genesis Atlas signing material, private IP/counsel/publication work product | Not public in Phase 1297. |

---

## 4. Privacy Filtering Contract

```text
privacy_filtering_contract_recorded_phase_1297
```

The privacy filter for any future public sidecar projection must enforce:

- Deny-by-default field inclusion. Unknown fields are rejected, not passed
  through.
- Explicit allowlist versioning for every public field.
- No raw AgentID, agent id, harness identity, OpenClaw identity, Tailscale
  identity, TransportPrincipal id, credential fingerprint, wallet id, stake
  id, node id, edge id, serving peer id, IP address, listener address, or peer
  discovery metadata.
- No raw wallet, stake, reward, ECU, ILC, settlement, withdrawal, transfer, or
  spend state.
- No public claimability verdicts unless a later public claimability API and
  verifier service are explicitly authorized.
- bounded response size, bounded record count, bounded traversal depth, and
  fail-closed behavior on overflow.
- Canonical JSON export for any machine-verifiable response, with deterministic
  key ordering and `allow_nan=False`.
- Exact numeric handling: no float for economic or staking state, and no
  non-finite `Decimal` at any public boundary.
- Epoch or sequence based protocol time. Wall-clock timestamps are diagnostic
  only and are not public protocol decision inputs.
- Field-decision auditability: every emitted public record must be traceable to
  an allow/redact/deny decision and policy version.
- Scraping and enumeration resistance before serving: rate-limit, ban,
  replay, and admission controls must be bound to authenticated
  TransportPrincipal material, not `requester_id`, `client_ip`, AgentID,
  OpenClaw identity, or Tailscale identity fallback.

This contract is not a server, endpoint, listener, CLI exposure, package
export, or public-RC claim.

---

## 5. Activation Preconditions Carried Forward

Future public sidecar projection serving still requires:

| Gate | Phase 1297 disposition |
|------|------------------------|
| Explicit public sidecar/projection serving authority | Not activated by Phase 1297. |
| Public-safe field schema | Recorded by Phase 1297, but not served. |
| Privacy filter implementation and review | Required before activation. |
| Sidecar bind, listener, and peer-discovery authority | Required; routed to Phase 1298. |
| TransportPrincipal public-path activation | Required before public projection serving. |
| Post-ratification CDL-087 TransportPrincipal helper replacement or explicit promotion prerequisites | Still open. |
| Admission, ban, rate-limit, replay, and privacy controls | Still future contracts only after Phase 1296. |
| Source allowlist export execution | Not executed by Phase 1297. |
| Release allowlist/artifact/key/envelope readiness | Still open. |
| Counsel, IP, and publication clearance | Still open. |

The next locked phase is:

```text
phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_next
```

Phase 1298 is sensitive and requires explicit `GO Phase 1298`.

---

## 6. Non-Claims

Phase 1297 does not authorize or perform:

- public sidecar/projection serving
- public projection endpoint serving
- non-loopback sidecar/projection serving
- non-loopback bind
- wildcard bind
- public host bind
- public listener
- socket listener
- HTTP route or public endpoint
- peer discovery
- public fetch serving
- public P2P exposure
- TransportPrincipal public-path activation
- public credential issuer authority
- credential lifecycle policy activation
- public revocation registry activation
- public replay cache activation
- admission policy activation
- ban registry activation
- public rate-limit state activation
- privacy policy activation
- Werner overlay activation
- helper promotion
- marker removal
- materialized export manifest production
- source allowlist export execution
- public repository publication
- public package publication
- release artifact production
- release-key generation
- release envelope production
- release manifest instance production
- public claimability activation
- public claimability API activation
- public verifier service
- public claim endpoint
- wallet withdrawal
- wallet transfer
- wallet spend
- wallet signing authority
- wallet ledger-write authority
- ECU minting
- ILC settlement
- withdrawal runtime activation
- CDL mutation
- CDL-088 opening
- Genesis Atlas mutation
- Genesis Atlas regeneration
- Genesis Atlas signing
- v0.2 signing
- public RC claim
- public launch claim
- IP filing
- paper publication
- immutable diagnostic mutation
- production `commit.epoch` emission

Public RC remains blocked after Phase 1297:

```text
public_rc_remains_blocked_after_phase_1297
```

Remaining blocker classes include final public claimability API/verifier
authority, privacy filter implementation and review, replay/nullifier and
duplicate-claim registry policy, actual TransportPrincipal public-path
activation authority, post-ratification helper replacement or explicit
promotion prerequisites, actual public sidecar/projection serving authority,
sidecar bind/listener/peer-discovery authority, release publication and v0.2
signing authority, counsel/IP/publication authorization, source publication and
release artifact authorization, wallet withdrawal/transfer/spend semantics,
ECU minting, and ILC settlement.

---

## 7. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_sidecar_public_safe_projection_schema_1297_v0.1.md -> sidecar/public_path
graph_delta=support_tests_added:tests/test_phase_1297_sidecar_public_safe_projection_schema.py -> validation
graph_delta=support_only:docs/phases/phase_1297_sidecar_public_safe_projection_schema_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```
