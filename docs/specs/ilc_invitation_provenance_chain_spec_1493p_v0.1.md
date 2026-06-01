<!-- PUBLIC_RC_EXCLUDE -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Internal pre-public invitation/provenance planning. No public bundle serving or invitation economics are authorized. -->

# ILC Invitation Provenance Chain Spec - Phase 1493p

**Date:** 2026-06-01  
**Window:** 1489p-1497p  
**Phase:** 1493p  
**Status:** Internal spec complete  
**Sensitivity:** NON-SENSITIVE, private pre-public  
**Obligation closed:** OBL-014  

```text
invitation_provenance_chain_spec_committed_phase_1493p
```

---

## 1. Context

Invitation provenance is the future graph-native record that an invitee agent
was bootstrapped through protocol software or state served by an inviter agent.
The narrow chain is:

```text
inviter agent -> bundle serving receipt -> invitee birth / INIT record
```

This is not a social referral system and not a live reward path. It is a
precondition for any later inviter-attribution economics because the protocol
would need evidence of who served what, to whom, at which epoch, and under which
bundle or snapshot rule version before any future CDL could safely discuss ECU
credit.

The relevant current substrate is private and non-activating:

| Surface | Current state |
|---|---|
| ADR-0009 | Proposed; defines Layer 0 protocol bundle, Layer 1 genesis state bundle, Layer 2 epoch snapshots, and Layer 3 wire binding |
| `ilc_core/bundle/` | Private reference scaffold for Layers 0-3; each layer has its own `ADR_0009_LAYER*_NOT_PUBLIC_DISTRIBUTION = True` guard |
| ADR-0038 | Accepted Agent Birth Attestation; binds new `agent_id` to Genesis lineage but does not itself create wallet, ECU, ILC, or public authority |
| ADR-0041 | Accepted Agent INIT protocol; INIT is permissionless and zero public epistemic weight until attested |
| CDL-091 | Ratified jury incentive economics, but reviewer payment is not activated and invitation economics are not authorized |
| Harness receipts | ConsentGate, CoAttestationReceipt, and LocalImmutableStore can hold private local evidence only |

The closest planning authority is the Window 1459+ invitation/provenance lane:
ADR-0009 bundle-serving evidence plus SIM evidence would be prerequisites for a
future CDL-091 successor. Phase 1493p only writes the prerequisite design
surface.

---

## 2. Chain Structure

### 2.1 Inviter Agent Identity

The inviter must be an agent identity recognized by the protocol identity
surface, not a host, operator instance, endpoint, or social account. Existing
bundle code does not yet provide a full invitation identity schema:

- Layer 0 has no agent identity field; it is a protocol bundle artifact.
- Layer 1 can contain an initial agent roster, but that is a Genesis-state
  surface, not a post-Genesis invitation chain.
- Layer 2 commits epoch-state digests, not a serving provenance edge.
- Layer 3 has `sender_agent_id`, but that identifies a wire-message sender and
  is not by itself a serving receipt or invitation authority.

Therefore inviter identity for a future invitation record must be bound through
an explicit provenance record that references the serving agent, the served
bundle or snapshot, and the invitee birth or INIT artifact.

### 2.2 Bundle Serving Event

The serving event is the auditable act that an agent served a specific ADR-0009
bundle or snapshot to a bootstrapping agent. A future serving receipt should be
canonical and deterministic. At minimum it should bind:

| Field | Purpose |
|---|---|
| `serving_receipt_id` | Stable identifier for the serving event |
| `serving_agent_id` | Agent that served the bundle or snapshot |
| `served_layer` | ADR-0009 layer or layer set served |
| `layer0_protocol_bundle_sha256` | Protocol bundle commitment |
| `layer1_genesis_bundle_sha256` | Optional Genesis bundle commitment when served |
| `layer2_epoch_snapshot_sha256` | Optional epoch snapshot commitment when served |
| `layer3_wire_binding_sha256` | Optional wire-binding commitment when relevant |
| `serving_epoch` | Protocol epoch for the serving event, not wall-clock time |
| `serving_rule_version` | Rule version used to evaluate receipt validity |
| `co_attestation_receipt_ref` | Optional private or public co-attestation reference |
| `consent_decision_ref` | Optional local ConsentGate decision reference |

Layer 0 establishes what software/rules were served. Layer 1 and Layer 2 can
establish what initial or current graph state was supplied. Layer 3 can help
bind the wire-level sender, but future verifier semantics must not equate a
message sender with a rewardable serving agent without additional evidence.

### 2.3 Invitee Bootstrap

The invitee side should bind the serving event to a new agent birth or INIT
surface:

| Field | Purpose |
|---|---|
| `invitee_agent_id` | New agent identity |
| `agent_birth_attestation_ref` | ADR-0038 birth attestation reference |
| `agent_init_ref` | ADR-0041 INIT artifact reference |
| `identity_lineage_ref` | Provenance edge preserving CDL-042 flat `agent_id` namespace |
| `bootstrap_epoch` | Protocol epoch when the invitee bootstrap is recorded |

The chain must preserve ADR-0041 permissionlessness. An inviter may provide
software or state, but does not gain control over the invitee, does not grant
public epistemic weight, and does not create wallet, ECU, ILC, settlement, or
governance authority for the invitee.

