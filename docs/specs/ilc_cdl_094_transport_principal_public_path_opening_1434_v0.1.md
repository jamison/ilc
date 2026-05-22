# ILC CDL-094 TransportPrincipal Public-Path Opening 1434 v0.1

**Date:** 2026-05-22
**Phase:** 1434
**Status:** CDL-094 opened; not prelocked; not ratified; no runtime activation
**Human authorization:** `GO Phase 1434`
**C1 commit:** `b5152c37`
**C2 commit:** this commit

```text
transport_principal_cdl_opened_phase_1434
cdl_094_transport_principal_opened_phase_1434
gap_10_cdl_opening_committed_phase_1434
cdl_094_opening_only_not_ratified_phase_1434
```

## 1. Verdict

Phase 1434 opens CDL-094 as the TransportPrincipal public-path governance lane.
The CDL register row is `status: open` only. Phase 1434 does not prelock,
ratify, implement, or activate the public path.

```text
cdl_094_status=open
cdl_094_ratified=false
gap_10_closed=false
public_fetch_serving_enabled=false
public_p2p_enabled=false
non_loopback_sidecar_projection_enabled=false
public_confidential_coordination_enabled=false
runtime_activation_status=not_authorized
```

## 2. Pre-Execution Claim Verification

| Claim | File or symbol checked | Result |
|---|---|---|
| CDL-093 is the last registered CDL before Phase 1434; CDL-094 is the next fresh number | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed before C1: CDL-093 was the last row; C1 added exactly one CDL-094 row |
| CDL-087 ratification carries a forward boundary that public fetch/sidecar serving remains blocked pending separate authorization | `docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md`; CDL register row `CDL-087` | confirmed: `cdl087_public_fetch_serving_not_enabled_phase_1278_fix1`, `cdl087_public_sidecar_projection_still_blocked_phase_1278_fix1`, `public_fetch_serving_status: not_enabled`, and `public_sidecar_projection_status: blocked_pending_separate_authorization` |
| CDL-079 is the HB-002 bootstrap distribution protocol, not public-path activation authority | `docs/specs/ilc_cdl_079_hb_002_bootstrap_distribution_ratification_evidence_918_v0.1.md`; CDL register row `CDL-079` | confirmed: operator-provided seed peer, CDL-077 bundle fetch, no DHT, no permissionless peer admission |
| Phase 1267 TransportPrincipal helper exists as a pre-public helper | `docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md`; `ilc_core/network/d2d/transport_principal_pre_public_path.py` | confirmed: helper constructs authenticated TransportPrincipal context and rejects requester_id, AgentID, harness identity, and client IP fallback |
| Phase 1277 public-path preflight helper remains internal and fail-closed | `docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md`; `ilc_core/network/d2d/transport_principal_public_path_preflight.py` | confirmed: helper is `PUBLIC_RC_EXCLUDE` and does not expose a listener, public P2P, public fetch, or non-loopback projection |
| Phase 1433 rehearsal verdict is PASS | `docs/specs/ilc_rehearsal_verdict_1433_v0.1.md` | confirmed: `verdict=PASS`, `rehearsal_verdict=pass_phase_1433`, wipe right exercised |
| `gossip_transport.py` does not conflict with TransportPrincipal scope | `ilc_core/network/d2d/gossip_transport.py`; `git status --short` | confirmed: no local modification to this file in the worktree; it remains an HTTP header adapter with no socket, QUIC, or HTTP client/server operations |

## 3. Discovery Results

### 3.1 Known Tokens

The Phase 1434 prompt, CDL register, Phase 1433 verdict, CDL-087 evidence,
CDL-079 evidence, Phase 1267 helper, Phase 1277 preflight, README contact block,
and historical public-path sidecar gate were searched for:

