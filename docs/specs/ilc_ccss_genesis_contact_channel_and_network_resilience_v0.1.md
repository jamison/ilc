# ILC CCSS Genesis Contact Channel and Network Resilience v0.1

**Phase:** 1576-CCSS-P2 (operationalization — produced during Window 1565-1575
research, to be implemented at/after Phase 1575)
**Date:** 2026-07-11
**Status:** forward-plan spec (not yet executed)
**Sensitivity:** NON-SENSITIVE

---

## 1. Purpose

This document captures the concrete operational plan for:

1. Enabling users to contact Genesis via CCSS immediately at public RC (Phase
   1575), under an honest disclosure of early-network routing limitations.
2. Handling offline delivery and network resilience during the bootstrap phase
   when network density is low and Genesis may be intermittently offline.

These two problems have separate solutions. Content security is independent of
routing privacy and is achievable from day one regardless of network density.

---

## 2. Genesis Contact Channel

### 2.1 Capability Key Publication

At Phase 1575 (Genesis signing ceremony / PUBLIC-RC-GATE-001), Genesis publishes
a **CCSS capability public key** in the project README. This is a 1216-byte
hybrid key (32-byte X25519 + 1184-byte ML-KEM-768) generated via
`generate_hybrid_recipient_keypair()` in
`ilc_core/network/d2d/spectral_route_token.py`.

The capability key is a **contact credential**, not a Genesis identity key:
- It is separate from the Genesis canonical root identity key (SPHINCS+)
- It can be rotated or revoked independently of Genesis's on-graph identity
- Revocation is operationally simple: stop checking messages on that key and
  publish a new key in the README

### 2.2 Two Independent Security Properties

| Property | Status at public RC | Depends on |
|----------|---------------------|------------|
| **Content security** | Full — hybrid X25519 + ML-KEM-768 sealed | Only the KEM, not network density |
| **Routing privacy** | Weak at bootstrap, strengthens with network | Active relay count, cover traffic |

These properties are independent. A user encrypting to the published capability
key gets the same cryptographic content protection regardless of whether 5 or
5,000 agents are online. Only routing privacy (anonymity set size, cover traffic
effectiveness) degrades at low density.

### 2.3 Honest README Language

The README must include a disclosure block alongside the capability key
publication. Suggested language:

```
## Contact Genesis via CCSS

Genesis accepts sealed messages via the CCSS encrypted coordination channel.
Capability public key: [hex-encoded 1216-byte hybrid key]

Message contents are cryptographically sealed (hybrid X25519 + ML-KEM-768).
Routing privacy scales with network participation — the anonymity set grows
as more relay agents join the network. During the early network phase, content
is secure but routing metadata may be more visible than it will be at scale.
Send messages regardless; we check this channel regularly.
```

No false claims. No formal anonymity assertion. Honest disclosure of the
bootstrapping limitation.

### 2.4 Key Lifecycle

- Genesis generates the capability keypair once at Phase 1575 prep
- The public key is committed to the README at Phase 1575 execution
- The private seed is kept offline (Genesis operator custody only)
- If the key is compromised or Genesis wishes to rotate: publish a new key in
  the README and a revocation notice; stop checking the old key
- Revocation is tracked via `build_capability_revocation_ref()` in
  `ilc_core/sidecars/confidential_coordination_capability.py`

---

## 3. Offline Delivery and Network Resilience

### 3.1 The Bootstrap Gap

The `ccss_pre_rc_cover_batch_profile_v1_candidate` design (Phase 1573r) has:
- Relay queue TTL: 5 × 120s = **10 minutes**
- Offline mailbox TTL: 20 × 120s = **40 minutes**
- After 40 min: **permanently deleted**

At bootstrap with low agent density, if Genesis is offline for more than 40
minutes, messages sent during that window are silently dropped. This is a real
gap for early network operation.

### 3.2 Solution: Bootstrap Mailbox Relay with Extended TTL

**Designate one always-on bootstrap relay** (Genesis-operated VPS or trusted
early participant) with extended mailbox retention configured:

| Parameter | Spec default | Bootstrap relay config |
|-----------|-------------|----------------------|
| Relay queue TTL | 10 min | 10 min (unchanged) |
| Offline mailbox TTL | 40 min | **24 hours** |
| Max messages held | spec default | same |

This is a **configuration parameter**, not a protocol change. The ILC relay
architecture already supports per-relay configurable retention. No CDL or
runtime change required.

### 3.3 Genesis Pull Model

Genesis operates on a **periodic pull pattern** rather than requiring continuous
presence:

