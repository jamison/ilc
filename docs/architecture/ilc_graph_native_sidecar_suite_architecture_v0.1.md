# ILC Graph-Native Sidecar Suite Architecture v0.1

**Status:** Architecture planning constraint.
**Recorded:** 2026-05-10.
**Authority:** This document records forward architecture only. It does not
open Window 1303+, execute source export, publish a repository or package,
produce release artifacts, generate release keys or envelopes, mutate or sign
Genesis Atlas, sign v0.2, activate public claimability, activate public
P2P/fetch/sidecar serving, or authorize wallet/ECU/ILC economics.

```text
ilc_graph_native_sidecar_suite_architecture_recorded
ilc_graph_native_sidecar_suite_not_conventional_api_layer
openclaw_nemoclaw_are_hosts_not_protocol_substrates
essential_openclaw_rc_sidecars_truth_projection_claimability_bridge
graph_native_sidecar_creation_routed_to_forward_windows_1303_1342
sidecar_suite_public_serving_remains_blocked_until_explicit_authority
confidential_coordination_sidecar_suite_routed_to_phases_1307_1311_1324_1329
confidential_coordination_sidecar_suite_not_public_rc_blocker_by_default
truth_primitive_sidecar_boundary_recorded_phase_1308
public_rc_exclude_helper_disposition_inventory_recorded_phase_1308
transport_principal_lifecycle_policy_local_substrate_phase_1309
transport_principal_public_path_not_activated_phase_1309
public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1
rust_public_p2p_substrate_gate_status_recorded_phase_1313
public_p2p_default_off_phase_1313
public_fetch_serving_default_off_phase_1313
transport_public_path_activation_not_authorized_phase_1313
phase_1314_wallet_withdrawal_transfer_spend_preflight_next
public_rc_remains_blocked_after_phase_1313
wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1
wallet_withdrawal_transfer_spend_not_activated_phase_1314
wallet_signing_ledger_write_not_authorized_phase_1314
public_claimability_user_action_boundary_recorded_phase_1314
wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314
phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next
public_rc_remains_blocked_after_phase_1314
ilc_native_harness_recipe_model_recorded
harness_function_sets_sidecar_boundaries_recorded
ilc_harness_hosts_sidecar_suite_not_protocol_substrate
```

## 1. Architecture Correction

The ILC harness boundary should not be understood as a conventional API layer
placed on top of ILC. The stronger ILC-native framing is a graph-native sidecar
suite: local, harness-agnostic sidecars that materialize ILC graph operations
for agents.

OpenClaw, NemoClaw, Codex-style agents, and a future first-party ILC harness are
hosts or operators of the suite. They are not protocol substrates and do not
define protocol truth.

The suite consumes and emits ILC-native objects:

- truth primitive submissions and graph-output contracts;
- encrypted or gated shard headers, commitments, and capability references;
- sidecar projection queries and bounded canonical exports;
- claimability receipts, proof-binding checks, replay/nullifier evidence, and
  verifier results;
- TransportPrincipal lifecycle, admission, replay, ban, and rate-limit state;
- sealed D2d payload envelopes where later authorized;
- package-profile manifests and explicit non-claims.

This preserves the accepted protocol-vs-harness boundary while avoiding a weak
"wrapper API" model.

## 2. Suite Elements

