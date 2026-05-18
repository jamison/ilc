# ADR-0039: Validator Endpoint Registry

**Status:** Accepted
**Date:** 2026-05-18
**Phase:** 1386b
**Author:** Jamison and Codex
**Dependencies:** CDL-017, CDL-068, CDL-078, ADR-0038, CDL-090, Phase 1360 Fix2a, Phase 1386a

```text
validator_endpoint_registry_adr_ratified_phase_1386b
quic_endpoint_epoch_scoped_signed_edge_defined
read_only_projection_contract_defined_phase_1386b
no_hardcoded_peer_list_production_activation_path_phase_1386b
```

---

## Context

Phase 1360 proved checkpoint ingestion and local commit across four independently
running validators, but the proof was explicitly scoped to directly injected
checkpoints and did not prove durable peer-to-peer BFT sessions. Phase 1360 Fix2a
recorded the production connectivity model: direct QUIC first, relay fallback
second, a graph-native endpoint registry, and persistent sessions per topology
epoch.

Phase 1386a proved the production TLS gRPC read path. Phase 1386b defines the
validator endpoint registry architecture needed before Phase 1386c can prove
persistent QUIC connectivity.

Hardcoded peer lists are not acceptable in any production activation path because
validator endpoints can rotate, operators can redeploy, and CDL-068 topology
shuffle changes which validators should communicate during a topology epoch.

## Decision

ILC defines `QUIC_ENDPOINT` as an epoch-scoped signed edge on an existing
`agent_id` node. The graph is the canonical validator endpoint registry. A
runtime projection may exist only as a bounded read-only cache rebuilt from
signed graph edges for the current topology epoch.

The endpoint registry is not a mutable external database, not a hardcoded IP
list, and not a Genesis configuration restart mechanism.

## Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1386a production TLS gRPC proof is complete | `docs/phases/STATUS.md`; `docs/specs/ilc_production_tls_grpc_proof_1386a_v0.1.md` | confirmed |
| Durable connectivity model exists | `docs/research/ilc_validator_connectivity_production_model_v0.1.md` | confirmed |
| CDL-068 governs topology shuffle epoch scoping | CDL-068 register row and ratification evidence | confirmed |
| CDL-078 governs relay incentive layer | CDL-078 register row and ratification evidence | confirmed |
| ADR-0038 defines Genesis-rooted birth attestation | `docs/adr/ADR_0038_Agent_Birth_Attestation.md` | confirmed |
| CDL-090 identity bootstrap is ratified | CDL-090 register row and ratification evidence | confirmed |
| Phase 1360/Fix2a durable peer-to-peer proof remains out of scope | STATUS and Fix2a prompt/planning hits | confirmed |

## `QUIC_ENDPOINT` Edge Representation

`QUIC_ENDPOINT` is an edge from a validator's existing `agent_id` node to a
connectivity claim payload. CDL-017 established validators as agents; this ADR
does not create a new validator identity namespace.

Minimum payload fields:

```json
{
  "address": "<dns-name-or-ip-literal>",
  "edge_type": "QUIC_ENDPOINT",
  "endpoint_kind": "direct|relay",
  "epoch_signed": "<topology-epoch-number>",
  "port": "<u16>",
  "protocol_version": "<ilc-quic-consensus-version>",
  "signature": "<signature-ref-over-canonical-payload>",
  "signer_agent_id": "<validator-agent-id>",
  "topology_epoch": "<cdl-068-topology-epoch>"
}
```

The signature binds the canonical payload to `signer_agent_id`. The signing
authority comes from ADR-0038 Agent Birth Attestation plus CDL-090 identity
bootstrap. ADR-0038 Agent Birth Attestation plus CDL-090 identity bootstrap is
the endpoint-claim identity authority. CDL-088 governs public claimability authority
and is not endpoint claim signing authority.

## Endpoint Forms

### Direct QUIC Endpoint

Direct form is the preferred production path for reachable validator operators.

Required fields:

```text
endpoint_kind=direct
address=<dns-name-or-ip-literal>
port=<u16>
protocol_version=<ilc-quic-consensus-version>
topology_epoch=<cdl-068-topology-epoch>
signature=<signature-ref-over-canonical-payload>
```

### CDL-078 Relay Endpoint

Relay form is a fallback representation for NAT, macOS, home, or other operators
that cannot maintain direct inbound QUIC reachability.

Required fields:

```text
endpoint_kind=relay
relay_agent_id=<relay-agent-id>
relay_address=<dns-name-or-ip-literal>
relay_port=<u16>
relay_mode=pass_through_consensus_quic
relay_incentive_ref=CDL-078
target_validator_agent_id=<validator-agent-id>
topology_epoch=<cdl-068-topology-epoch>
signature=<signature-ref-over-canonical-payload>
```

Relay mode is pass-through transport for consensus QUIC. It must not terminate
and re-origin consensus messages as graph-content relay. If CDL-078 needs a
transport-relay amendment or sibling CDL before production activation, Phase
1386c must record that as a blocker or bounded deferral.

## Epoch Scoping

