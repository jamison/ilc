# ILC Network Transport Identity and Value Path — Forward Planning v0.1

**Produced:** 2026-05-07
**Session context:** Window 1233-1240 open; Phase 1238 SIM-FETCH-01 complete; sidecar runtime
Phase 1237 Fix1-Fix7 complete; audit hardening committed (9601ac79).
**Status:** Non-normative forward planning. Does not override ratified CDL state.
**Governing authorities:** CDL register, ADR register, ratified runtime chain.
**Purpose:** Record architectural decisions and planning tokens from Gemini review synthesis
(2026-05-07 Codex conversation) across five threads: transport identity, OpenClaw/deployment
posture, package modularity, Werner topological flow governor, and ECU/ILC value path.

```text
network_transport_identity_and_value_path_forward_planning_recorded_phase_1238
unknown_unknown_discovery_required_before_phase_execution
```

---

## 0. Execution Discovery Discipline

Any future phase derived from this forward plan must run an unknown-unknown
discovery pass before coding. Known planning tokens are not enough for transport,
Werner, ECU/ILC, or claimability work because older canon often uses different
terms.

Required prompt/execution structure:

1. `§0a — Known-token audit`: verify the tokens already named in the prompt.
2. `§0b — Concept-discovery search`: search concepts and synonyms such as
   `principal`, `requester`, `claim`, `withdraw`, `redeem`, `mint`,
   `settlement`, `Werner`, `heat`, `flow`, `wallet`, and `conversion`.
3. `§0c — Contradiction and non-claim search`: search for `deferred`,
   `blocked`, `not authorized`, `not ratified`, `local-only`, `no public`,
   and domain-specific denial terms before widening any runtime or economic
   claim.
4. `§0d — Source expansion and newly discovered tokens`: direct-read every
   relevant hit and carry new tokens/non-claims into the phase artifact.

MemPalace can be used for historical recall, but every useful hit must be
direct-read in the repo before it is treated as canon.
Exact-token `rg` is only a schema/completion check for known markers. Transport
and value-path phases must also search token components, synonyms, neighboring
ideas, older names, runtime symbols, and denial terms before treating a blocker
or implementation concept as absent.

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

Public P2P must also remove any fallback from authenticated transport identity to a JSON/body
`requester_id`. A body field can remain a protocol payload field where already governed, but it
must not be trusted as the public-path rate-limit or ban key.

The same rule applies to the future sidecar projection endpoint. If projection serving is exposed
beyond loopback/local-process use, it requires TransportPrincipal authentication and public-path
rate limiting before launch.

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
- Covered by an explicit lifecycle: issuance, epoch-scoped rotation, revocation, local-ban
  persistence, replay prevention, and privacy-preserving admission/stake binding

Design constraint: TransportPrincipal must not require revealing agent economic position at
connection time. An agent with large stake should not be identifiable as such by a passive
network observer watching D2D connections.

**Planning tokens:**