| Sidecar | Graph-native role | First planning target | Public posture |
|---------|-------------------|-----------------------|----------------|
| Sidecar registry and manifest | Declares suite components, package profile, required capabilities, authority gates, non-claims, and deterministic export metadata. | Phase 1307-style package/profile hardening. | Local/package metadata only; no serving authority. |
| Truth primitive submission sidecar | Builds and validates `assert.truth`, `validate.claim`, `contradict.assert`, `refute.claim`, `revise.assert`, and `link.claim` submissions against ratified wire/runtime contracts. | Phase 1307/1308-style graph-native local sidecar contract. | Local only until persistence/network gates are separately authorized. |
| Local graph and memory projection sidecar | Presents local graph/memory/query projections using bounded sidecar query runtime and public-safe field classification. | Phase 1311/1312-style projection implementation and privacy tests. | In-process or loopback/private only; public serving remains gated. |
| Claimability and receipt verifier sidecar | Verifies receipts, settled roots, wallet-root bindings, canonical hashes, exact numerics, replay/nullifier evidence, and duplicate-claim policy. | Phase 1305/1306-style offline verifier and negative-path corpus; Phase 1323 profile dry run. | No public API or claim endpoint without explicit activation authority. |
| OpenClaw/NemoClaw bridge sidecar | Lets third-party harnesses call the graph-native suite through local imports, CLI subprocesses, or loopback/private sidecar calls. | Phase 1323-style OpenClaw/NemoClaw claimable profile dry run. | Harness host only; OpenClaw/NemoClaw are not protocol dependencies. |
| TransportPrincipal admission sidecar | Materializes transport identity lifecycle, revocation, replay cache, admission, ban, rate-limit, and privacy policies. | Phase 1309/1310-style lifecycle and hostile-network tests. | Public path remains blocked until TransportPrincipal and public transport gates close. |
| Public fetch/P2P readiness sidecar | Records default-off public fetch/P2P readiness, Rust substrate gate evidence, Python HTTP devnet/test classification, and explicit non-activation state. | Phase 1313 default-off readiness candidate. | No public P2P, public fetch serving, listener, peer discovery, non-loopback bind, or public transport activation authority. |
| Private/gated shard sidecar | Manages encrypted coordination nodes, shard headers, capability-token references, access grants, revocations, and private-to-public promotion evidence. | Parallel post-essential suite lane after the OpenClaw-compatible essentials are stable. | Planning/runtime gated; no plaintext public disclosure claim. |
| Sealed sender sidecar | Constructs fixed-size sealed D2d payloads and relay instructions for privacy-preserving delivery where later authorized. | Future H-013/H-015 lane after public transport substrate decisions. | Not part of first public RC unless explicitly pulled in and audited. |
| Confidential coordination profile | Bundles private/gated shard, capability/membership, sealed sender delivery, gossip announce/pull, jitter/cover policy, and harness bridge sidecars into a local/private coordination suite. | Phase 1307 manifest profile, Phase 1311/1312 projection prerequisites, and Phase 1324-1329 implementation/dry-run lane. | Private/local by default; not a public confidential-messaging claim without Phase 1337/1341 authority. |
| Wallet-facing value-action semantics preflight sidecar | Records read-only wallet-facing query operations and blocks provider-facing withdrawal, transfer, spend, signing, ledger-write, public claim endpoint submission, and external chain destination collection until explicit authority. | Phase 1314 preflight. | Local preflight only; no wallet write, signing, claim endpoint, or settlement activation. |
| Value-path activation boundary preflight sidecar | Records local read-only ECU/ILC/wallet substrates and blocks ECU minting, ILC settlement, withdrawal runtime, wallet writes, public claim endpoint, public claimability activation, release materialization, CDL-088, and value-path activation until explicit authority. | Phase 1315 preflight. | Local preflight only; no ECU minting, no ILC settlement, no withdrawal runtime, no wallet write, and no value-path activation. |
| Ledger-truth value-action sidecar | Materializes claim, transfer, spend, ECU minting, settlement, and withdrawal requests against ILC ledger/graph/receipt truth only after authority gates close. Wallet providers remain adapters around this substrate. | Phase 1338-style economics gate after Phase 1314/1315 preflights. | Blocked by default; no wallet write or settlement activation from the suite name alone. |
| ILC wallet recipe profile | Composes wallet-provider adapter, signing-intent/payload binding, ledger-truth value-action validation, receipt/history presentation, and recovery/export portability sidecars into an optional ILC-native wallet profile. | After Phase 1315 settlement-boundary work, and before any Phase 1338-style activation gate if explicitly selected. | Not a first-RC blocker by default; no monolithic wallet embedded in core. |
| Contributor sidecar SDK/conformance pack | Lets external contributors build sidecars against deterministic manifest, schema, privacy, and non-claim rules. | After first private OpenClaw/NemoClaw dry run, or later public contributor window. | Requires publication/export authority before external release. |

