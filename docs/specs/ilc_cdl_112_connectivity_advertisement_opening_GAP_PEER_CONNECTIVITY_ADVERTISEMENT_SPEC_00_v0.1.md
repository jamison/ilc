# CDL-112 ConnectivityAdvertisement Opening

**Phase:** GAP-PEER-CONNECTIVITY-ADVERTISEMENT-SPEC-00  
**Date:** 2026-08-30  
**Status:** RATIFIED  
**Opening token:** `cdl_112_opened_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_SPEC_00`  
**Ratification phase:** GAP-CDL-112-RATIFY-00  
**Ratification date:** 2026-09-09  
**Ratification token:** `cdl_112_connectivity_advertisement_ratified_GAP_CDL_112_RATIFY_00`  
**Schema version:** `connectivity_advertisement_cdl112.v0.1`

## Authority Context

CDL-112 is the ratified constitutional lane for `ConnectivityAdvertisement`, a signed peer connectivity advertisement schema that can carry richer reachability information than CDL-103 `PeerAdvertisement` v1.

CDL-112 is not a CDL-103 amendment. CDL-103 remains the ratified authority for `peer_advertisement_cdl103.v0.1`, including ML-DSA-65 signatures, bounded TTL, curated bootstrap fallback, deterministic introduction sampling, and anti-eclipse mitigation targets. CDL-112 is a separate CDL governing a new schema version whose public gossip path remains behind `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED=True` until explicit guard clearance.

Related authority and planning sources:

- CDL-103: Dynamic Peer Discovery Protocol.
- ADR-0039: Validator Endpoint Registry and direct-first relay-fallback principle.
- CDL-078: Relay/rendezvous serving authority context.
- GAP-CONNECTIVITY-RECONCILE-00: connectivity path taxonomy.
- GAP-RELAY-RENDEZVOUS-SPEC-00: relay rendezvous semantics.

## Purpose

The proposed schema lets an agent advertise its current connectivity posture without granting validator admission, relay incentives, serving rewards, reputation credit, or endpoint authority. A `ConnectivityAdvertisement` is a signed discovery hint. It is not a validator endpoint assertion and cannot supersede CDL-105 or ADR-0039 authority.

The intended uses are:

- Advertise whether the agent is direct-public, NAT-traversed, relay-assisted, outbound-only, local-only, validator-direct, validator-relay, validator-observer-direct, or validator-observer-relay.
- Carry one preferred transport endpoint plus a bounded list of candidate endpoints for controlled connectivity attempts.
- Reference local probe or relay-slot evidence without embedding secrets or unbounded network metadata.
- Preserve CDL-103 privacy-bounded slice-digest and epoch TTL constraints while preparing a richer v2 discovery surface.

## Canonical Fields

The ratified v0.1 schema uses this top-level shape:

```json
{
  "schema_version": "connectivity_advertisement_cdl112.v0.1",
  "body": {
    "agent_id": "<96 lowercase hex chars>",
    "protocol_version": "<string>",
    "installed_slices_digest": "<privacy-bounded digest>",
    "content_availability_count": 0,
    "peer_timestamp_epoch": 0,
    "ttl_epochs": 1,
    "connectivity_mode": "<ConnectivityMode value>",
    "transport_endpoint": {},
    "relay_endpoint": null,
    "candidate_list": [],
    "probe_receipt_ref": null,
    "relay_slot_ref": null
  },
  "key_binding_ref": "<key binding reference>",
  "ml_dsa_signature": "<ML-DSA-65 signature hex>"
}
```

The current guarded runtime representation is implemented by GAP-PEER-CONNECTIVITY-ADVERTISEMENT-IMPL-00. Public gossip activation remains deferred to GAP-CONNECTIVITY-ADVERTISEMENT-ACTIVATE-00.

## Field Constraints

`connectivity_mode` must be one of the ratified or opened connectivity-mode vocabulary values used by the Part 3l connectivity lane: `local_only`, `outbound_only`, `relay_candidate`, `relay_reachable`, `direct_public`, `nat_traversed_direct`, `validator_observer_direct`, `validator_observer_relay`, `validator_direct`, or `validator_relay`, subject to the final implementation enum.

`transport_endpoint` must use the same structured endpoint discipline as CDL-103 v1 unless CDL-112 ratification explicitly narrows it further.

`relay_endpoint` is optional. It is required when the advertisement claims an active relay-reachable mode and must be absent for purely local-only or outbound-only modes, unless the field is represented inside `candidate_list` as a candidate rather than an active claim.

`candidate_list` is a bounded ordered preference list of at most three `TransportEndpoint` candidates. It is not an arbitrary endpoint injection surface. Candidate endpoints must be signed inside the advertisement body, must use the same endpoint grammar, and must be interpreted as hints requiring independent validation.

`probe_receipt_ref` may reference a local connectivity probe receipt by CID, SHA-384 digest, or later graph-native reference. It must not embed private router state, raw invite secrets, private keys, or unbounded probe logs.

`relay_slot_ref` may reference a relay grant, relay slot, or relay revocation-compatible evidence object. It is only a reachability hint and does not create relay incentive authority.

## Preserved CDL-103 Invariants

CDL-112 must preserve these CDL-103 invariants unless a later ratification explicitly amends them:

