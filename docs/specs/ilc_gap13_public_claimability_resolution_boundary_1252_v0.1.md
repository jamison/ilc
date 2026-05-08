# ILC Gap 13 Public Claimability Resolution Boundary 1252 v0.1

Status: locked
Date: 2026-05-08
Phase: 1252
Owner lane: G8 public-RC blocker lane

`gap13_claimability_resolution_boundary_phase_1252.v0.1`
`public_claimability_runtime_not_activated_phase_1252`
`epoch_commit_settlement_not_agent_manual_claim_default_phase_1252`
`phase_1252_digest_truncation_security_binding_classification_recorded`
`phase_1252_gap13_claimability_boundary_complete`

## 1. Purpose and non-activation boundary

This packet defines the Gap 13 public-claimability resolution boundary for the
`openclaw_skill_claimable` public-RC target. It is a boundary and dependency
inventory, not a runtime activation.

The controlling rule remains:

```text
rc0_1_balance_visibility_does_not_imply_public_claimability
ecu_accrual_reaches_ilc_balance_only_through_epoch_commit
wallet_visibility_and_accounting_only
no_public_claimability_or_spend_in_lifecycle_spec
```

Phase 1252 does not activate public claimability, wallet withdrawal, ILC
transfer, spend authority, ECU mint authority, public repository publication,
public RC, release keys, release envelopes, v0.2 signing, CDL mutation, or
public P2P exposure.

## 2. Canon lineage verified in this phase

| Source | Direct-read conclusion |
|--------|------------------------|
| `docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md` | Phase 1252 is sensitive, requires `GO Phase 1252`, and must not activate public claimability, wallet withdrawal, ILC transfer, release keys, public launch, or public RC. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Public economic claimability remains a blocker for the final OpenClaw/NemoClaw claimable profile. |
| `docs/specs/ilc_rc0_1_settlement_wallet_boundary_lock_576_v0.1.md` | Wallet visibility is read-only accounting. Signing, spend, transfer, and withdrawal semantics are deferred. |
| `docs/specs/ilc_ecu_to_ilc_lifecycle_contract_spec_615_v0.1.md` | ECU is productive-credit layer; ILC is hard settlement asset; visible `balance_ilc` is delayed post-epoch-commit evidence only. |
| `ilc_core/ledger/ecu_ilc_lifecycle_runtime.py` | `commit_settled_epoch()` materializes internal visible ILC balance and keeps `claimability_state` as `deferred`. |
| `ilc_core/protocol/public_wallet_runtime.py` | Public wallet status/history/export/summary are GET/read-only surfaces with full settled root and receipt references, and `claimability_state` remains `deferred`. |
| `ilc_core/rc/package_profiles.py` | `openclaw_skill_claimable` declares public claimability as a target component, but Phase 1251 package CI recorded runtime activation as false. |
| `ilc_consensus/` | Rust consensus surfaces include BLS, QUIC/rustls, fixed-point micro-ECU, epoch checkpoint, and owned-object transfer machinery, but no public claimability activation. |

MemPalace was used only as advisory retrieval support. It returned
`docs/research/ilc_rc_gap_context_pack_v0.1.md` and
`docs/research/ilc_mysticeti_implementation_lane_m_series_v0.1.md`; both were
direct-read before use. The research context confirms historical emphasis on
Genesis monetary authority, CDL-048 mandatory conversion, fixed-point micro-ECU
in Rust, and a read-only Python path, but repo canon above controls this packet.

## 3. Resolution model

Public claimability must be derived from settled runtime roots and epoch
resolution, not from agent-specific manual claims.

Default decision:

```text
epoch_commit_settlement_not_agent_manual_claim_default_phase_1252
```

The lifecycle is:

1. ECU accrual is recorded in the bounded productive-credit layer.
2. Epoch settlement closes through the canonical epoch-commit path.
3. Internal visible ILC balance is materialized by settled runtime state.
4. Public wallet surfaces expose read-only accounting, receipt refs, and settled
   root refs while `claimability_state` remains `deferred`.
5. A future public claimability runtime may consume canonical settled roots and
   proofs, but the future participant request does not itself determine
   entitlement.

CDL-048 mandatory conversion remains a future runtime requirement. The canon
records a 4 issuance-epoch conversion deadline; under the current one-month
issuance epoch cadence this is a four-month rolling window. That deadline is a
network/governance resolution rule over ECU after it exists. It is not an agent-authored manual entitlement claim.

## 4. Future public claimability requirements

Before `openclaw_skill_claimable` may be used as a public-RC claimable profile,
the future claimability runtime must specify and verify:

- Full settled runtime root proof, including wallet-state root, latest balance
  receipt, history digest, epoch identifier, and canonical agent identity.
- Full SHA-256 or stronger security-binding digest fields for any claim proof,
  settlement proof, incident proof, signer-lineage proof, and release manifest.
- Exact numeric ECU and ILC contracts with no float at value boundaries and
  explicit non-finite rejection before arithmetic.
- Replay and double-claim prevention keyed by canonical epoch, agent identity,
  wallet root, and claimability state transition.
- Rust/chain settlement substrate selection for the public claim path, including
  whether `ilc_consensus` or a later substrate is the public verifier.
- BLS/PQ/release-key and signer-lineage rules for public claims, compromise
  response, recovery, key rotation, and release-envelope signing.
- TransportPrincipal or another authenticated transport boundary for any
  non-loopback public claim API.
- Privacy and audit treatment for public balance proofs, public receipts, and
  serving-peer or agent identifiers.
- Counsel/IP/allowlist readiness before public repository publication or public
  RC claim.