## 3. Essential First Path

The first useful OpenClaw-style RC path should be the smallest graph-native
suite that lets a harness use ILC without becoming ILC:

1. sidecar registry and deterministic manifest;
2. truth primitive submission sidecar;
3. local graph/memory projection sidecar;
4. offline claimability and receipt verifier sidecar;
5. OpenClaw/NemoClaw bridge sidecar over local imports, CLI, or private
   loopback/Tailscale wiring.

That set supports private DigitalOcean OpenClaw droplet testing while preserving
the current non-authorization boundaries: no public P2P, no public sidecar
serving, no public claim endpoint, no source publication, and no release/signing
authority.

Phase 1307 implements the first element as deterministic local/package metadata
at `ilc_core/sidecars/registry_manifest.py` and records the executable packet
in `docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md`.
It declares OpenClaw/NemoClaw-compatible local bridge profiles, a claimable
local bridge profile bound to the offline verifier sidecar, and
`confidential_coordination_local_preview` as private/local only.

Phase 1308 records the truth primitive submission boundary as local
graph-native sidecar infrastructure and updates the registry entry for
`truth_primitive_submission_boundary` with
`truth_primitive_sidecar_boundary_recorded_phase_1308`. It also maps all
current runtime `PUBLIC_RC_EXCLUDE` helpers to `replace_before_export`, so the
suite remains package-clean by replacement/materialization rather than by
flipping internal helper flags.

Phase 1309 implements the local TransportPrincipal admission sidecar lifecycle
substrate at `ilc_core/sidecars/transport_principal_admission.py` and updates
the registry entry for `transport_principal_admission` to
`lifecycle_substrate_recorded_phase_1309_tests_hardened_phase_1310`. Phase 1310
then hardens hostile-network negative paths for local revocation, replay,
admission, ban, rate-limit, and privacy behavior:
`revocation_replay_admission_ban_tests_phase_1310.v0.1`,
`transport_principal_revocation_replay_tests_hardened_phase_1310`,
`admission_ban_rate_privacy_tests_hardened_phase_1310`, and
`hostile_network_public_path_still_blocked_phase_1310`. This is a
local graph-native substrate only: no public P2P, no public fetch serving, no
public sidecar/projection serving, no public credential issuer authority, no
public revocation registry activation, no public replay cache activation, no
public rate-limit state activation, no non-loopback bind, no listener, no peer
discovery, no wallet withdrawal, no ECU minting, and no ILC settlement are
authorized.

Phase 1311 implements the local graph/memory projection sidecar substrate at
`ilc_core/sidecars/local_graph_memory_projection.py` and updates the registry
entry for `local_graph_memory_projection` to
`local_projection_substrate_implemented_phase_1311_privacy_tests_hardened_phase_1312`.
It records `local_graph_memory_projection_sidecar_phase_1311.v0.1`,
`public_safe_projection_implementation_local_only_phase_1311`,
`confidential_coordination_projection_reference_local_only_phase_1311`, and
`public_sidecar_projection_serving_not_enabled_phase_1311`.

Phase 1312 hardens that substrate with `projection_privacy_field_filtering_tests_phase_1312.v0.1`,
`projection_privacy_filters_hardened_phase_1312`,
`confidential_coordination_projection_non_leakage_tests_phase_1312`,
`public_sidecar_projection_serving_not_enabled_phase_1312`,
`phase_1313_public_fetch_p2p_activation_candidate_default_off_next`, and
`public_rc_remains_blocked_after_phase_1312`. The implementation now includes
an export-level raw-fragment leak guard for accidental identifier, membership,
route, plaintext, wallet, stake, economic, or graph-position leakage inside
otherwise allowed string values. This is local-only projection infrastructure:
no public sidecar/projection serving, no non-loopback bind, no public listener,
no peer discovery, no public confidential messaging, no public confidential
coordination serving, no wallet withdrawal, no ECU minting, and no ILC
settlement are authorized.

