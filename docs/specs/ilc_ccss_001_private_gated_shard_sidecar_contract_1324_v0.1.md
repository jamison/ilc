# ILC CCSS-001 Private/Gated Shard Sidecar Contract 1324 v0.1

Status: implemented / local-only / no public confidential coordination serving
Date: 2026-05-13
Phase: 1324
Owner lane: Confidential Coordination Sidecar Suite / CCSS-001

Required tokens:

```text
ccss_001_private_gated_shard_sidecar_contract_phase_1324.v0.1
encrypted_coordination_node_envelope_contract_recorded_phase_1324
shard_header_projection_contract_recorded_phase_1324
private_to_public_promotion_evidence_shape_recorded_phase_1324
ccss_public_serving_not_enabled_phase_1324
phase_1325_ccss_capability_membership_boundary_next
public_rc_remains_blocked_after_phase_1324
```

Phase 1324 was executed after explicit human authorization:

```text
GO Phase 1324
```

This phase adds a deterministic local-only substrate at
`ilc_core/sidecars/confidential_coordination_shard.py`. It records the
CCSS-001 contract for opaque `PrivateShardRef`, encrypted coordination-node
envelopes, safe shard-header projections, private-to-public promotion evidence
references, and explicit disclosure denials.

## 0. Discovery Discipline

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | The Phase 1324 prompt was validated and every required token was initially present only in the executable prompt. The tokens are now carried into code, tests, spec, walkthrough, STATUS, PLANNING_INDEX, Capsule v5.54, Roadmap v1.1, the forward packaging/signing plan, and the CCSS forward plan. |
| Section 0b Concept-discovery search | Searched CCSS, Confidential Coordination Sidecar Suite, private shard, gated shard, encrypted coordination-node, envelope, shard header, projection, promotion evidence, private-to-public, local graph, memory projection, public confidential coordination serving, public P2P, Phase 730, and CDL-038. MemPalace advisory hits pointed to older private-promotion and gated-shard discussion; direct repo reads used the current Phase 730 and CDL-038 artifacts as canon. |
| Section 0c Contradiction and non-claim search | Confirmed that Phases 1324-1328 are the CCSS private/local lane, not Atlas-G tail work. ATLAS-G-007 through ATLAS-G-010 remain carried forward outside this phase. No source grants public confidential coordination serving, public P2P, public sidecar serving, public promotion, source publication, release signing, wallet action, ECU minting, ILC settlement, Genesis mutation/signing, CDL mutation, or CDL-088 opening. |
| Section 0d Source expansion | Direct-read PLANNING_INDEX, STATUS tail, Capsule v5.54, Window 1317-1329 sequence lock/guidance, forward packaging/signing plan, CCSS forward plan, Phase 730 gated-shard hardening, CDL-038 promotion ratification evidence, Phase 1311/1312 local projection code/tests, and sidecar registry code. |

Standing discovery token:

```text
unknown_unknown_discovery_required_before_phase_execution
```