```text
transport_principal_identity_required_before_public_p2p
d2d_rate_limiter_key_must_be_authenticated_transport_principal
agent_id_must_not_be_default_transport_rate_limit_key
json_requester_id_rate_limit_fallback_forbidden_public_p2p
transport_principal_cdl_required_before_runtime_implementation
transport_principal_lifecycle_and_revocation_spec_required
sidecar_projection_endpoint_public_path_requires_transport_principal_auth
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

The public P2P substrate should not be chosen by slogan. A near-term ADR must decide whether to
extend the existing Quinn/rustls transport, adopt libp2p, or define an adapter boundary that can
support both. Gemini's libp2p recommendation is directionally relevant, but the repository already
has Rust QUIC/TLS code and should evaluate reuse before introducing a new network stack.

**Planning tokens:**

```text
python_http_transport_formally_downgraded_to_devnet_test_only_required
rust_public_p2p_transport_lane_required_before_public_p2p
rust_quic_tls_transport_already_exists_in_ilc_consensus_src_network_rs
rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p
```

### 2.6 OpenClaw/NemoClaw posture

NemoClaw (NVIDIA's OpenClaw reference stack) is a sandboxing, lifecycle, credential injection,
and proxied network/API access framework for LLM agents. It is NOT a sovereign BFT P2P transport.
External check, 2026-05-07: NVIDIA describes NemoClaw as an open-source reference stack for running
OpenClaw assistants inside OpenShell containers with onboarding, lifecycle management, network
policies, and sandboxed execution. This supports treating it as an orchestration/onboarding layer,
not as ILC's protocol transport substrate.

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

Deployment note recorded 2026-05-07: the current VPS provider, DigitalOcean, offers OpenClaw
droplets, and the existing Tailscale/private-infrastructure posture appears compatible enough to
make DigitalOcean OpenClaw droplets the first external harness deployment test target. This is a
deployment-testing target only. It does not authorize public ILC P2P exposure, public sidecar
binding, unauthenticated projection serving, or treating OpenClaw/Tailscale as protocol substrate.
The intended first target is an OpenClaw/NemoClaw skill or sidecar profile reachable over loopback,
Tailscale, or other explicitly private harness wiring.

**Planning tokens:**

```text
openclaw_sdk_packaging_lane_not_base_transport_dependency
openclaw_skill_packaging_phase_authorized_as_parallel_onboarding_lane
digitalocean_openclaw_droplet_first_external_harness_target
tailscale_private_harness_network_allowed_no_public_p2p_claim
```

### 2.7 Package modularity for agentic harness integration

If ILC launches first as an OpenClaw/NemoClaw-consumable package or skill, the repo must be split
into package boundaries that let external harnesses provide transport, storage, lifecycle, and
credential injection without importing the ILC devnet HTTP stack.

The desired modularity is:

| Package / crate | Responsibility | Must not own |
|-----------------|----------------|--------------|
| `ilc_consensus_core` (Rust) | BLS/validator cryptography, quorum proof verification, fixed-point ECU primitives, epoch-settlement math | Python orchestration, CLI, OpenClaw adapters |
| `ilc_consensus_node` (Rust) | Public P2P transport, admission, mempool/buffer, rate limiting, settlement storage adapters | Agent cognition or LLM/tool orchestration |
| `ilc_logic` (Python) | Epistemic rules, projection/query logic, attribution rules, `commit.epoch` projection/adaptation surfaces, spectral distances | `http.server`, public network transport, LMDB ownership, terminal CLI |
| `ilc_node_runtime` (Python/Rust boundary) | Local node orchestration, storage wiring, daemon lifecycle, devnet/test server surfaces | Pure protocol math |
| `ilc_cli` (Python) | `ilc ...` command surface, config loading, operator UX, subprocess-compatible harness entrypoint | Protocol truth, economic settlement authority |
| `ilc_harness_adapters` (Python) | OpenClaw/NemoClaw skills, sidecar apps, local REST/CLI adapters, `TransportHarness` and `StorageHarness` protocol implementations | Canonical protocol law |

The Rust/Python boundary must include an explicit binding plan. If Python imports Rust consensus
logic directly, the implementing phase must choose and document the binding surface (likely PyO3 or
an equivalent stable FFI wrapper), including which APIs are exposed to Python and which remain
Rust-internal. This is separate from the public P2P substrate decision: a binding plan exposes local
consensus primitives to Python; the P2P ADR chooses the hostile-network transport substrate.

`commit.epoch` should be split, not moved wholesale:
- canonical mapping/projection/adaptation remains in Python `ilc_logic.protocol`;
- quorum/finality verification and settlement commitment remain Rust `ilc_consensus_core`;
- the CLI or node runtime triggers epoch commit, but neither should define the canonical event
  semantics;
- any trigger must use ratified epoch/sequence inputs, not OS wall clock time, for protocol
  liveness or settlement semantics.

Harness adapters can be sidecar apps, but the sidecar path must be local-first. If a local REST
API is bound beyond loopback or exposed to untrusted clients, it must require TransportPrincipal
authentication and the public P2P policy stack. OpenClaw/NemoClaw can call ILC through native Python
imports, CLI subprocesses, or a localhost sidecar API, but none of those deployment choices may
become protocol dependencies. The adapter contract should be generic enough for OpenClaw/NemoClaw
without becoming OpenClaw-specific: future harnesses (for example TypeScript, Go, C++, AutoGPT-style,
LangChain-style, or other agent runners) should be able to consume the same CLI/local-sidecar/native
import contract. Sidecar adapters also need dependency-isolation requirements: harness dependencies,
tooling dependencies, and public-facing transport stacks must not force their dependency graph into
the pure `ilc_logic` package or the Rust consensus core.

LOC baseline, measured locally on 2026-05-07:
- tracked repository files: approximately 852,159 lines;
- tracked Python + Rust only: approximately 276,405 lines;
- tracked Python/Rust/Markdown/JSON/TOML/YAML: approximately 577,728 lines.

This is a repository-size baseline, not a package-size target. Public launch should include a
package-size audit because docs, generated `out/` artifacts, test fixtures, patent-pending material,
and devnet harnesses should not all ship in the same installable surface. A reasonable launch
estimate must be measured from the selected packaging profile, not from monorepo LOC.

**Planning tokens:**

```text
ilc_package_modularity_split_required_before_openclaw_skill_launch
ilc_logic_pure_protocol_interfaces_required
ilc_logic_must_not_require_http_lmdb_or_harness_transport
ilc_cli_package_boundary_required
pyo3_binding_plan_required_for_ilc_consensus_core
commit_epoch_boundary_split_python_projection_rust_finality_required
commit_epoch_trigger_must_use_epoch_sequence_not_wall_clock
openclaw_nemoclaw_adapter_must_be_sidecar_or_cli_not_protocol_substrate
harness_adapter_transport_storage_protocols_required
generic_agent_harness_adapter_contract_required
localhost_sidecar_api_must_remain_loopback_or_transport_principal_auth
sidecar_dependency_isolation_required_for_harness_adapters
line_count_baseline_must_be_measured_not_estimated_before_public_rc
public_package_size_audit_required_before_openclaw_skill_launch
digitalocean_openclaw_droplet_first_external_harness_target
tailscale_private_harness_network_allowed_no_public_p2p_claim
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
- Increase future productive-work opportunity through reputation, discoverability, and admission
  budget before any direct value path is considered
