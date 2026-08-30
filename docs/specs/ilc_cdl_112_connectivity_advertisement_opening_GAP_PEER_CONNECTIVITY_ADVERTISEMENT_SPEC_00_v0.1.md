# CDL-112 ConnectivityAdvertisement Opening

**Phase:** GAP-PEER-CONNECTIVITY-ADVERTISEMENT-SPEC-00  
**Date:** 2026-08-30  
**Status:** OPENED, not ratified  
**Opening token:** `cdl_112_opened_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_SPEC_00`  
**Schema version:** `connectivity_advertisement_cdl112.v0.1`

## Authority Context

CDL-112 opens a new constitutional lane for `ConnectivityAdvertisement`, a signed peer connectivity advertisement schema that can carry richer reachability information than CDL-103 `PeerAdvertisement` v1.

CDL-112 is not a CDL-103 amendment. CDL-103 remains the ratified authority for `peer_advertisement_cdl103.v0.1`, including ML-DSA-65 signatures, bounded TTL, curated bootstrap fallback, deterministic introduction sampling, and anti-eclipse mitigation targets. CDL-112 is a separate CDL governing a new schema version that may be implemented only behind `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED=True` until ratification and explicit guard clearance.

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

## Proposed Canonical Fields

The opening proposes this top-level shape:

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

The exact runtime representation remains deferred to GAP-PEER-CONNECTIVITY-ADVERTISEMENT-IMPL-00 and later ratification.

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

## Open Questions For Ratification

1. Whether `candidate_list` may include private-literal endpoints in public advertisements, or whether private candidates must be carried only in invite-local or encrypted capsules.
2. Whether `relay_slot_ref` should be a SHA-384 digest, CID, graph edge reference, or typed relay grant reference.
3. Whether `probe_receipt_ref` is required for `direct_public`, `nat_traversed_direct`, `validator_direct`, and `validator_observer_direct` claims.
4. Whether connectivity-mode transitions require explicit supersession records or can be represented by TTL expiry plus newer signatures.
5. How CDL-103 anti-eclipse peer-table-root work should interact with richer v2 connectivity advertisements.
6. What maximum serialized advertisement size should apply and how that limit interacts with CDL-103 `N_MAX`.
7. How relay revocation receipts propagate through connectivity advertisements.
8. Which NAT traversal details are too privacy-sensitive to publish in public advertisements.
9. Whether validator-capable observer modes require a stronger proof reference than non-validator observer modes.
10. Whether `connectivity_advertisement_cdl112.v0.1` should reuse ML-DSA-65 only or allow a future signature-suite registry after separate authority.

## Non-Claims

This opening does not ratify CDL-112. It does not implement runtime code, clear `CONNECTIVITY_ADVERTISEMENT_NOT_ACTIVATED`, activate DHT, grant relay incentives, admit validators, authorize public serving, mutate LMDB/Atlas runtime graph state, push a public mirror, activate public RC, transition epoch state, settle ECU, or mint ILC.

This opening does not amend CDL-103. CDL-103 `PeerAdvertisement` v1 remains valid and unchanged.

## Output Token

`cdl_112_opened_GAP_PEER_CONNECTIVITY_ADVERTISEMENT_SPEC_00`