1. Genesis sends outbound messages whenever online
2. Inbound messages queue at the designated bootstrap mailbox relay
3. Genesis polls the bootstrap relay on each session reconnect
4. Messages older than 24 hours are dropped by the relay (TTL enforcement)
5. Genesis replies to messages within the session that pulled them

This is effectively a mailbox server pattern. It does not require continuous
Genesis uptime. It requires Genesis to connect at least once every 24 hours
to drain the queue (or accept that older messages are dropped).

**Practical schedule:** Genesis checks in at minimum every 12–24 hours during
the early network phase. As the network densifies and message volume grows,
the pull frequency increases naturally.

### 3.4 README Disclosure for Reply Latency

The README contact block should include reply latency expectations:

```
Reply latency depends on our session schedule during the early network phase
(typically within 24 hours). As network participation grows, delivery
reliability and routing privacy both improve automatically.
```

### 3.5 General Network Resilience at Bootstrap

For the ILC network as a whole (not just Genesis contact):

**Gossip delivery model:** Best-effort, TTL-bounded. Messages propagate
whenever a delivery path exists within the TTL window. No guaranteed delivery.
This is by design — not a bug.

**What keeps a sparse early network functional:**
1. A small set of well-connected **seed/bootstrap nodes** that are reliably
   online. These hold and forward messages during gaps. Required for any P2P
   network at genesis (Bitcoin, IPFS, Tor all depend on seed layers).
2. **Extended TTL on bootstrap nodes** covers periods when both sender and
   recipient are offline simultaneously.
3. **Reconnect drain:** Recipients drain their mailbox on first contact after
   an absence period.

**Expected trajectory:**
- Genesis phase: low density, weak routing privacy, extended TTL on bootstrap
  relay, Genesis manual pull pattern
- Early network: seed nodes always-on, routing privacy begins to emerge at
  N > 50 active relays
- Mature network: organic relay density, cover traffic effective, TTL reduces
  to spec defaults, routing privacy approaches design claims

**Honest characterization for early ILC:**
> The network is functional but not fully resilient. It routes messages when
> paths exist within the TTL window. As more nodes come online and stay online,
> delivery reliability and routing privacy improve. Seed node operation is
> required at genesis for baseline reliability.

---

## 4. Implementation Checklist for Phase 1575 and 1576-CCSS-P2

### At Phase 1575 (Genesis signing / PUBLIC-RC-GATE-001)

- [ ] Generate CCSS capability keypair (offline, Genesis operator)
- [ ] Commit capability public key to README with honest disclosure block
- [ ] Designate bootstrap relay and configure 24-hour mailbox TTL
- [ ] Document reply latency expectation in README

### At Phase 1576-CCSS-P2 or first operational phase post-1575

- [ ] Confirm bootstrap relay is operational with extended TTL
- [ ] Confirm Genesis pull schedule is established
- [ ] Add capability key to any published capability advertisements
- [ ] Add revocation notice pathway to README (one-line: "check this repo for
  key rotation notices")
- [ ] Record the bootstrap relay address in the project operational runbook
  (NOT in the public README — relay addresses are operational details)

### Forward: as network density grows

- [ ] Reduce bootstrap relay TTL back toward spec default (40 min) once
  Genesis uptime is more regular
- [ ] Activate cover/batching runtime when `CCSS_COVER_BATCHING_NOT_ACTIVATED`
  is cleared (requires separate CDL/activation gate — not Phase 1575)
- [ ] Update README disclosure when routing privacy claim strengthens

---

## 5. Non-Claims

This document does NOT:
- Activate CCSS-SPECTRAL-01 runtime
- Activate cover/batching (`CCSS_COVER_BATCHING_NOT_ACTIVATED` stays True)
- Assert formal anonymity for Genesis contact messages
- Assert GPO resistance
- Grant public-RC authority (that is Phase 1575's remit)
- Constitute a CDL or ADR

---

## 6. Governing Constraints

| Constraint | Source |
|-----------|--------|
| Cover/batching NOT_ACTIVATED | `ilc_core/sidecars/confidential_coordination_capability.py` |
| CCSS-SPECTRAL-01 NOT_ACTIVATED | `ilc_core/network/d2d/spectral_route_token.py:29` |
| Capability key is separate from Genesis root identity key | CDL-042, key-derived identity |
| TTL parameters are configurable per relay | `ccss_pre_rc_cover_batch_profile_v1_candidate` (Phase 1573r) |
| No formal anonymity claim at public RC | Phase 1573o, 1573p, 1574 activation matrix |
| Relay-level k-anonymity is a future claim target | Phase 1576-CCSS-P1 SIM hardening |