Phase 1313 records `public_fetch_p2p_readiness_candidate` in the sidecar
registry and implements the default-off readiness packet at
`ilc_core/sidecars/public_fetch_p2p_readiness.py`. It records
`public_fetch_p2p_activation_candidate_default_off_phase_1313.v0.1`,
`rust_public_p2p_substrate_gate_status_recorded_phase_1313`,
`public_p2p_default_off_phase_1313`,
`public_fetch_serving_default_off_phase_1313`,
`transport_public_path_activation_not_authorized_phase_1313`,
`phase_1314_wallet_withdrawal_transfer_spend_preflight_next`, and
`public_rc_remains_blocked_after_phase_1313`. The packet records Rust
QUIC/rustls source evidence from `ilc_consensus/src/network.rs`, but it keeps
the Rust public-P2P substrate gate unsatisfied by default and classifies Python
HTTP fetch/gossip as devnet/test only. It does not authorize public P2P, public
fetch serving, public listener, peer discovery, non-loopback bind, public
sidecar/projection serving, TransportPrincipal public-path activation,
wallet-facing withdrawal requests, ECU minting, or ILC settlement. Phase 1314
has now completed as preflight-only wallet-facing value-action boundary work.

Phase 1314 records `wallet_action_semantics_preflight` in the sidecar registry
and implements the preflight packet at
`ilc_core/sidecars/wallet_action_semantics_preflight.py`. It records
`wallet_withdrawal_transfer_spend_semantics_preflight_phase_1314.v0.1`,
`wallet_withdrawal_transfer_spend_not_activated_phase_1314`,
`wallet_signing_ledger_write_not_authorized_phase_1314`,
`public_claimability_user_action_boundary_recorded_phase_1314`,
`wallet_provider_agnostic_not_ledger_truth_agnostic_phase_1314`,
`phase_1315_ecu_minting_ilc_settlement_boundary_preflight_next`, and
`public_rc_remains_blocked_after_phase_1314`. The packet preserves the
read-only public wallet runtime surface and blocks wallet-facing withdrawal
requests, wallet-facing transfer requests, wallet-facing spend requests,
wallet-provider signing requests, wallet-provider ledger-write requests, public
claim endpoint submission, external chain destination collection, ECU minting,
and ILC settlement. It also locks the interpretation that wallets are adapters or
sidecars around ILC truth, while ledger state, graph state, receipts, settled
roots, wallet-root bindings, claimability proofs, and deterministic sidecar
manifests remain the authoritative truth objects.

Phase 1315 adds the local value-path activation boundary preflight sidecar at
`ilc_core/sidecars/value_path_activation_boundary_preflight.py`. It records
`ecu_minting_ilc_settlement_boundary_preflight_phase_1315.v0.1`,
`ecu_minting_not_authorized_phase_1315`,
`ilc_settlement_not_authorized_phase_1315`,
`value_path_activation_boundary_recorded_phase_1315`,
`phase_1316_window_1303_1316_closure_audit_next`, and
`public_rc_remains_blocked_after_phase_1315`. The packet preserves local
read-only substrates while recording no ECU minting, no ILC settlement, no
withdrawal runtime, no wallet-facing withdrawal request, no wallet-facing
transfer request, no wallet-facing spend request, no wallet-provider signing
request, no wallet-provider ledger-write request, no public claim endpoint, no
public claimability activation, and no value-path activation. Phase 1316 is
sensitive and requires explicit `GO Phase 1316`.

The stronger sidecars, especially private/gated shards, sealed sender,
TransportPrincipal public-path controls, and ledger-truth value-action sidecars,
should continue in parallel after the essential suite is testable. If an
ILC-native wallet is selected later, it should be a sidecar recipe/profile over
that substrate, not a monolithic wallet inside the core ledger runtime.

## 4. Confidential Coordination Suite