Phase 1252 records these requirements only. It does not implement a public claim endpoint, withdrawal endpoint, spend endpoint, transfer endpoint, or chain bridge.

## 5. Chain, cryptography, and Rust dependency inventory

| Dependency area | Current repo state | Public claimability implication |
|-----------------|--------------------|---------------------------------|
| Rust settlement substrate | `ilc_consensus` contains Rust types, LMDB balance store, BLS validation, QUIC/rustls networking, and epoch checkpoint storage. | Candidate substrate evidence exists, but public claimability still needs an explicit selected verifier path and public-claim proof contract. |
| Exact economic units | Rust uses `u64` micro-ECU; Python lifecycle runtime uses `Decimal` and finite checks. | Future public claimability must preserve exact integer or Decimal value boundaries and must not introduce float settlement state. |
| Epoch settlement | `EpochSettlementProtocol::process_epoch_checkpoint()` verifies BLS aggregate signatures before storing epoch records. | Public claimability should consume epoch-root proofs, not ad hoc agent statements. |
| Public wallet runtime | Python public wallet surfaces expose read-only roots and receipts. | Suitable visibility/input surface, but not authority to claim, spend, withdraw, or transfer. |
| Key/fingerprint migration | Canon bundle signing emits 16-char key IDs and full 64-char key fingerprints; asymmetric-required mode requires the fingerprint. | Full fingerprints are already the binding identity path. The short key ID remains a compatibility alias until a separate migration changes it. |
| Compromise and lineage runtime | Phase 1252 hardens incident, recovery, and lineage event IDs to full SHA-256. | Claimability proofs can reference non-truncated security/audit identifiers. |
| Public transport identity | TransportPrincipal remains future Phase 1253 work. | Any non-loopback public claimability API remains blocked until authenticated transport identity is specified. |

## 6. Phase 1250 Fix1 digest truncation classification

`RCGAP-1250-FIX1-003` is resolved by this classification and scoped hardening.
The Phase 1250 Fix1 scan found 11 truncation candidates total. Eight
ledger/security candidates were routed to Phase 1252 and are classified below.
Three network/transport candidates remain outside this phase and carry forward
to Phase 1253 under `RCGAP-1250-FIX1-004`.

| Candidate | Classification | Phase 1252 disposition |
|-----------|----------------|------------------------|
| `ilc_core/ledger/canon_bundle_key_registry.py:267` `_derive_key_id()` | Already-covered compatibility alias | Left unchanged. Full `key_fingerprint` exists and is checked by signing verification; changing key ID length would be a compatibility migration. |
| `ilc_core/ledger/canon_bundle_key_registry.py:636` backup `content_hash` | Storage/display-only | Left unchanged. It names local backup files and is not used as a security root or settlement proof. |
| `ilc_core/ledger/canon_bundle_key_registry_channel_signing.py:54` `_derive_key_id()` | Already-covered compatibility alias | Left unchanged. Channel sidecars include full `key_fingerprint`; asymmetric-required mode requires it. |
| `ilc_core/ledger/canon_bundle_utils.py:23` `derive_key_id()` | Already-covered compatibility alias | Left unchanged for current manifest compatibility; full `derive_key_fingerprint()` remains binding. |
| `ilc_core/ledger/settlement_verification.py:56` `input_hash` | Security/audit-binding evidence hash | Hardened in Phase 1252 to full SHA-256 over canonical JSON with `sort_keys=True`, compact separators, and `allow_nan=False`. |
| `ilc_core/security/key_compromise_runtime.py:248` `incident_id` | Security-binding incident identifier | Hardened in Phase 1252 to full SHA-256. |
| `ilc_core/security/key_compromise_runtime.py:261` `recovery_attestation` | Security-binding recovery attestation | Hardened in Phase 1252 to full SHA-256. |
| `ilc_core/security/signer_lineage_runtime.py:350` `event_id` | Security-binding signer-lineage event identifier | Hardened in Phase 1252 to full SHA-256. |

The network/transport-adjacent digest candidates from Phase 1250 Fix1 are not
closed here:

- `ilc_core/network/d2d/gossip.py:181` `channel_tag`
- `ilc_core/network/d2d/spectral_beacon.py:207` requester `agent:` digest
- `ilc_core/network/star_map/star_map_route_index_runtime.py:120` route-index ngram digest

They remain routed to Phase 1253 with
`phase_1253_transport_digest_and_rust_m5_disposition_recorded` because their
correct classification depends on TransportPrincipal and public-P2P substrate
requirements rather than the Gap 13 wallet/settlement claimability boundary.

## 7. Explicit non-claims and carry-forward

`RCGAP-1250-FIX1-006` is dispositioned as a sensitive boundary record, not as a
claimability activation.

Carry-forward blockers:

- Public claimability runtime remains required before final public RC.
- CDL-048 conversion sweeper remains required before public conversion runtime.
- TransportPrincipal remains required before public P2P and any non-loopback
  public claimability API.
- CDL-087 production-candidate fetch evidence and ratification remain open.
- ATLAS-G public-RC graph reachability gate remains open.
- Counsel/IP/allowlist and release-key authorization remain open.
- v0.2 signing remains deferred pending explicit signing authorization.

Graph delta:

```text
graph_delta=load_bearing_spec_added:docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md -> ecu/ilc/public_rc
graph_delta=load_bearing_code_changed:ilc_core/ledger/settlement_verification.py -> ecu/ilc/security
graph_delta=load_bearing_code_changed:ilc_core/security/key_compromise_runtime.py -> security
graph_delta=load_bearing_code_changed:ilc_core/security/signer_lineage_runtime.py -> security
```