### 2.4 Multi-Hop Chain Depth

Multi-hop invitation chains are recorded by linking a new invite to a prior
invite:

```text
A serves B -> invite_id=I1, invite_depth=1
B serves C -> invite_id=I2, parent_invite_id=I1, invite_depth=2
C serves D -> invite_id=I3, parent_invite_id=I2, invite_depth=3
```

Required future record fields:

| Field | Purpose |
|---|---|
| `invite_id` | Stable identifier for the invitation provenance record |
| `parent_invite_id` | Prior invitation record, if any |
| `inviter_agent_id` | Agent credited with serving/bootstrap evidence |
| `invitee_agent_id` | Agent that was bootstrapped |
| `serving_receipt_id` | Bundle or snapshot serving evidence |
| `bundle_hash` | Compatibility alias for the relevant ADR-0009 bundle digest |
| `serving_epoch` | Protocol epoch of serving evidence |
| `bootstrap_epoch` | Protocol epoch of invitee bootstrap |
| `invite_depth` | Derived depth from the root invitation record |
| `rule_version` | Canonical rule version for depth and validity calculation |

Depth must be computed from ratified graph state, not from user-supplied input.
A future verifier should reject cycles, inconsistent parent links, and records
whose parent chain exceeds a ratified maximum depth.

---

## 3. Current Implementation State

What exists today:

- ADR-0009 private Layer 0-3 bundle scaffolding exists in `ilc_core/bundle/`.
- Phase 1476p verified the ADR-0009 cross-layer chain at the private scaffold
  level.
- `ConsentGate` can approve private local artifacts and optionally write to
  `LocalImmutableStore`.
- `CoAttestationReceipt` can bind attestations to a private artifact hash.
- `MaintenanceTaskExecutor` can emit private query-response artifacts.

What is missing:

- no invitation provenance record schema;
- no serving receipt schema;
- no `invite_depth` computation;
- no parent-chain verifier;
- no binding from ADR-0038 birth attestation plus ADR-0041 INIT to an invitation
  record;
- no public verifier bridge for bundle-serving receipts;
- no public bundle serving activation;
- no ECU credit, wallet, settlement, treasury, or graph-write activation.

What must not be added in this phase:

- ECU credit logic;
- live invitation rewards;
- public bundle-serving incentives;
- public endpoint serving;
- CDL-091 successor runtime;
- any mutation of ADR-0009 status or the CDL register.

---

## 4. Forward Path to Inviter-Attribution Economics

A future CDL-091 successor would need to govern, at minimum:

| Surface | Required decision |
|---|---|
| Reward trigger | Whether reward is based on accepted downstream work, survival, review success, uptime, or another delayed outcome |
| Reward recipient | Which serving agent earns credit when there are multiple serving receipts |
| Hop count | Maximum invitation depth eligible for attribution |
| Decay and caps | Decay curve, per-hop cap, cluster cap, and anti-dominance bound |
| Time window | How long after bootstrap downstream work remains attributable |
| Evidence standard | Which serving receipts, INIT records, attestations, and downstream outcomes are sufficient |
| Fraud handling | Withheld reward, clawback, or fraud flag semantics |
| Double-counting | Relationship to maintenance, review, provenance, and backward-attribution rewards |
| Privacy boundary | Whether private sidecar receipts plus bounded disclosure are acceptable |

SIM evidence should precede any CDL opening. Required simulations include:

- bootstrap adoption and censorship-resilience effects;
- delayed downstream-value attribution;
- Sybil invitation-tree amplification;
- same-cluster mirror-farm invitation patterns;
- artificial productivity or self-dealing loops;
- sensitivity to depth caps, decay, reward windows, and cluster diversity.

CDL-093 maintenance lottery and invitation provenance are complementary but can
overlap. Maintenance lottery rewards reviewed maintenance work. Invitation
provenance would, if ever authorized, reward bootstrap service only when later
downstream value occurs. A future CDL must prevent the same artifact or agent
event from being counted twice across both surfaces.

---

## 5. Non-Authorizations

This spec does not:

- activate ECU credit on invitation;
- create, open, prelock, or ratify a CDL;
- mutate the CDL register;
- change ADR-0009 status from `Proposed`;
- authorize public bundle serving;
- authorize public package publication, public repository publication, public
  onboarding, public RC publication, or epoch transition;
- activate public graph writes, wallet writes, treasury writes, ECU minting, or
  ILC settlement;
- activate any agentic function endpoint or invitation-based economic credit;
- give an inviter authority over an invitee;
- treat Layer 3 `sender_agent_id` as rewardable invitation authority by itself.

Public bundle serving remains blocked. In the bundle layer, the active private
guards are the ADR-specific `ADR_0009_LAYER*_NOT_PUBLIC_DISTRIBUTION = True`
constants. Broader package and public-path code also retains public-RC
activation blockers. No agent can earn ECU from bundle serving until a future
CDL explicitly authorizes it.

---

## 6. Carry-Forward

OBL-014 is closed by this spec. Future work remains:

- write a concrete invitation provenance record schema only after a future
  phase authorizes schema work;
- produce SIM evidence before any CDL-091 successor opening;
- decide whether invitation-service attribution remains separate from backward
  attribution or composes with it under a later unified economic rule;
- keep public release routed through allowlist export and patent/counsel gates.
