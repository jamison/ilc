# ILC CDL-101 D2D Signed Gossip Envelope Ratification Evidence 1572a v0.1

Status: ratification evidence committed
Date: 2026-07-06
Phase: 1572a
CDL: CDL-101
Ratification token: `cdl_101_ratified`
Public RC status: blocked
Runtime activation status: private receiver verification wired, public path blocked

## 1. CDL-101 Identity And Dependency Token

CDL-101 is the D2D Signed Gossip Envelope successor governance surface for
CDL-061. It binds static transport peer identity, key identifier, routing
context, domain, envelope version, algorithm, and payload hash inside a
canonical ML-DSA-65 signed context before receiver-side verification.

Dependency token:

```text
cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1
```

Ratified CDL register row:

```text
CDL-101 | D2D Signed Gossip Envelope (CDL-061 successor) | ratified | phase_1572a | cdl_101_ratified
```

## 2. Ratification Basis

Phase 1572 committed receiver-side verification and recorded the required
attack-class tests. The focused Phase 1572 receiver-verification test file
passed all nine required cases:

1. `test_valid_envelope_accepted`
2. `test_forged_sender_peer_id`
3. `test_body_tamper`
4. `test_routing_field_tamper`
5. `test_replay_detected`
6. `test_actor_binding_mismatch`
7. `test_invalid_packet_does_not_poison_replay_cache`
8. `test_unverifiable_peer_buffered`
9. `test_expired_key_rejected`

The Phase 1572 adjacent transport/registry/startup suite also passed with
89 tests. The repository-wide `python -m pytest -q` command remains blocked
before execution by pre-existing sidecar package/import-name conflicts:
`ilc-timecapsule-sidecar` has an unresolved import path and duplicate CCSS test
module names exist between sidecar tests and root tests. This is not recorded
as a Phase 1572 receiver-verification failure.

## 3. Implementation Completeness

Phase 1571 deliverables confirmed:

- `ilc_core/crypto/pq_signature_verify.py` defines the fail-closed
  `verify_mldsa65_signature()` helper and exposes
  `CDL_101_SIGNED_ENVELOPE_DEPENDENCY`.
- `GossipPeerRegistry` supports structured peer entries with `peer_id`,
  `mldsa_pubkey_hex`, `key_id`, `valid_from_epoch`, `valid_until_epoch`, and
  `authorized_actor_ids`.
- Backward-compatible plain-string peer entries remain loadable and explicitly
  unverifiable.

Phase 1572 deliverables confirmed:

- `gossip_transport.py` now requires `ILC-Sender-Peer-Id` and `ILC-Key-Id`.
- `http_gossip_transport_runtime.py` reconstructs the 11-field canonical
  signed context before buffering.
- Structured peers with public keys are ML-DSA-65 verified.
- Replay cache entries are recorded only after key validity, signature
  verification, and actor-binding checks pass.
- Authority-bearing gossip types enforce explicit `claimed_actor` membership
  in `authorized_actor_ids`.

## 4. Spec Decisions Locked

| Decision | Chosen value | Phase 1570 token |
|---|---|---|
| Signing scheme | `canonical_json_v1` | `d2d_envelope_decisions_locked_phase_1570` |
| Governance form | `cdl061bis_successor` | `d2d_envelope_decisions_locked_phase_1570` |
| Signed context | 11 exact fields serialized with `json.dumps(sort_keys=True, separators=(",", ":"), allow_nan=False)` | `signed_d2d_envelope_spec_committed_phase_1570` |
| Replay identity | `(peer_id, key_id, epoch, gossip_type, channel, payload_sha256)` | `d2d_envelope_decisions_locked_phase_1570` |
| Actor binding | `peer_id_maps_to_authorized_actor_ids` | `d2d_envelope_decisions_locked_phase_1570` |
| Delegation | out of scope for v1 | `d2d_envelope_decisions_locked_phase_1570` |

## 5. Governance Form

CDL-101 is ratified as a CDL-061 successor surface, not as a retroactive edit
to CDL-061. The CDL-061 ratified row is not modified by Phase 1572a.

Governance form:

```yaml
governance_form: cdl061bis_successor
```

## 6. CDL-039 Compatibility

`ILC-Sender-Peer-Id` is a static transport peer-registry slot. It is not a
creator agent ID, graph node ID, authorship claim, public CCSS anonymity claim,
or public unlinkability claim.

CDL-101 preserves the CDL-039 forbidden-header boundary:

- `ILC-Creator-Agent-Id` remains forbidden.
- `ILC-Node-Id` remains forbidden.
- `creator_agent_id` remains forbidden.
- `node_id` remains forbidden.

The receiver treats `ILC-Sender-Peer-Id` and `ILC-Key-Id` as routing hints
until the reconstructed signed context verifies against the registry public
key.

## 7. TLA+ Forward Obligation

Forward obligation token:

```text
tla_plus_obligation_delegation_key_rotation_safety
```

Scope: delegation chains where one peer signs on behalf of another actor, and
key-rotation overlap windows where old-key-signed packets arrive after a
registry update. This is not a Phase 1572a ratification blocker because v1
delegation is out of scope and Phase 1572 records static key-validity checks.

## 8. Ratification Verdict

Verdict: `cdl_101_ratified`

CDL-101 is ratified in Phase 1572a on the basis of the Phase 1570 spec,
Phase 1571 key/verify infrastructure, and Phase 1572 receiver-verification
implementation and attack-class tests.

## 9. Pre-Public-RC Clearance Note

CDL-101 is now ratified and may be treated by Phase 1575
PUBLIC-RC-GATE-001 as the load-bearing private D2D transport authentication
governance surface.

This evidence does not authorize public RC, public P2P, public relay serving,
wallet writes, treasury writes, settlement, minting, Genesis signing, epoch
transition, or any production guard clearance. Public transport remains
blocked under the separate CCSS-004 and OBL-047 boundary decisions.
