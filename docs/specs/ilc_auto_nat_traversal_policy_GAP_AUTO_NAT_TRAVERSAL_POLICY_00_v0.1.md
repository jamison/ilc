# ILC Auto-NAT Traversal Policy and Consent Model
Version: v0.1
Phase: GAP-AUTO-NAT-TRAVERSAL-POLICY-00
Date: 2026-08-28
Status: ratified-spec-candidate
Governs: NAT traversal method allowlist, consent model, receipt requirements, rollback, privacy
Authority: ADR-0011, ADR-0039, ilc_connectivity_path_taxonomy_GAP_CONNECTIVITY_RECONCILE_00_v0.1

## 1 - Key Policy Principle

"Automatic traversal may be default only if it is bounded, disclosed, receipted, reversible, and fails safely to relay/outbound mode."

Definitions:

| Term | Required meaning |
|---|---|
| Bounded | Limited to one declared ILC inbound port, one declared method per attempt, bounded retries, and a maximum lease duration. |
| Disclosed | The operator, human or headless agent, can inspect the policy and receives a clear receipt for every attempted method and result. |
| Receipted | Every attempt writes a deterministic `NatTraversalAttemptReceipt`, including skipped attempts caused by missing opt-in. |
| Reversible | Any router mapping includes a machine-parseable rollback instruction and a lease expiration strategy. |
| Fails safely | Failure never crashes install, never leaves an unbounded mapping, and falls back to `relay_reachable` or `outbound_only`. |

Automatic traversal is intended to improve default reachability for ordinary installs. It is not an authority shortcut: direct reachability, relay reachability, and validator eligibility remain separately verified claims.

## 2 - Allowed Traversal Methods

| Method | Description | Default? | Requires opt-in flag | Max lease seconds | Notes |
|---|---|---:|---:|---:|---|
| ILC observer detection | ILC bootstrap node reports observed external IP/port. | Yes | No | N/A | Passive and non-mutating. Determines observed address only. |
| Relay fallback | Automatic fall-through to relay/rendezvous path. | Yes | No | N/A | Relay slot TTL is governed by relay spec. Option A admission required. Not router mutation. |
| PCP (Port Control Protocol) | RFC 6887 structured port mapping request to a PCP-capable router. | No | Yes, `--enable-upnp` | 3600 | Preferred over NAT-PMP when both are available. Requires rollback. |
| NAT-PMP | RFC 6886 legacy port mapping for older routers. | No | Yes, `--enable-upnp` | 3600 | Fallback from PCP. Requires rollback. |
| UPnP IGD | Universal Plug and Play Internet Gateway Device SOAP-based port mapping. | No | Yes, `--enable-upnp` | 3600 | Highest compatibility and highest local-network risk. Fallback from NAT-PMP. Requires rollback. |
| STUN (third-party) | Not allowed. | N/A | N/A | N/A | Forbidden. Use ILC observer detection only. |

Method order for implementation is observer detection first, relay fallback availability check second, then optional router mutation only when explicitly requested. If router mutation is enabled, attempt PCP, then NAT-PMP, then UPnP IGD, stopping after the first successful verified mapping.

## 3 - Install-Time Default Behavior

On a fresh install, ILC runs with serving peer ON by default and relay fallback ON by default. No router mutation is attempted at startup.

Default progression:

| Step | Expected mode |
|---|---|
| Identity created, no network attempt | `local_only` |
| Outbound bootstrap or update succeeds | `outbound_only` |
| Relay admission succeeds | `relay_reachable` |
| Operator runs explicit probe without router mutation | `outbound_only` or `direct_public` if already reachable |
| Operator runs with `--enable-upnp` and mapping succeeds | `nat_traversed_direct`, then `direct_public` after observer verification |

Direct reachability requires explicit `--enable-upnp` for router mutation or explicit `--probe-reachability` for non-mutating direct probe. Headless automated agents follow the same rule: router mutation requires `--enable-upnp` in the invocation command. Environment detection, noninteractive install, or agent autonomy does not create silent consent.

## 4 - Forbidden Silent Behaviors

None of these may occur without explicit opt-in and a user-visible receipt:

1. Creating or modifying a port forwarding rule on a router or firewall without the `--enable-upnp` flag.
2. Contacting any third-party STUN server, including Google, Cloudflare, ISP, or vendor STUN services.
3. Creating a port mapping without an associated `rollback_instruction` in the traversal receipt.
4. Opening a port range broader than the single required ILC inbound port.
5. Creating a permanent port mapping (`lease_seconds = 0`, unlimited lease, or equivalent) without a future explicit configuration authority.
6. Retrying a failed traversal attempt without bounded backoff and operator-visible receipt.
7. Claiming `connectivity_mode = "direct_public"` or `connectivity_mode = "nat_traversed_direct"` without successful external verification from an ILC probe observer.
8. Publishing router model, firmware version, LAN IP, gateway metadata, or UPnP device descriptions as public graph or gossip data.
9. Treating relay reachability alone as active validator admission or as eligibility for economic rewards.

## 5 - Receipt Schema

Every traversal attempt must produce a `NatTraversalAttemptReceipt` record with these fields:

| Field | Type | Required | Description |
|---|---|---:|---|
| `agent_id` | string | Yes | AgentID of the instance that made the attempt. |
| `attempt_timestamp_epoch` | uint64 | Yes | Protocol epoch at time of attempt. This is not wall clock for protocol logic. |
| `method` | string | Yes | One of `ilc_observer_detection`, `pcp`, `nat_pmp`, `upnp_igd`, `relay_fallback`. |
| `result` | string | Yes | One of `success`, `failure`, `not_attempted`, `skipped_no_opt_in`. |
| `external_endpoint` | string or null | Yes | Observed external IP:port if result is `success`; null otherwise. |
| `internal_port` | uint16 | Yes | Internal port that was mapped or probed. |
| `lease_seconds` | uint32 | Yes | Lease duration in seconds; `0` if no mapping was created. |
| `rollback_instruction` | string or null | Yes | Machine-readable rollback command; null if no mapping was created. |
| `observer_ref` | string or null | Yes | AgentID or hostname of ILC bootstrap observer used; null if method is not observer-based. |
| `firewall_mutation_attempted` | bool | Yes | True if any router state was modified; must be false unless `--enable-upnp` was explicitly set. |
| `policy_version` | string | Yes | Version of this policy document governing the attempt. |

Canonical serialization:

```python
json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

No float values are allowed. Receipt implementations must reject `NaN`, `Infinity`, negative ports, zero ports, out-of-range ports, negative lease values, and unknown methods/results.

## 6 - Port Allowlist and Lease Limits

| Control | Policy |
|---|---|
| Port allowlist | Only the single configured ILC inbound port may be mapped. Default must be configurable and within 1024-65535. |
| Port ranges | Forbidden. |
| Privileged ports | Forbidden for default install. |
| Maximum lease | 3600 seconds. |
| Permanent mappings | Forbidden pre-RC. |
| Renewal | Allowed before expiry, but each renewal produces a new receipt. |
| Expiry behavior | Release mapping if possible, then fall back to `relay_reachable` or `outbound_only`. |
| Multiple mappings | At most one active router-created mapping per AgentID per local install profile. |

## 7 - External Verification Requirement

Before declaring `connectivity_mode = "nat_traversed_direct"` or `connectivity_mode = "direct_public"`, the instance must:

1. Receive a probe response from at least one ILC bootstrap node confirming the external endpoint is reachable.
2. Record the probe response in the traversal receipt with `observer_ref` set.
3. Bind the observed endpoint to the current AgentID and local key material.
4. Keep the mode at `outbound_only` or `relay_reachable` if probe confirmation is absent before timeout.

`nat_traversed_direct` is a local candidate state until external verification succeeds. `direct_public` is externally verified direct reachability, but still not validator admission.

## 8 - Rollback and Lease Expiration

Every port mapping created by ILC must have a stored `rollback_instruction` that is:

- Machine-parseable.
- Bound to the exact method, protocol, internal port, external port, and lease.
- Tested before the mapping is declared successful when the router supports safe verification.
- Executed on clean shutdown and lease expiry.
- Re-attempted on unexpected restart if the lease has not expired and the local receipt is still present.

Rollback failure handling:

| Failure | Required behavior |
|---|---|
| Router unreachable | Record rollback failure and continue. Do not crash. |
| Rule already gone | Treat as safe terminal state and record `already_absent`. |
| Method unsupported | Record failure and fall back to next allowed method or relay/outbound. |
| Permission denied | Record failure, stop router mutation attempts for the current invocation, and fall back to relay/outbound. |

## 9 - Privacy Non-Claims

- ILC does not send the peer's IP address to arbitrary third-party STUN servers.
- ILC does not use Google STUN, Cloudflare STUN, ISP STUN, or vendor STUN infrastructure.
- ILC does not record external IP addresses in any public ledger or gossip advertisement without operator awareness.
- ILC does not disclose router model, firmware version, UPnP device description, gateway LAN address, or local network topology to any third party.
- ILC does not claim NAT traversal anonymity. Reachability and privacy are separate layers.
- ILC does not make `relay_reachable` equivalent to `direct_public`.

## 10 - Headless Agent Consent

Headless digital agents can consent through explicit invocation arguments or a local configuration record, but not through silence.

| Context | Router mutation allowed? | Required evidence |
|---|---:|---|
| Interactive human install without `--enable-upnp` | No | Receipt with `skipped_no_opt_in`. |
| Interactive human install with `--enable-upnp` | Yes | Receipt for each method attempted. |
| Headless install without `--enable-upnp` | No | Receipt with `skipped_no_opt_in`. |
| Headless install with `--enable-upnp` | Yes | Invocation record plus receipt for each method attempted. |
| Config-file authorization | Later phase only | Must be explicit, local, and auditable. |

The consent model intentionally allows default usefulness while preserving operator control over router mutation. Serving and relay fallback may be default. Router mutation is not.

## 11 - Non-Authorizations

This policy does not:

- Modify `ilc_core/`.
- Implement PCP, NAT-PMP, UPnP, relay, or probe runtime.
- Authorize arbitrary third-party STUN, TURN, ICE, or DHT.
- Clear public P2P, sidecar serving, validator, minting, settlement, or launch guards.
- Grant validator admission from reachability.
- Activate CDL-078 production relay incentives.
- Remove PyPI/GitHub fallback from pre-RC bootstrap.
- Publish public mirror content.

## 12 - Graph Delta

```text
load_bearing_artifact_added: docs/specs/ilc_auto_nat_traversal_policy_GAP_AUTO_NAT_TRAVERSAL_POLICY_00_v0.1.md -> genesis:genesis_root_v0.4
support_only: docs/phases/phase_gap_auto_nat_traversal_policy_00_walkthrough.md
```