The Confidential Coordination Sidecar Suite is the graph-native private
coordination path. It should be framed as a local/private suite, not as a
Signal clone and not as a default first-RC public product claim.

The suite composition is:

1. confidential coordination profile in the sidecar registry;
2. private/gated shard sidecar;
3. capability, membership, grant, and revocation sidecar;
4. sealed sender delivery sidecar;
5. gossip announce/pull plus jitter and cover-policy sidecar;
6. OpenClaw/NemoClaw or equivalent confidential bridge sidecar.

Specific phase routing:

| Phase | Assignment |
|-------|------------|
| 1307 | Add `confidential_coordination_local_preview` to the sidecar registry/manifest design with explicit non-claims and private wiring modes. |
| 1311/1312 | Complete for local projection prerequisites: local graph/memory projection can represent private/gated shard headers and encrypted coordination-node references, and Phase 1312 tests harden deny-by-default filtering against plaintext, membership, route-history, sealed-payload, raw identifier, wallet, stake, economic, and graph-position leakage. |
| 1324 | Private/gated shard sidecar contract and encrypted coordination-node envelope. |
| 1325 | Capability, membership, grant, revocation, and optional ZK-membership proof interface boundaries. |
| 1326 | Sealed sender local delivery sidecar boundary using H-013/H-015 seams, fixed-size payload handling, and no-public-P2P defaults. |
| 1327 | Gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis negative tests with no anonymity-guarantee claim. |
| 1328 | Private OpenClaw/NemoClaw or equivalent DigitalOcean droplet dry run over loopback, Tailscale, or other private wiring. |
| 1329 | Closure decision: post-RC/private lane, selected public-RC blocker, or later dedicated window. |

Detailed routing is recorded in
`docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md`.

## 5. Forward Planning Routing

The forward routing should be:

- Phase 1305/1306 class: build and harden the local claimability/receipt
  verifier sidecar substrate.
- Phase 1307 class: define the graph-native sidecar registry, manifest, and
  OpenClaw-compatible essential-suite package profile.
- Phase 1308 class: reconcile `PUBLIC_RC_EXCLUDE` helper replacement/stripping
  with truth primitive sidecar and public-safe local suite boundaries. This is
  now recorded as helper-disposition metadata and local truth-boundary metadata;
  no export or public serving authority is opened.
- Phase 1309/1310 class: Phase 1309 now implements the local
  TransportPrincipal admission sidecar lifecycle substrate without public
  activation; Phase 1310 now hardens revocation, replay, admission, ban,
  rate-limit, and privacy negative-path tests while public path remains blocked.
- Phase 1311/1312 class: implement local graph/memory projection sidecar and
  privacy/filtering tests.
- Phase 1313 class: record default-off public fetch/P2P readiness and Rust
  substrate gate status without public transport activation.
- Phase 1314 class: record wallet-facing value-action semantics preflight
  without wallet-facing withdrawal, transfer, spend, signing, ledger-write,
  public claim endpoint, ECU minting, or ILC settlement activation.
- Phase 1315 class: record ECU/ILC value-path activation boundary preflight
  without ECU minting, ILC settlement, withdrawal runtime, wallet writes,
  public claim endpoint, public claimability activation, or value-path
  activation.
- Phase 1338 class: if selected, route the optional ILC wallet recipe
  profile as sidecar composition over the ledger-truth value-action substrate,
  not as a separate wallet source of truth.
- Phase 1322/1323 class: run private DigitalOcean/OpenClaw/NemoClaw dry runs
  against the essential graph-native suite, not against bespoke harness code.
- Phase 1324-1329 class: route the Confidential Coordination Sidecar Suite as a
  private/local lane after the essential OpenClaw-compatible suite is testable.
  It is not a public-RC blocker unless explicitly selected by a later sequence
  lock.
- Phase 1324+ or parallel lane: continue contributor sidecar SDK work if it is
  not selected as first-RC blocker.
- Phase 1333+ class: export only a clean materialized source tree whose sidecar
  components have no `PUBLIC_RC_EXCLUDE` markers or stripped-helper imports.

