# ILC Network Transport Identity and Value Path — Forward Planning v0.1

**Produced:** 2026-05-07
**Session context:** Window 1233-1240 open; Phase 1238 SIM-FETCH-01 complete; sidecar runtime
Phase 1237 Fix1-Fix7 complete; audit hardening committed (9601ac79).
**Status:** Non-normative forward planning. Does not override ratified CDL state.
**Governing authorities:** CDL register, ADR register, ratified runtime chain.
**Purpose:** Record architectural decisions and planning tokens from Gemini review synthesis
(2026-05-07 Codex conversation) across four threads: transport identity, OpenClaw/deployment
posture, Werner topological flow governor, and ECU/ILC value path.

```text
network_transport_identity_and_value_path_forward_planning_recorded_phase_1238
```

---

## 1. Background: What Triggered This Review

Phase 1237 completed a full L3 sidecar query runtime (Fix1-Fix7, 107 tests). Phase 1237 Post-Fix7
applied deep audit hardening (136 tests). Phase 1238 delivered SIM-FETCH-01 with baseline verdict
`fail` due to Tier C sparsity. During this work, Gemini's architectural review was evaluated and
synthesized with existing repo canon. This document records the forward-planning outputs of that
synthesis, including where Gemini was right, where it was stale, and what needs to move into
actionable planning tokens.

---

## 2. Transport Layer Assessment

### 2.1 What exists and is bounded (correcting Gemini C partial staleness)

Gemini's "unbounded collections" critique is partially outdated. Current confirmed state:

| Collection | Module | Bound | Confirmed |
|------------|--------|-------|-----------|
| `PeerFingerprintCache` | `peer_fingerprint_cache.py` | `DEFAULT_MAX_CACHE_SIZE = 5_000` (LRU eviction) | Phase 1237 audit |
| Transport event log | `http_gossip_transport_runtime.py` | `deque(maxlen=10_000)` | Phase 1237 audit |
| Rate limiter buckets | `persistent_fetch_rate_limiter_runtime.py` | `max_buckets = 10_000` | Phase 1202 |
| Fetch transport rate limit key | `http_fetch_transport_runtime.py:238` | Keys on `client_ip`, not JSON `requester_id` | Code read 2026-05-07 |

The Rust QUIC layer in `ilc_consensus/src/network.rs` already uses Quinn (QUIC) and rustls (TLS 1.3)
with pinned certificate verification. The Python HTTP transport is not the only network layer in the
repo — the Rust consensus path already uses proper async TLS.

Continuous hardening remains correct as a standing obligation. A bounded-state audit should scan any
new server-facing collection before it ships. This is not a single-phase fix but a per-PR invariant.

### 2.2 Rate limit key gap: IP → authenticated principal

The fetch transport keys rate limiting on `client_ip` (line 238,
`http_fetch_transport_runtime.py`). This is better than JSON `requester_id` from payload, but it
is still not sufficient for an adversarial public network. IP addresses are shared by NAT, dynamic,
and cheap to rotate.

**The correct fix:** rate limiting and admission must bind to an authenticated *transport
principal* — a cryptographic identity that costs something to establish, is tied to observed
behavior, and cannot be trivially rotated.

This is the highest-priority network hardening item before public P2P exposure.

### 2.3 The key ladder

The repo already has layered identity types. The correct ladder, as confirmed by Codex synthesis and
existing code, is:

| Layer | Identity type | Primary use | Notes |
|-------|--------------|-------------|-------|
| L0: Protocol | `AgentID` | Permanent epistemic identity; content-addressed key derivation | Python; Phase 410; CDL-042; must not be exposed as transport handle |
| L1: Consensus/economic | BLS12-381 agent/validator key | Quorum voting, ECU transfer certificates, epoch finality | Rust `ilc_consensus`; CDL-055/056 validator rules |
| L2: Enrollment/bootstrap | Ed25519 enrollment/beacon key | Bootstrap admission, route/beacon auth, sealed-sender H-013 path | H-013 lane; Phase 938 |
| L3: Transport | **TransportPrincipal** ← MISSING | D2D connection auth, rate limiting, admission, peer reputation | Must be defined; see §2.4 |
| L4: Deployment/container | OpenClaw/NemoClaw harness identity | Container lifecycle, tool permissions, credential injection | Orchestration only; outside protocol law |