```text
transport_principal_cdl_opened_phase_1434
cdl_094
CDL-094
transport_principal
TransportPrincipal
gap_10
CDL-087
CDL-079
public_fetch
sidecar
jamison_confidential_sidecar
public_confidential_messaging
public_confidential_coordination_serving
rehearsal_verdict=pass_phase_1433
non_loopback_sidecar
public_fetch_serving
loopback_only_default
ILC_CDL_MUTATION_AUTHORIZED
```

### 3.2 Concept Search

Broad searches covered authenticated principal binding, public-path governance,
public fetch, public sidecar/projection serving, public P2P, non-loopback
binding, rate limiting, ban/revocation/replay, IP authentication, JSON body
identity fallback, confidential coordination, sealed sender, and contact
instructions for Jamison.

### 3.3 Contradiction And Non-Claim Search

Contradiction searches found no current source that blocks opening CDL-094 after
Phase 1433 PASS. They did confirm the following still-active non-claims:

```text
public_fetch_serving_not_enabled
public_sidecar_projection_serving_not_enabled
public_p2p_not_activated
non_loopback_bind_not_enabled
public_confidential_coordination_serving_requires_explicit_authority_phase_1337
public_confidential_coordination_serving_not_enabled_phase_1328
no_public_confidential_messaging
```

## 4. Problem Statement: Gap 10

Gap 10 blocks public P2P, public fetch serving, and non-loopback
sidecar/projection serving because the network needs an authenticated principal
abstraction for hostile public paths. IP address, host name, raw AgentID,
OpenClaw harness identity, and JSON body `requester_id` are not sufficient
public-path authority.

The current public-path blocker is not just "can a process listen on a port."
The missing constitutional rule is: which authenticated identity is responsible
for public-path admission, rate limits, replay checks, revocations, bans,
abuse throttling, and privacy-preserving contact surfaces.

CDL-094 is opened to deliberate that rule.

## 5. Proposed Scope

CDL-094 should define TransportPrincipal as the authenticated principal
abstraction that binds public paths to an agent-controlled transport credential.
The binding applies across:

- public HTTP fetch and verifier paths;
- public P2P or relay paths;
- public sidecar/projection serving;
- any later public confidential contact or coordination serving surface.

The principal must be derived from authenticated transport material such as an
mTLS certificate fingerprint, QUIC peer credential, rustls peer certificate-chain
hash, signed transport handshake, or successor credential type ratified by the
CDL. It must not be derived from:

- IP address;
- DNS host name;
- JSON body requester identity;
- HTTP header requester identity without cryptographic binding;
- raw AgentID as the default public-path rate-limit key;
- OpenClaw or test harness identity.

## 6. Policy Boundary

| Surface | Default before CDL-094 ratification | Candidate after later ratification and runtime activation |
|---|---|---|
| Loopback-only local paths | permitted when separately authorized | unchanged |
| Private Tailscale rehearsal paths | permitted as private rehearsal evidence only | unchanged unless public path is explicitly activated |
| Public fetch serving | blocked | TransportPrincipal-gated and CDL-087-compatible |
| Public sidecar/projection serving | blocked | TransportPrincipal-gated, privacy-filtered, and rate-limited |
| Public P2P/OpenClaw path | blocked | TransportPrincipal-gated and CDL-078/CDL-079/CDL-087-compatible |
| Public confidential contact surface | planned, not live | requires separate public confidential coordination authority in addition to CDL-094 |

Machine-readable boundary:

```text
loopback_only_default=true
public_path_requires_cdl_094_ratification=true
public_path_runtime_activation_required_after_ratification=true
```

## 7. Rate-Limit Policy Candidate

Phase 1435 deliberation should decide whether the initial public-path limiter
uses:

| Candidate | Summary | Risk |
|---|---|---|
| `per_transport_principal_epoch_bucket` | One bounded request bucket per TransportPrincipal per epoch | simple and deterministic, but weak for shared infrastructure abuse |
| `per_transport_principal_surface_bucket` | Separate buckets for fetch, verifier, sidecar, and P2P paths | better isolation, more policy surface |
| `weighted_transport_principal_bucket` | Principal-level bucket weighted by reputation, history, and current risk flags | strongest long-term shape, highest policy complexity |

