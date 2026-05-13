# ILC CCSS-002 Capability Membership Grant Revocation Boundary 1325 v0.1

**Phase:** 1325
**Date:** 2026-05-13
**Status:** local/private capability and membership boundary recorded; no public serving

```text
ccss_002_capability_membership_grant_revocation_boundary_phase_1325.v0.1
private_shard_access_control_boundary_recorded_phase_1325
membership_plaintext_disclosure_forbidden_phase_1325
optional_zk_interface_boundary_recorded_phase_1325
phase_1326_ccss_sealed_sender_boundary_next
public_rc_remains_blocked_after_phase_1325
```

## 1. Purpose

Phase 1325 defines the CCSS-002 local/private access-control boundary for
private and gated confidential-coordination shards. It gives CCSS-001 shard
headers a deterministic place to point for capability policy, opaque
membership boundary, grant evidence, revocation evidence, and optional
ZK-membership interface references.

The implementation lives at:

```text
ilc_core/sidecars/confidential_coordination_capability.py
```

It is a local validation substrate. It is not a public membership service, a
public credential authority, a public confidential coordination server, a ZK
verifier, a public P2P route, or a public RC launch claim.

## 2. Canon And Source Basis

| Source | Phase 1325 use |
|--------|----------------|
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | Routes CCSS-002 as capability, membership, grant, revocation, and optional ZK proof interface boundary with no plaintext disclosure or public membership leak. |
| `docs/specs/ilc_ccss_001_private_gated_shard_sidecar_contract_1324_v0.1.md` | Establishes CCSS-001 opaque private-shard references and says CCSS-002 may define membership-boundary references without leaking membership. |
| `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_hardening_730_v0.1.md` | Establishes capability-token reference model and keeps full custody, cryptography, delivery, and enterprise-policy mechanics deferred. |
| `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_candidate_v0.1.md` | Provides the planning surface for access grants, target shard, scope, validity epochs, revocation reference, and signature without implementing business logic. |
| `docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md` | Keeps private/local use lightweight and discontinuous from public legitimacy until explicit promotion/public evaluation. |
| `docs/specs/ilc_transport_principal_lifecycle_revocation_replay_preflight_1295_v0.1.md` | Preserves public-path blockers for lifecycle, revocation, replay, admission, ban, rate-limit, and privacy authority. |

## 3. Record Surfaces

The Phase 1325 substrate defines these local-only record surfaces:

| Record | Purpose | Public posture |
|--------|---------|----------------|
| `CapabilityPolicyRef` | Records access states, fail-closed conditions, hash inputs, local policy inputs, and revocation precedence. | Opaque local policy ref only. |
| `MembershipBoundaryRef` | Records membership root and proof references as opaque commitments. | No member list, participant identity, or member count disclosure. |
| `CapabilityGrantRef` | Records an opaque capability grant reference bound to shard, policy, membership boundary, proof ref, scope, epoch window, and local sequence. | Candidate evidence only until local state resolves it. |
| `CapabilityRevocationRef` | Records revocation evidence for a grant and capability. | Revocation wins over grant; no revocation reason disclosure. |
| `ZKMembershipInterfaceRef` | Records a seam for future ZK membership proof verification. | No proving system ratified, no witness disclosure, no proof payload disclosure, no public verifier. |
| `CapabilityAccessDecision` | Local helper output for access-state resolution. | Local-only decision object, not a public credential or public receipt. |

Each machine-verifiable record uses deterministic JSON:

```text
json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))
```

Each ref is derived from the canonical record body with SHA-256 and a
record-specific prefix.

## 4. Access-State Model

The local access state machine has exactly these states:

| State | Meaning | Access |
|-------|---------|--------|
| `unknown` | No grant evidence, unreadable grant evidence, or malformed grant evidence. | Deny. |
| `candidate_granted` | Grant evidence exists but shard, membership, replay, and revocation state have not resolved to active local access. | Deny. |
| `active_local` | Grant evidence matches requested shard and capability, membership boundary resolves, grant is current, no replay blocker exists, no supersession exists, and no matching revocation exists. | Allow local-only access. |
| `revoked` | Matching revocation evidence exists or revocation evidence is malformed in a fail-closed path. | Deny. |
| `expired_or_superseded` | Current epoch is outside the grant window or caller-supplied local supersession state contains the capability ref. | Deny. |
| `zk_deferred` | Optional ZK seam exists but no ratified verifier is active. | Deny. |