- Offer bounded ECU bounties or productive credit advances only through separately governed bounty,
  escrow, wallet-intent, or productive-credit authorization paths where connectivity deficits block
  verified work
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
→ organic control first: routing reputation, routing weight, admission budget, cache/mirror priority
→ productive work demand signal (beta-decomposed from noise and reputation theater)
→ optional governed bounty / escrow / credit-intent path
→ ILC incentive and settlement effects
```

**Critical invariant:** heat must not directly create ECU. Heat identifies where useful work is
scarce and where routing/reputation/admission/cache policy should shift first. ECU is emitted only
when an agent performs *verified productive work* against an authorized demand path. Before any
phase proposes direct Werner-linked ECU creation, it must check repo canon, MemPalace/historical
conversation context, CDL-078, ADR-0016/0017, and the current wallet/settlement code for existing
organic or indirect instruments.

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

Phase 1238 Fix8 delivered the first Werner overlay as opt-in SIM-FETCH metrics
(`werner_overlay_enabled`). This was the correct containment while the model remained
non-authorizing evidence. It is not the desired permanent shape if Werner topology pressure is
part of the core evaluation path. After the overlay is validated, a follow-up phase must promote
it to the default SIM-FETCH topology-pressure evaluation profile, replacing the boolean with an
explicit profile such as `topology_pressure_model = "werner_v1"`. A `"none"` or null model should
remain only for legacy comparison/research evidence, not as the default production-facing
simulation path.

Before any heat/topology signal can become a policy input, it must pass the same spectral trust
threshold discipline already established in the spectral SIM work: enough established nodes,
connected-enough topology, nonzero reliable lambda2, and largest-component safeguards. Heat is a
demand signal, not an ECU minting authority.

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
flow_governor_spectral_trust_threshold_required_before_policy_use
heat_signal_must_not_directly_mint_ecu
werner_overlay_opt_in_must_be_promoted_or_retired_after_validation
werner_default_topology_pressure_profile_required_before_runtime_cdl
werner_heat_prefers_reputation_routing_admission_before_ecu_creation
direct_werner_ecu_creation_assumption_requires_repo_memtrace_check
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
| ECU lot accounting | Track issue epoch, origin, funding provenance, deadline, and conversion status; aggregate balances alone cannot enforce a 4-epoch sweeper |
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
ecu_lot_accounting_required_for_cdl_048_conversion_sweeper
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
json_requester_id_rate_limit_fallback_forbidden_public_p2p
transport_principal_cdl_required_before_runtime_implementation
transport_principal_lifecycle_and_revocation_spec_required
python_http_transport_formally_downgraded_to_devnet_test_only_required
rust_public_p2p_transport_lane_required_before_public_p2p
rust_quic_tls_transport_already_exists_in_ilc_consensus_src_network_rs
rust_p2p_substrate_decision_adr_required_quinn_vs_libp2p
openclaw_sdk_packaging_lane_not_base_transport_dependency
openclaw_skill_packaging_phase_authorized_as_parallel_onboarding_lane
sidecar_projection_endpoint_public_path_requires_transport_principal_auth

# OpenClaw/NemoClaw package modularity
ilc_package_modularity_split_required_before_openclaw_skill_launch
ilc_logic_pure_protocol_interfaces_required
ilc_logic_must_not_require_http_lmdb_or_harness_transport
ilc_cli_package_boundary_required
pyo3_binding_plan_required_for_ilc_consensus_core
commit_epoch_boundary_split_python_projection_rust_finality_required
commit_epoch_trigger_must_use_epoch_sequence_not_wall_clock
openclaw_nemoclaw_adapter_must_be_sidecar_or_cli_not_protocol_substrate
harness_adapter_transport_storage_protocols_required
generic_agent_harness_adapter_contract_required
localhost_sidecar_api_must_remain_loopback_or_transport_principal_auth
sidecar_dependency_isolation_required_for_harness_adapters
line_count_baseline_must_be_measured_not_estimated_before_public_rc
public_package_size_audit_required_before_openclaw_skill_launch

# Werner flow governor
werner_topological_flow_governor_forward_planning_recorded_phase_1238
werner_flow_governor_overlay_required_for_sim_fetch_01
server_shard_credit_flow_governor_required_pre_public_p2p
no_per_hop_ecu_micropayment_for_fetch_relay_preserved
flow_governor_cdl_required_before_runtime_policy_deployment
beta_decomposition_required_before_policy_use
flow_governor_must_not_replace_quality_reputation_mechanism
fetch_rate_limit_must_remain_circuit_breaker_until_authenticated_principal_credit_governor_cdl
flow_governor_spectral_trust_threshold_required_before_policy_use
heat_signal_must_not_directly_mint_ecu

# ECU creation and ILC settlement
agentic_wallet_ecu_credit_creation_runtime_required_pre_public_launch
werner_productive_credit_authorization_cdl_required
ecu_credit_creation_must_be_consensus_epoch_settled_not_wallet_mutation
ecu_to_ilc_conversion_execution_runtime_required_pre_public_launch
pe_governor_fixed_point_runtime_required_pre_public_launch
mandatory_conversion_sweeper_required_for_cdl_048_runtime
ecu_lot_accounting_required_for_cdl_048_conversion_sweeper
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