## 6. ILC-Native Harness Recipe Model

The post-OpenClaw direction is not to copy OpenClaw as a monolith. The ILC-native
harness should be a recipe host over this graph-native sidecar suite:

```text
ilc-harness
  recipe_manifest
  agent_loop_orchestrator
  provider_runtime_adapters
  local_workspace_memory
  operator_consent_queue
  sidecar_recipe_modules
```

Each sidecar recipe must declare:

- `recipe_id`
- required `ilc_core/` surfaces
- required authority gates
- public/private/default-off posture
- storage roots and bounded export paths
- graph node types it may create locally
- publication path and consent requirement
- anti-gaming and duplicate-suppression policy if it can create maintenance work

The initial recipe families should be:

| Recipe family | Modules | Purpose |
|---------------|---------|---------|
| Capture | `LocalNodeCapture`, `ConsentGate`, hash-separation tests | Capture raw model/tool outputs as local content-addressed nodes without automatic publication |
| Provider usage | OpenAI, Anthropic, Gemini/local fallback adapters | Read scheduling signals and local counters without turning quota state into protocol truth |
| Maintenance | `star.map.embedding`, `contradiction.sweep`, `graph.compression`, `stability.simulation` | Execute review-lane / maintenance-lottery tasks under Werner CDL authority gates |
| Operator UX | approval inbox, budget/status panel, pending-publication queue, identity status | Give humans control over spend, publication, and identity state |
| Coordination function sets | task offers, task reservations, result availability, receipt/claimability availability, peer health, sealed/private coordination | Coordinate work and availability without bypassing TransportPrincipal, public P2P, verifier, or CCSS gates |
| Distribution | recipe-pack verifier, profile conformance tests, installer/update checks | Ship plug-and-play modules without mixing harness code into protocol core |

### Harness coordination function-set boundaries

Harness coordination function sets are sidecar-level operator surfaces. They may
later use local IPC, private Tailscale wiring, D2D gossip, or another authorized
transport, but the function set is not itself a transport commitment. These
function sets are not consensus, not economic proof, and not a replacement for
review-lane admission.

| Function set | What it may carry | What it must not carry by default |
|--------------|-------------------|-----------------------------------|
| `task_offer_coordination` | task_id, task_type, bounded task envelope hash, expiry epoch | private keys, provider quota, automatic credit claim |
| `task_reservation_coordination` | operator_agent_id, task_id reservation, duplicate-suppression token | public admission claim or settlement-grade proof |
| `task_result_availability` | result CID/local ref, reviewer fetch hint, consent status | raw private payload unless publication consent exists |
| `receipt_claimability_availability` | verifier receipt hash, nullifier status ref, claimability proof availability | wallet secrets, transfer/spend authority, settlement activation claim |
| `peer_health_diagnostics` | bounded diagnostics, reachability, queue capacity | provider quota as protocol truth or reputation score |
| `sealed_private_coordination` | encrypted/padded announce-pull envelopes | plaintext membership, route history, sender identity leakage |

These recipes make the future first-party ILC harness OpenClaw-style at the user
layer while preserving the core rule: OpenClaw, NemoClaw, Codex, Claude Code, and
`ilc-harness` are hosts or operators of the graph-native suite, not protocol
substrates.

## 7. Non-Claims

This architecture document does not authorize:

- Window 1303+ execution;
- sidecar public serving;
- public projection endpoint serving;
- public claimability API activation;
- public confidential messaging;
- public verifier service;
- public P2P or public fetch serving;
- OpenClaw/NemoClaw as protocol substrate;
- source allowlist export execution;
- public repository publication;
- public package publication;
- release artifact production;
- release-key generation;
- release envelope production;
- public RC claim;
- wallet-facing withdrawal, transfer, spend, ECU minting, or ILC settlement;
- Genesis Atlas mutation, regeneration, or signing;
- v0.2 signing;
- CDL mutation or CDL-088 opening;
- IP filing or paper publication.