Revocation wins over grant evidence. Unknown, malformed, replayed,
cross-shard, expired, superseded, and ZK-deferred capability states deny.

## 5. Hash Inputs, Local Policy Inputs, And Metadata

Hash inputs include the local/private refs and deterministic epoch/sequence
fields that define the record:

- private shard ref;
- membership boundary ref;
- capability policy ref;
- opaque capability ref;
- opaque membership proof ref;
- grant or revocation sequence;
- validity epochs;
- access-state and ordering-model declarations.

Local policy inputs are caller-supplied and not protocol authority by
themselves:

- current epoch;
- local replay collection;
- local supersession collection;
- local revocation evidence;
- local membership-boundary record.

The module intentionally does not use wall-clock time as protocol authority.
Ordering is epoch plus local sequence only.

## 6. Disclosure Boundary

The contract rejects plaintext or identity-bearing material in CCSS-002 records.
Forbidden material includes:

- `AgentID`, `agent_id`, bearer identity, grantor identity, grantee identity,
  harness identity, OpenClaw identity, Tailscale identity, wallet identity, and
  client IP;
- member-agent identifiers, participant identifiers, membership lists, raw
  membership material, raw grants, raw capabilities, route history, sender or
  recipient identity;
- plaintext payloads, raw sealed payloads, secret material, identity seeds,
  mnemonics, private keys, ZK witnesses, and revocation reasons.

The false disclosure flags themselves are allowed as boundary metadata. Their
values must remain false. They do not disclose the underlying private material.

## 7. Optional ZK Seam

The ZK surface is an interface boundary only:

- `proof_system_ref` is an opaque reference, not a ratified proving system;
- `zk_proof_ref` is an opaque reference, not an inline proof payload;
- `proving_system_ratified` must be false;
- `public_verifier_enabled` must be false;
- `witness_material_disclosed` must be false;
- `proof_payload_disclosed` must be false;
- access resolution through this seam returns `zk_deferred`.

No public ZK claim, public verifier, anonymity guarantee, or membership-proof
validity claim is made in Phase 1325.

## 8. Registry Integration

The sidecar registry now records:

```text
confidential_coordination_capability_membership_boundary
```

under:

```text
phase_1325_private_local_contract_only
```

The `confidential_coordination_local_preview` profile now requires this sidecar
alongside the CCSS-001 private/gated shard contract, local graph/memory
projection, local preview profile metadata, and OpenClaw/NemoClaw local bridge.

This is package/profile metadata and local validation only.

## 9. Non-Claims

Phase 1325 does not authorize:

- public RC claim or public launch claim;
- source export execution, source publication, package publication, clean public
  tree materialization, or public repository publication;
- release artifact production, release-key generation, release envelope
  production, release signing material, signature, or release signing;
- Genesis Atlas mutation, regeneration, signing, v0.2 signing, ATLAS-G-007,
  ATLAS-G-008, ATLAS-G-009, or ATLAS-G-010;
- CDL mutation or CDL-088 opening;
- identity artifact creation, genesis record creation, seed commitment
  creation, `identity_seed_commitment` creation, dummy Agent Birth artifact
  creation, identity-seed generation, mnemonic generation, private-key
  generation, secret-store write, or seed/mnemonic/private-key disclosure;
- public confidential coordination serving, public confidential messaging,
  public membership directory, public credential authority, public capability
  directory, public revocation registry, public verifier service, public sidecar
  serving, public projection endpoint serving, public P2P, public fetch serving,
  public listener, peer discovery, non-loopback bind, or public registry serving;
- public promotion, private-to-public promotion execution, promotion receipt
  materialization, private content reveal, public availability claim, automatic
  public corroboration carry-forward, or automatic public reputation
  carry-forward;
- wallet-facing withdrawal request, wallet-facing transfer request,
  wallet-facing spend request, wallet-provider signing, wallet-provider
  ledger-write, wallet write, withdrawal runtime, ECU minting, ILC settlement,
  or value-path activation.

Short non-claim shorthand: no public confidential coordination serving, no
public P2P, no public membership directory, no public credential authority, no
public ZK verifier, no source publication, no release signing.

## 10. Next Gate

Phase 1326 is sensitive and requires explicit `GO Phase 1326`.

```text
phase_1326_ccss_sealed_sender_boundary_next
```

Phase 1326 should define the sealed-sender local delivery boundary without
public P2P activation or public confidential coordination serving.