`topology_epoch` means the period between CDL-068 topology shuffles. It is not a
wall-clock epoch and not a generic consensus epoch unless the active topology
runtime binds those counters explicitly.

Every `QUIC_ENDPOINT` edge is valid only for the current topology epoch. On each
CDL-068 topology shuffle:

1. The previous projection is invalidated.
2. The current validator set is recomputed from the signed topology state.
3. Signed `QUIC_ENDPOINT` edges are read for the current validator set only.
4. A fresh read-only projection is rebuilt.
5. Stale edges from prior topology epochs are ignored for connection selection.

## Update Propagation

Endpoint update propagation does not require Genesis restart. A validator updates
its endpoint by publishing a new signed `QUIC_ENDPOINT` edge for the current
topology epoch.

Propagation path:

```text
validator signs endpoint edge
    -> signed edge is gossiped over the ratified announcement path
    -> receivers verify ADR-0038/CDL-090 identity authority
    -> receivers verify topology_epoch matches current CDL-068 topology epoch
    -> read-only projection is rebuilt from the accepted signed edge snapshot
```

This ADR names the intended propagation path as signed edge gossip compatible
with the existing announcement lane. It does not implement runtime gossip, public
P2P serving, endpoint publication, or production validators.

## Read-Only Projection Contract

The production runtime may use an in-memory projection for fast lookup, but only
under this contract:

- The graph remains canonical.
- The projection is derived from signed graph edges only.
- The projection is bounded to the current topology epoch's validator set.
- The projection is invalidated and rebuilt on each CDL-068 topology shuffle.
- The projection output must be deterministic and canonical-hashable.
- The projection must never acquire write/update/set/insert/delete methods
  outside full rebuild from signed graph edges.
- The projection must not accept environment variables, config overrides,
  hardcoded peer lists, or ad hoc endpoint refresh as endpoint authority.
- A stale projection must not outlive its topology epoch.

If a future implementation introduces `set_endpoint`, `update_endpoint`,
`insert_endpoint`, `delete_endpoint`, `write_endpoint`, partial mutation, or an
equivalent endpoint mutation method on the projection, it violates this ADR.

## Hardcoded Peer List Prohibition

No hardcoded peer list may appear in any production activation path.

Allowed pre-production uses:

- local test fixtures,
- private testnet harness configuration,
- one-shot diagnostic scripts,
- gitignored operator-local staging files.

Production activation must derive peer endpoints from signed `QUIC_ENDPOINT`
edges and the current CDL-068 topology epoch. Hardcoded peer lists are not a
fallback.

Hardcoded peer lists are not a fallback.

## Relationship To Existing Canon

CDL-068 governs validator topology selection and topology shuffle cadence. This
ADR uses CDL-068 to scope endpoint validity by topology epoch; it does not
change CDL-068 topology law.

CDL-078 governs relay incentives. This ADR defines the relay endpoint form for
future consensus QUIC fallback; it does not activate relay service.

ADR-0038 plus CDL-090 provide identity authority for endpoint-claim signatures.
A Phase 1360 Fix2a planning note used CDL-088 terminology for public identity
attestation. That wording is stale. CDL-088 governs public claimability, not
endpoint-claim signing authority.

CDL-017 remains the validator admission and validator-as-agent anchor. This ADR
does not create new validator admission law.

## Phase 1386c Acceptance Requirements

Phase 1386c must verify or explicitly defer with authority:

- persistent direct QUIC sessions can be selected from the projection;
- relay fallback is selected only from signed `QUIC_ENDPOINT` relay payloads;
- no hardcoded peer list exists in any production activation path;
- no write/update/set/insert/delete methods exist on the projection;
- stale topology-epoch projections are rejected;
- projection rebuild requires a signed edge snapshot and current topology epoch.

## Non-Goals

This ADR does not:

- mutate the CDL register;
- mutate runtime source;
- implement Phase 1386c;
- activate production validators;
- activate public P2P;
- activate public gRPC serving;
- activate CDL-078 relay service;
- publish endpoint claims publicly;
- authorize production topology shuffle activation;
- authorize wallet, ECU, ILC, settlement, value-path, or public claimability behavior.

## Discovery Notes

| Discovery pass | Result |
|----------------|--------|
| §0a Known-token audit | Phase 1386a proof token exists; ADR-0038/CDL-090 tokens exist; output tokens only appeared in the Phase 1386b/1386c/1387 prompts before this ADR. |
| §0b Concept-discovery search | Found the Phase 1360 Fix2a connectivity model and current research note; both point to `QUIC_ENDPOINT` edge semantics and read-only projection. |
| §0c Contradiction and non-claim search | Found the required prohibition against mutable projections and hardcoded peer lists; no production activation authority found. |
| §0d Source expansion | Direct-read the connectivity research note, ADR-0038, CDL-068, CDL-078, CDL-090, STATUS, PLANNING_INDEX, sequence lock, and candidate grouping. |
| MemPalace | Attempted advisory retrieval; query was stopped because the local wrapper did not return promptly. Current-worktree direct reads are controlling. |

## Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/adr/ADR_0039_Validator_Endpoint_Registry.md -> validator-connectivity/endpoint-registry-adr
```