- ML-DSA-65 remains the v1 public peer advertisement signature algorithm.
- `MAX_TTL_EPOCHS = 4` remains the upper TTL bound.
- Future epoch skew remains bounded by the CDL-103 rule.
- `installed_slices_digest` remains privacy-bounded and must not expose the full installed graph state.
- Advertisement bodies used for signing must be canonical JSON with deterministic key order, compact separators, and no non-finite numeric values.
- Advertisement records are discovery hints only; validator authority is not inferred from advertisement presence.
- DHT remains out of scope for this opening.

## Authority Split

`ConnectivityAdvertisement` is a peer discovery and reachability hint. It does not grant:

- Validator admission.
- Validator endpoint authority.
- CDL-105 endpoint assertion authority.
- Relay reward authority.
- Public serving reward authority.
- Reputation credit.
- ECU generation.
- ILC minting.

Validator endpoint authority remains governed by CDL-105 and ADR-0039. Relay pass-through semantics remain governed by relay/rendezvous authority and must not terminate, re-sign, or re-origin consensus messages.

## Ratification Question Resolutions

The ten opening questions are resolved for the ratified v0.1 scope as follows:

1. Public advertisements must not include private, loopback, link-local, or unspecified
   address literals in `transport_endpoint`, `relay_endpoint`, or `candidate_list`.
   Private candidates may be carried only in invite-local or encrypted future artifacts.
2. `relay_slot_ref` remains an opaque bounded reference string in v0.1. It may contain a
   SHA-384 digest, CID, or later typed graph reference, but consumers must treat it only
   as evidence metadata until a later CDL narrows the type.
3. `probe_receipt_ref` is optional in v0.1. Direct-public and NAT-traversed modes without a
   probe receipt are discovery hints, not endpoint authority or validator liveness proof.
4. Ordinary connectivity-mode transitions use signed supersession by higher
   `peer_timestamp_epoch`; explicit withdrawal uses a separate signed tombstone. TTL expiry
   is passive expiry only.
5. CDL-103 anti-eclipse work remains separate. CDL-112 must not weaken CDL-103 peer-table
   caps, deterministic introduction sampling, or future peer-table-root work.
6. Serialized advertisement size must be bounded by the activation implementation. The
   registry entry count remains bounded by CDL-103-compatible `N_MAX` discipline.
7. Relay revocation is represented by a signed tombstone or by references to relay
   revocation evidence; relay revocation does not create relay incentive authority.
8. NAT traversal internals, local router state, private addresses, raw probe logs, and
   invite secrets are too privacy-sensitive for public advertisements.
9. Validator-capable observer modes remain discovery hints. They require no stronger v0.1
   proof reference than other advertisements, and they do not confer validator status.
10. v0.1 uses ML-DSA-65 only. Any future signature-suite registry requires separate
    authority.

## Ratified Activation Invariants

The following invariants are ratified as activation prerequisites for any phase that clears
`CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED`.

1. **Ratification does not clear the guard.** CDL-112 ratification is governance-only.
   `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED` remains `True` until
   GAP-CONNECTIVITY-ADVERTISEMENT-ACTIVATE-00 completes with its own GO phrase.
2. **Separate activation phase required.** Public-RC activation requires
   GAP-CONNECTIVITY-ADVERTISEMENT-ACTIVATE-00 with GO phrase
   `GO Phase GAP-CONNECTIVITY-ADVERTISEMENT-ACTIVATE-00 CONNECTIVITY-ADVERTISEMENT-PUBLIC-RC-ACTIVATE`.
   No other phase may clear the guard.
3. **Public advertisements must be signed.** Every gossiped `ConnectivityAdvertisement`
   must carry a valid ML-DSA-65 signature over the canonical advertisement payload.
   Unsigned or invalid advertisements must be rejected before registry insertion.
4. **TTL and epoch bounds are mandatory.** Every advertisement must include non-zero
   `ttl_epochs` and `peer_timestamp_epoch`. TTL must be at most `MAX_TTL_EPOCHS`;
   missing, zero, negative, or out-of-range epoch fields must be rejected.
5. **No local/private/loopback/link-local endpoint leakage.** Public gossip must reject
   RFC1918, loopback, link-local, and unspecified endpoints in every endpoint-bearing
   field.
6. **Rate limits and storage caps required.** Activation must enforce bounded total
   registry size and per-agent update limits. Unbounded gossip ingestion is forbidden.
7. **Revocation and supersession required.** Activation must support signed supersession
   by newer advertisement and explicit signed tombstone revocation. `ttl_epochs=0` remains
   invalid and must never be used as a revocation signal.
8. **Relay advertisement does not imply validator admission.** Relay reachability confers
   no validator admission, BFT quorum weight, reward eligibility, settlement eligibility,
   CDL-107 candidacy, or active validator-set membership.
9. **Advertisement identity binds to authenticated AgentID.** The authoritative identity
   is the CDL-094 authenticated AgentID. Requester-provided JSON and client IP are not
   identity authority; `JSON_REQUESTER_ID_AUTHENTICATION_ALLOWED=False` and
   `REQUESTER_ID_FALLBACK_ALLOWED=False` apply.

## Non-Claims

This ratification does not implement runtime code, clear `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED`, activate DHT, grant relay incentives, admit validators, authorize public serving, mutate LMDB/Atlas runtime graph state, push a public mirror, activate public RC, transition epoch state, settle ECU, or mint ILC.

This ratification does not amend CDL-103. CDL-103 `PeerAdvertisement` v1 remains valid and unchanged.

## Output Token

`cdl_112_opened_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_SPEC_00`

`cdl_112_connectivity_advertisement_ratified_GAP_CDL_112_RATIFY_00`