**Critical invariants established from this synthesis:**
- `AgentID` must not be the default transport-level rate limit key. Exposing permanent economic
  identity at the transport layer undermines sealed-sender/privacy posture and allows adversarial
  correlation across epochs.
- BLS keys are for economic signing (quorum, transfer certificates). Not for per-connection
  transport identity.
- OpenClaw/NemoClaw identity is a deployment channel concern. It must not become a protocol
  dependency. The Agent SDK boundary contract (Phase 665-670 lock) confirms: SDK must work without
  OpenClaw.

### 2.4 TransportPrincipal: the missing layer

`TransportPrincipal` is not yet defined or implemented. It should be:
- A short-lived or rotating identity suitable for rate limiting and peer banning
- Cryptographically derived (Ed25519 key pair minimum; could be derived from enrollment key or
  separately provisioned)
- Bound to observable transport behavior (spam, circuit breaker activations, invalid envelopes)
- Optionally linkable to stake/reputation under governance authorization, but not automatically
  equal to AgentID or validator key
- The key that `PersistentFetchRateLimiter` and admission controls bind to, replacing IP

Design constraint: TransportPrincipal must not require revealing agent economic position at
connection time. An agent with large stake should not be identifiable as such by a passive
network observer watching D2D connections.

**Planning tokens:**

```text
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
transport_principal_cdl_required_before_runtime_implementation
```

### 2.5 Python HTTP transport downgrade path

The Python `ThreadingHTTPServer` layers (`http_fetch_transport_runtime.py`,
`http_gossip_transport_runtime.py`) are correctly classified as devnet/test harnesses.
They are NOT suitable as the public-internet-facing P2P substrate. They should be:
1. Formally downgraded to `devnet/test` classification in a near-term phase
2. Left intact as regression/test surfaces — do not "rip out"
3. Replaced with a Rust async transport lane (Quinn/libp2p-compatible) as the public P2P path

The Rust QUIC layer in `ilc_consensus/src/network.rs` provides the foundation. The gap is:
making it the primary public P2P transport for D2D (not just consensus gossip).

**Planning tokens:**

```text
python_http_transport_formally_downgraded_to_devnet_test_only_required
rust_public_p2p_transport_lane_required_before_public_p2p
rust_quic_tls_transport_already_exists_in_ilc_consensus_src_network_rs
```

### 2.6 OpenClaw/NemoClaw posture