Minimum recommended prelock floor:

```text
rate_limit_identity_source=authenticated_transport_principal
requester_id_fallback_allowed=false
client_ip_primary_rate_limit_key_allowed=false
agent_id_default_rate_limit_key_allowed=false
```

## 8. Ban, Revocation, Replay Integration Surface

CDL-094 deliberation should define how a TransportPrincipal participates in:

- credential issuance and expiry;
- revocation registry lookup;
- replay cache keying;
- ban registry keying;
- admission throttling;
- public-path audit trail minimization;
- privacy mode selection.

The Phase 1267 and Phase 1277 helpers already expose separate keys for rate
limit, admission, ban, and replay decisions. CDL-094 should decide whether those
separate keys are binding public-path requirements or pre-public implementation
guidance.

## 9. README Contact Placeholder Disposition

The README currently contains:

```text
jamison_confidential_sidecar: planned_not_live
status: local_preview_only_no_public_confidential_messaging
current_contact: out_of_band_until_public_confidential_coordination_authorized
future_gate[3]: CDL-094_TransportPrincipal,public_sidecar_activation,public_confidential_coordination_authority
update_trigger[2]: phase_1434_transport_principal_scope_review,phase_1435_transport_principal_ratification_review
```

Phase 1434 reviews the placeholder and preserves it as a non-claim:

```text
jamison_confidential_sidecar=planned_not_live
public_confidential_messaging_enabled=false
public_confidential_coordination_enabled=false
live_contact_instruction_added=false
```

No live confidential contact instruction is added in Phase 1434. A later phase
may update the README only after the public confidential coordination surface is
authorized by the relevant governance and runtime gates.

## 10. Explicitly Not In Scope

Phase 1434 does not authorize:

- CDL-094 prelock or ratification;
- runtime implementation of TransportPrincipal;
- non-loopback sidecar/projection serving;
- public fetch serving;
- public P2P or peer discovery;
- public OpenClaw gateway serving;
- public confidential messaging;
- public confidential coordination serving;
- IP-only authentication;
- anonymous public paths;
- JSON body `requester_id` authentication;
- graph writes;
- wallet writes;
- treasury writes;
- ECU minting;
- ILC settlement;
- public RC publication;
- epoch 0-to-1 transition.

## 11. Open Questions For Phase 1435

| ID | Question | Prelock target |
|---|---|---|
| Q1 | Which credential kinds are valid TransportPrincipal source material at first public RC? | mTLS fingerprint, QUIC peer credential, rustls certificate-chain hash, signed transport handshake, or stricter subset |
| Q2 | Which rate-limit policy candidate is initial law? | choose one of the three candidates in Section 7 |
| Q3 | What revocation and ban registry semantics are mandatory before public serving? | explicit registry inputs, epoch windows, replay-cache scope |
| Q4 | Is raw AgentID ever allowed as a public-path limiter key? | default answer should be no; use authenticated TransportPrincipal instead |
| Q5 | Does CDL-094 cover public confidential contact routing, or only the principal binding it would depend on? | preserve `jamison_confidential_sidecar=planned_not_live` unless separate authority is explicit |
| Q6 | What is the minimum privacy mode for public path attribution and auditability? | rotating pseudonymous principal or stricter |
| Q7 | Which runtime flag(s) must remain false until post-ratification activation? | public fetch, public P2P, non-loopback sidecar/projection, public confidential coordination |

## 12. Graph Delta

Runtime graph state is unchanged:

```text
graph_delta=none:no_runtime_graph_write_phase_1434
```

Governance documentation changes are load-bearing:

```text
graph_delta=load_bearing_artifact_changed:docs/specs/ilc_constitutional_decision_log_v0.1.md -> governance/cdl094
graph_delta=load_bearing_artifact_added:docs/specs/ilc_cdl_094_transport_principal_public_path_opening_1434_v0.1.md -> governance/cdl094
```
