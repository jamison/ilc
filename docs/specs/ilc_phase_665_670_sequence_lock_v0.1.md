# ILC Phase 665-670 Sequence Lock v0.1

Status: sequence lock artifact
Date: 2026-04-15
Owner lane: G8 transport maturity strike force
Classification: sensitive planning boundary

## 1. Window identity and row-9 target

Phase 665 locks Window 665-670 as the row-9 transport and discovery maturity
lane.

Required lock statements:
- `row_9_lane_locked_to_operational_maturity_not_dynamic_discovery`
- `row_9_target_bounded_public_participant_maturity`

The locked target is:
- bounded public-participant transport and discovery maturity
- under the already-ratified D2d posture
- for the first honest public-participant threshold, not for internet-scale
  proof

## 2. Inherited canon and non-goals

Inherited canon:
- ADR-0025 keeps HTTP/3 over QUIC as the preferred D2d binding and HTTP/2 as
  the fallback path where QUIC or UDP is blocked
- static peer registry v1 remains the active discovery posture
- curated bootstrap plus explicit promotion remains the active RC/testbed
  posture
- bounded metadata/topology PUSH plus heavy payload PULL remains the current
  hybrid discipline

Required non-goal lock:
- `dynamic_peer_discovery_deferred_beyond_665_670`

This phase does not authorize:
- dynamic peer discovery
- DHT or swarm membership
- autonomous peer-set expansion
- anonymity-overlay requirements
- any row-7 or row-8 closure work
- any `CDL-062` work

## 3. Closure tier versus stretch tier

Required lock:
- `closure_tier_vs_stretch_tier_threshold_split`

Closure-tier evidence means:
- enough evidence to close row 9 honestly if the later gate passes
- the minimum topology, scenario, and repeatability proof fixed in Phase 666

Stretch-tier evidence means:
- broader or deeper evidence that improves confidence and later lanes
- longer-tail capture that is useful but not required for closure unless it
  exposes a core failure

## 4. Live-infra and VPN discipline

Required lock:
- `vpn_firewall_posture_must_be_verified_first`

The lane must verify live-infra posture before making closure-grade claims:
- the two external VPNs are available as bounded distributed evidence
  infrastructure
- required ports and bind posture must be verified before any live transport
  claim is made
- blocked or unavailable live posture must be recorded as an evidence limit,
  not hidden

This phase performs no live VPN or remote-host interaction.

## 5. OpenClaw overlay-harness boundary

Required lock:
- `openclaw_overlay_harness_not_transport_base_layer`

OpenClaw may support:
- internal RC operator assistance
- remote agent operability checks
- overlay-harness experiments

OpenClaw may not become:
- the required base harness for transport correctness
- a substitute for the raw transport proof surface

## 6. What this window may and may not close

Required lock:
- `participant_lateness_cost_is_participant_side_not_network_rescue_duty`

The lane posture is intentionally “lazy but precise”:
- late or absent participants bear the cost of lateness or absence
- the network does not owe bespoke rescue semantics
- the protocol still owes deterministic, machine-legible failure and recovery
  behavior

What Window 665-670 may close:
- row 9 only, if and only if the maturity contract is met and the closure gate
  passes

What Window 665-670 may not close:
- row 5
- row 7
- row 8
- `CDL-062`
- final `Option B` selection