NemoClaw (NVIDIA's OpenClaw reference stack) is a sandboxing, lifecycle, credential injection,
and proxied network/API access framework for LLM agents. It is NOT a sovereign BFT P2P transport.

**The correct framing (confirmed by Phase 665-670 lock and SDK boundary contract):**

- ILC SDK (protocol surface): works identically regardless of deployment mechanism
- OpenClaw/NemoClaw (orchestration surface): one valid deployment channel; must not be required
- ILC core: modular, connects to whatever transport the deployment harness exposes
- OpenClaw/NemoClaw as ILC onboarding/skill packaging: a valid parallel lane that makes ILC
  accessible through agentic harnesses without requiring users to run a full node
- OpenClaw/NemoClaw as ILC protocol substrate: explicitly NOT the direction

The fork in the road the user identified:
- Path A: Public RC with ILC core + own harness → use Rust P2P transport
- Path B: OpenClaw/NemoClaw skill packaging first → lower barrier, orchestration-level onboarding

These are not mutually exclusive. Path B (OpenClaw packaging as onboarding lane) can proceed in
parallel without blocking Path A. The SDK boundary contract already establishes the correct
separation.

**Planning token:**

```text
openclaw_sdk_packaging_lane_not_base_transport_dependency
openclaw_skill_packaging_phase_authorized_as_parallel_onboarding_lane
```

---

## 3. Werner Topological Flow Governor

### 3.1 Existing infrastructure

The repo already has:
- `ilc_core/analysis/laplacian_analytics.py` — normalized hypergraph Laplacian, lambda2,
  structural impedance concepts
- `ilc_core/analysis/local_spectral_analytics.py` — local lambda2, Fiedler centrality delta
- `ilc_core/types.py` — `REUSE_ATTRIBUTION_RATE = Decimal("0.20")`,
  `EDGE_MINT_PHI_BOUND = Decimal("0.60")` (Werner φ-bound)
- `ilc_core/economics/epoch_attribution_settle_runtime.py` — Werner φ-bound enforcement,
  provenance decay, productive credit attribution
- `ilc_core/network/d2d/persistent_fetch_rate_limiter_runtime.py` — circuit breaker
- `ilc_core/network/d2d/centrality_delta_gossip_runtime.py` — CDL-060 centrality delta

What does not yet exist: a function that constructs a *heat vector* over the shard/peer topology,
runs Laplacian smoothing over it, and produces bidirectional control outputs (cooling + heating).

### 3.2 The architecture

Heat across shards, rates, and serve pressure is a topology signal if modeled as flows over a
graph. Three coupled graphs apply:

| Graph | Nodes | Edges | Signal |
|-------|-------|-------|--------|
| Transport topology | Serving peers, shards, route paths | Fetch flows, serve pressure, relay routes | Request pressure, cache miss rate, circuit breaker activations |
| Economic pressure topology | Agents, shards, escrow pools | ECU credit flow, productive-flow credit, bounty demand | Werner phi-bound pressure, credit advance eligibility |
| Epistemic topology | Graph Nodes (truth primitives, CDLs, ADRs) | Provenance, reuse, refutation edges | Centrality, structural impedance, Fiedler vector |

The dual Laplacian applies naturally: primal graph nodes are shards/peers (for hot shard
detection); dual graph nodes are flows/edges (fetch streams, provenance paths, cache-mirror
relationships). This lets the controller detect hot shards, hot links, hot proof classes,
brittle bridges, underconnected high-value regions, and Sybil-like dense local clusters.

### 3.3 Bidirectional control outputs

The Werner Flow Governor is NOT a rate limiter and NOT a per-request ECU toll. It is a
topology-aware, bidirectional economic control system.

**Cooling signals** (suppress overload and unproductive amplification):
- Reduce request/admission budget for identities whose traffic is high but `productive_flow_score`
  is low
- Tighten escrow, reduce CWEA/credit advance eligibility, lengthen vesting when pressure looks
  spammy
- Suppress provenance/edge-mint payouts when phi-bound evidence says expansion is non-productive
  (CDL-085 Werner φ-bound already does this at the attribution layer)
- Activate static 429/rate limit circuit breaker as fallback abuse control (not primary policy)

**Heating signals** (attract capacity to where useful work is scarce):
- Increase routing weight for peers that reliably serve useful data (CDL-078 reputation path)
- Expand cache/mirror priority for underconnected shards with high verified demand
- Offer bounded ECU bounties or productive credit advances where connectivity deficits block work
- Raise serve/admission budget for authenticated principals with good `productive_flow_score`

**Candidate `productive_flow_score` components:**
```
verified_serves
+ valid_reuse
+ accepted_provenance
+ successful_refutations
- rejected_sybil_paths
- overload_penalties
```

The clean invariant chain:
```
network heat topology
→ smoothed pressure via primal/dual Laplacian
→ productive work demand signal (beta-decomposed from noise)
→ ECU allocation / bounty / credit budget
→ ILC incentive and settlement effects
```

**Critical invariant:** heat must not directly create ECU. Heat identifies where useful work is
scarce. ECU is emitted only when an agent performs *verified productive work* against that demand.

**Critical invariant preserved from prior repo decisions:** no per-hop ECU micropayment for
fetch/relay. The relay incentive is reputation-implicit (CDL-078), not a per-packet toll.

### 3.4 Relationship to SIM-FETCH-01

The SIM-FETCH-01 harness (Phase 1238) is the right place to first prototype the heat vector and
topology smoother as a *simulation overlay*, not as runtime policy. The Phase 1238 Fix series
(particularly Fix5 or a later Fix) should add:
- A `build_heat_vector(sim_result)` function that constructs `h_i` from serve pressure,
  cache miss pressure, circuit breaker activations per shard/peer
- A smoothed pressure field using the existing `laplacian_analytics.py` utilities
- A bidirectional control output report: which shards get cooled, which get heated

This produces simulation evidence before any runtime deployment. A CDL is required before
deploying as runtime policy.

**Planning tokens:**

```text
werner_topological_flow_governor_forward_planning_recorded_phase_1238
werner_flow_governor_overlay_required_for_sim_fetch_01
server_shard_credit_flow_governor_required_pre_public_p2p
no_per_hop_ecu_micropayment_for_fetch_relay_preserved
flow_governor_cdl_required_before_runtime_policy_deployment
beta_decomposition_required_before_policy_use
flow_governor_must_not_replace_quality_reputation_mechanism
fetch_rate_limit_must_remain_circuit_breaker_until_authenticated_principal_credit_governor_cdl
```

---

## 4. ECU Credit Creation and ILC Settlement — Value Path Gaps

This section records the pre-public-launch gaps in the complete productive-work-to-value chain.
The current architecture has the accounting spine (ECU balances in Rust, wallet visibility in
Python) but the public value loop is not complete.

### 4.1 Current state (confirmed from code)

| Component | Status |
|-----------|--------|
| `balance_store.rs` | ECU balance storage, transfer application, replay checks, duplicate attribution rejection, overflow guards — OPERATIONAL |
| `types.rs` | ECU as `u64` micro-ECU fixed-point — CORRECT |
| `economic_cycle_runtime.py` | Bounded RC wallet state and wallet history — OPERATIONAL |
| Phase 576 wallet boundary | Wallet visibility is read-only; no ledger write authority — ENFORCED |
| CDL-048 | Mandatory ECU conversion after 4 issuance epochs — RATIFIED |
| Phase 609 | ECU = productive credit, ILC = hard settlement asset; public settlement substrate unresolved — CANONICAL |
| `balance_ilc` in RC wallet | Internal field present, no public conversion runtime — GAP |

### 4.2 Gap 1: ECU credit creation in the agentic wallet

The wallet cannot originate credit creation, accept a Werner work advance, sign spend/escrow
actions, or manage active productive-credit state. This gap must close before public launch.

Required missing pieces:

| Component | Description |
|-----------|-------------|
| `ECUCreditCreationIntent` | Wallet-side object: work being financed, shard/heat demand responded to, evidence authorizing it, repayment/retirement path |
| Werner authorization rule | Credit issued only against verified productive commitment, accepted bounty flow, validated receivable, escrowed sponsor capital, or quality-weighted portfolio with haircut |
| Exposure ceilings | Per agent, per shard, per epoch, and global outstanding credit cap |
| Escrow and clawback | Failed commitments cancel credit and burn/forfeit bonded stake without socializing unlimited loss |
| Wallet signing authority | Separate keys: identity, transfer, productive-credit intent, recovery, governance-sensitive actions |
| Consensus integration | ECU creation must settle through Rust/epoch authority, not Python wallet mutation |
| Lifecycle state machine | Proposed → accepted → active → partially retired → retired → defaulted → clawed back → converted |
| Funding provenance tags | organic, bounty, treasury-authorized, sponsor-escrowed, receivable-backed, subsidized |

**Critical invariant:** the wallet requests or signs ECU creation, but it must not *create* ECU by
itself. ECU creation is a consensus-epoch-settled event.

### 4.3 Gap 2: ECU-to-ILC settlement execution runtime

CDL-048 ratifies the 4-epoch mandatory conversion deadline. The current `balance_ilc` field in
the RC wallet is internal state, not a public conversion runtime with receipts.

**Note on scope separation (pushback on over-bundling):** Two components must be separated:

1. **Conversion mechanism** — eligible ECU lots convert to ILC quantity at `P_e` per epoch
   settlement. This is *internal bookkeeping* that can be implemented as a Rust/epoch-settled
   runtime without requiring a public substrate decision. This should be implemented pre-launch
   to prove the economic model works on testnet.

2. **Public claimability substrate** — what chain/mechanism allows humans to actually
   withdraw/claim ILC (L1 chain? wrapped token? custody?). This is a *governance decision*
   affecting public launch timing but NOT blocking internal testnet readiness.

Conflating these creates a false dependency. The conversion runtime can be built now. The public
claimability substrate choice requires separate deliberation.

Required missing pieces for conversion mechanism:

| Component | Description |
|-----------|-------------|
| Production conversion runtime | Eligible ECU lots → ILC quantity at `P_e` per epoch settlement, canonical rules |
| Decimal/fixed-point `P_e` runtime | `epoch_ledger.py` has float telemetry path only; production requires fixed-point monetary engine |
| Mandatory conversion sweeper | Enforce CDL-048 4-epoch deadline; sweep expired ECU lots |
| ILC issuance budget accounting | Total ILC budget available, emitted per epoch, exhausted, taper/long-tail |
| Claimability state machine | Internal settled → pending conversion → converted ILC → claimable ILC → transferred/withdrawn |
| Machine-verifiable receipts | ECU origin, conversion epoch, `P_e`, ILC amount, claimability status; auditable |

### 4.4 Priority order for value path

| Priority | Component | Pre-launch required |
|----------|-----------|---------------------|
| 1 | `ECUCreditCreationIntent` design spec + CDL | Yes — no value path without authorized creation |
| 2 | Werner productive credit authorization CDL | Yes — CDL required before runtime |
| 3 | ECU-to-ILC conversion mechanism runtime (internal) | Yes — proves economic model on testnet |
| 4 | `P_e` fixed-point governor runtime | Yes — float clearing price is wrong for settlement |
| 5 | Mandatory conversion sweeper (CDL-048 runtime) | Yes — CDL ratified; runtime must close the loop |
| 6 | Public claimability substrate decision | Yes for public launch; not blocking testnet proof |
| 7 | Wallet signing authority widening | Yes for public launch; not blocking testnet proof |
| 8 | Machine-verifiable public receipts | Yes for public launch |

**Planning tokens:**

```text
agentic_wallet_ecu_credit_creation_runtime_required_pre_public_launch
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
ecu_to_ilc_conversion_execution_runtime_required_pre_public_launch
pe_governor_fixed_point_runtime_required_pre_public_launch
mandatory_conversion_sweeper_required_for_cdl_048_runtime
ilc_public_claimability_substrate_required_pre_public_launch
ilc_public_claimability_substrate_does_not_block_internal_conversion_runtime
wallet_signing_spend_transfer_claimability_boundary_required
ecu_credit_creation_intent_cdl_required
```

---

## 5. SIM-FETCH-01 Fix Phase Recommendations

The Phase 1238 baseline verdict `fail` is informative evidence about the Tier C distribution
model, not a terminal result. The Phase 1238 Fix series should address four gaps in priority
order:

| Fix | Topic | Rationale |
|-----|-------|-----------|
| Fix1 | Tier-stratified failure rates + verdict correction | CDL-087 §3 explicitly says Tier C has "no infrastructure-grade service expectation"; applying the ≤0.10 threshold to aggregate failure including inherently-sparse Tier C is architecturally wrong. Fix the verdict logic before sweeping parameters. |
| Fix2 | Configurable tier inventory fractions + parameter sweep runner | The most critical evidence for CDL-087 ratification condition 1: what inventory coverage produces pass? Harness currently has hardcoded `_TIER_B_PEER_INVENTORY_FRACTION = 6` and `_TIER_C_PEER_INVENTORY_FRACTION = 2` as module constants — not configurable. |
| Fix3 | Multi-hop WANT-HAVE retry model | CDL-077 real behavior: agents probe multiple peers before giving up. A single-hop 404 is modeled as terminal failure. With `max_retry_hops=3` and `tier_c_inventory=0.60`, Tier C effective miss ≈ `0.40^3 = 0.064` → failure_rate drops to ~0.06. |
| Fix4 | Zipf artifact selection within tiers | Real content follows power-law popularity. Uniform selection underestimates how quickly hot Tier A artifacts warm in cache. |
| Fix5 | Warm-up epochs + steady-state measurement | Cold-start cache drags aggregate hit rates down; separate warm-up from measurement epochs. |

**Planning tokens:**

```text
sim_fetch_01_tier_stratified_failure_rates_required
sim_fetch_01_configurable_inventory_fractions_required
sim_fetch_01_multi_hop_retry_model_required
sim_fetch_01_parameter_sweep_required_for_cdl_087_evidence
sim_fetch_01_zipf_artifact_selection_required_for_realism
sim_fetch_01_warmup_epoch_separation_required
```

---

## 6. Assessment Summary: Gemini Recommendations A-D

| Rec | Assessment | Action |
|-----|------------|--------|
| **A — Rip out Python HTTP, use libp2p** | Directionally right; too absolute. Rust QUIC/TLS already exists in `network.rs`. Python HTTP should be formally downgraded to devnet/test only, not destroyed — it is a regression surface. | `python_http_transport_formally_downgraded_to_devnet_test_only_required`; `rust_public_p2p_transport_lane_required_before_public_p2p` |
| **B — Cryptographic identity at transport layer** | Strong agree. IP-based rate limiting is insufficient. TransportPrincipal layer is genuinely missing. Must not default to AgentID as transport key. | `transport_principal_identity_required_before_public_p2p`; CDL required |
| **C — Strict memory bounding** | Partially stale. PeerFingerprintCache is already capped at 5,000. Event logs use `deque(maxlen=10_000)`. Fetch transport already keys on `client_ip` not JSON `requester_id`. Continuous hardening remains the right standing obligation. | Standing per-PR invariant; no single phase required |
| **D — Shift state management to Rust** | Agree on direction; nuance required. Rust should own: networking, admission, peer identity, mempool buffering, settlement, rate limiting. Python should own: agent reasoning, local orchestration, analysis, sidecar query, non-adversarial tooling. Do NOT move agent cognition to Rust. Projection/query/cache state can stay Python if read-only, bounded, deterministic, fed by authenticated Rust outputs. | Strategic boundary; enforce per phase review |

---

## 7. Planning Token Registry

```text
# Transport identity
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
transport_principal_cdl_required_before_runtime_implementation
python_http_transport_formally_downgraded_to_devnet_test_only_required
rust_public_p2p_transport_lane_required_before_public_p2p
rust_quic_tls_transport_already_exists_in_ilc_consensus_src_network_rs
openclaw_sdk_packaging_lane_not_base_transport_dependency
openclaw_skill_packaging_phase_authorized_as_parallel_onboarding_lane

# Werner flow governor
werner_topological_flow_governor_forward_planning_recorded_phase_1238
werner_flow_governor_overlay_required_for_sim_fetch_01
server_shard_credit_flow_governor_required_pre_public_p2p
no_per_hop_ecu_micropayment_for_fetch_relay_preserved
flow_governor_cdl_required_before_runtime_policy_deployment
beta_decomposition_required_before_policy_use
flow_governor_must_not_replace_quality_reputation_mechanism
fetch_rate_limit_must_remain_circuit_breaker_until_authenticated_principal_credit_governor_cdl

# ECU creation and ILC settlement
agentic_wallet_ecu_credit_creation_runtime_required_pre_public_launch
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
ecu_to_ilc_conversion_execution_runtime_required_pre_public_launch
pe_governor_fixed_point_runtime_required_pre_public_launch
mandatory_conversion_sweeper_required_for_cdl_048_runtime
ilc_public_claimability_substrate_required_pre_public_launch
ilc_public_claimability_substrate_does_not_block_internal_conversion_runtime
wallet_signing_spend_transfer_claimability_boundary_required
ecu_credit_creation_intent_cdl_required

# SIM-FETCH-01 improvements
sim_fetch_01_tier_stratified_failure_rates_required
sim_fetch_01_configurable_inventory_fractions_required
sim_fetch_01_multi_hop_retry_model_required
sim_fetch_01_parameter_sweep_required_for_cdl_087_evidence
sim_fetch_01_zipf_artifact_selection_required_for_realism
sim_fetch_01_warmup_epoch_separation_required
```