## 1. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1324 is sensitive and requires explicit GO | `docs/antigravity_tasks/antigravity_prompt__phase_1324_g8_ccss_001_private_gated_shard_sidecar_contract.md` | confirmed |
| Phase 1324 owns CCSS-001 private/gated shard contract only | Phase 1324 prompt, CCSS forward plan, forward packaging/signing plan | confirmed |
| Atlas-G tail must not be hidden inside CCSS phases | `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | confirmed |
| Phase 730 records the older private/gated header and capability-token planning surface | `docs/specs/ilc_private_gated_shard_header_and_capability_token_contract_hardening_730_v0.1.md` | confirmed |
| CDL-038 requires successor-node plus promotion receipt without automatic reputation carry-forward | `docs/specs/ilc_cdl_038_private_to_public_promotion_and_promotion_receipt_ratification_evidence_353_v0.1.md` | confirmed |
| Phase 1311/1312 local projection already supports opaque private/gated shard header refs and encrypted coordination refs | `ilc_core/sidecars/local_graph_memory_projection.py` and Phase 1311/1312 tests | confirmed |
| Public confidential coordination serving is blocked | CCSS forward plan, Capsule v5.54, sidecar registry | confirmed |

## 2. Implemented Contract Surface

The new module provides:

- `ccss_001_required_tokens()`
- `ccss_001_private_gated_shard_manifest()`
- `build_private_shard_ref()`
- `build_encrypted_coordination_node_envelope()`
- `build_shard_header_projection()`
- `build_promotion_evidence_ref()`
- `build_disclosure_denial()`
- `validate_ccss_001_record()`
- `validate_ccss_001_manifest()`
- `export_ccss_001_record_json()`

The named record aliases are:

- `PrivateShardRef`
- `EncryptedCoordinationNodeEnvelope`
- `ShardHeaderProjection`
- `PromotionEvidenceRef`
- `DisclosureDenial`

All exports use canonical JSON with deterministic ordering:

```text
json.dumps(..., sort_keys=True, allow_nan=False, separators=(",", ":"))
```

The validator rejects floats, cycles, tuples, non-string keys, excessive depth,
excessive node count, oversized text, ASCII control characters, excessive
canonical JSON byte size, unexpected record keys, wrong digest prefixes,
digest/hash drift, pre-Genesis epoch 0, and authorization-flag drift.

Phase 1324 Fix1 records implementation-audit hardening:

```text
phase_1324_fix1_ccss_001_shard_contract_hardening.v0.1
ccss_001_epoch_zero_rejected_phase_1324_fix1
ccss_001_canonical_json_byte_cap_enforced_phase_1324_fix1
ccss_001_ref_list_count_prechecked_phase_1324_fix1
ccss_001_phase_1325_membership_ref_false_positive_removed_phase_1324_fix1
```

## 3. PrivateShardRef

`PrivateShardRef` is an opaque local/private shard reference. It records:

- `private_shard_ref`
- `genesis_lineage_ref`
- `root_commitment_ref`
- `gate_control_ref`
- `access_policy_ref`
- `visibility_mode`
- `routing_scope`
- `label_policy`

The contract intentionally excludes participant names, `creator_agent_id`,
AgentIDs, wallet IDs, Tailscale identities, OpenClaw identities, IP addresses,
and harness identities. Labels are bounded to:

```text
opaque_refs_only_no_identity_labels
```

## 4. EncryptedCoordinationNodeEnvelope

`EncryptedCoordinationNodeEnvelope` records only ciphertext references and
encryption metadata:

- `envelope_ref`
- `private_shard_ref`
- `shard_header_ref`
- `capability_policy_ref`
- `disclosure_denial_ref`
- `encryption_scheme_ref`
- `ciphertext_digest_ref`
- `ciphertext_storage_ref`
- `ciphertext_size_bytes`
- `ciphertext_size_class`
- `envelope_epoch`

The marker is:

```text
encrypted_payload_digest_only
```

The transport marker is:

```text
opaque_ref_only_ciphertext_digest
```

The envelope does not carry plaintext bytes, membership, route history, sender,
recipient, capability contents, raw sealed payloads, wallet material, seed
material, mnemonic material, private keys, or identity fields. The current size
bound is 1 MiB per ciphertext reference for this contract. `envelope_epoch`
must be positive; epoch 0 is rejected as pre-Genesis.

## 5. ShardHeaderProjection

`ShardHeaderProjection` is the safe local projection surface. It carries:

- `private_shard_ref`
- `shard_header_ref`
- `root_commitment_ref`
- `capability_policy_ref`
- `disclosure_denial_ref`
- sorted `encrypted_coordination_refs`
- sorted `promotion_evidence_refs`
- `envelope_count`
- `header_epoch`
- `projection_sha256`

It is compatible with the Phase 1311 projection record kind:

```text
private_gated_shard_header
```

The projection is local-header-only and must not reveal plaintext body,
membership list, route history, sender identity, recipient identity, capability
contents, wallet identity, AgentID, IP address, harness identity, or raw sealed
payload content. `header_epoch` must be positive, `envelope_count` must match
the encrypted coordination refs, and zero-envelope shard-header projections are
rejected rather than treated as placeholders.

## 6. PromotionEvidenceRef

`PromotionEvidenceRef` records evidence shape only. It does not promote content,
publish content, create a public successor node, materialize a promotion receipt,
or claim public availability.

The shape preserves CDL-038:

```text
successor_node_plus_promotion_receipt_without_automatic_reputation_carry_forward
```

The record carries opaque references for:

- source private shard;
- source shard header;
- original private-node commitment;
- successor public-node candidate;
- disclosed lineage;
- promotion epoch.

`promotion_epoch` must be positive; epoch 0 is rejected as pre-Genesis.

It enforces:

- no public promotion;
- no private content reveal;
- no public availability claim;
- no promotion execution;
- no materialized promotion receipt;
- no automatic public corroboration carry-forward;
- no automatic public reputation carry-forward.

## 7. DisclosureDenial

`DisclosureDenial` records the field-denial contract. Denied fields include
plaintext body, membership list, route history, sender identity, recipient
identity, capability contents, AgentID/agent_id, wallet_id, Tailscale identity,
OpenClaw identity, harness identity, client IP, identity seed, mnemonic, private
key, and secret material.

The denial record is allowed to name those forbidden fields only as a denial
list. Other CCSS-001 records reject those fields or fragments.

## 8. Registry Impact

The sidecar registry now records:

```text
confidential_coordination_private_gated_shard
```

with authority gate:

```text
phase_1324_private_local_contract_only
```

and implementation status:

```text
contract_recorded_phase_1324_no_public_serving
```

The `confidential_coordination_local_preview` profile now requires this sidecar
alongside `confidential_coordination_local_preview`, `local_graph_memory_projection`,
and `openclaw_nemoclaw_local_bridge`.

This is package/profile metadata plus local validation only. It is not public
confidential coordination serving, public P2P, public projection serving, source
publication, package publication, OpenClaw skill publication, ClawHub listing,
release artifact production, release key/envelope work, release signing, or a
public RC claim.

Short non-claim shorthand: no public confidential coordination serving, no
public P2P, no public promotion, no source publication, no release signing.

## 9. Non-Claims

Phase 1324 does not authorize:

- public RC claim or public launch claim;
- source export execution, source publication, package publication, clean public tree materialization, or public repository publication;
- release artifact production, release-key generation, release envelope production, release signing material, signature, or release signing;
- Genesis Atlas mutation, regeneration, signing, v0.2 signing, ATLAS-G-007, ATLAS-G-008, ATLAS-G-009, or ATLAS-G-010;
- CDL mutation or CDL-088 opening;
- identity artifact creation, genesis record creation, seed commitment creation, `identity_seed_commitment` creation, dummy Agent Birth artifact creation, identity-seed generation, mnemonic generation, private-key generation, secret-store write, or seed/mnemonic/private-key disclosure;
- public confidential coordination serving, public confidential messaging, public sidecar serving, public projection endpoint serving, public P2P, public fetch serving, public listener, peer discovery, non-loopback bind, or public registry serving;
- public promotion, private-to-public promotion execution, promotion receipt materialization, private content reveal, public availability claim, automatic public corroboration carry-forward, or automatic public reputation carry-forward;
- wallet-facing withdrawal request, wallet-facing transfer request, wallet-facing spend request, wallet-provider signing, wallet-provider ledger-write, wallet write, withdrawal runtime, ECU minting, ILC settlement, or value-path activation.

## 10. Next Gate

Phase 1325 is sensitive and requires explicit `GO Phase 1325`.

```text
phase_1325_ccss_capability_membership_boundary_next
```

Phase 1325 should define the capability/membership boundary that CCSS-001 only
references here. It must keep membership private, avoid plaintext disclosure,
and avoid public serving/P2P activation unless a later prompt explicitly opens
that authority. CCSS-001 rejects literal `membership_list` and member-agent
disclosures while avoiding a broad substring ban on the word `membership`;
Phase 1325 may define opaque membership-boundary references, but those references
must not disclose actual membership, participant identity, route history, or
capability contents through CCSS-001 records.
