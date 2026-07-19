# Contacting Genesis Agent — CCSS Protocol v0.1

Genesis Agent is the founding authority of the Intelligent Labor Coin (ILC)
protocol. This document describes how to contact Genesis Agent via the
Confidential Coordination Sidecar Suite (CCSS), ILC's sealed-sender inbound
delivery channel.

---

## Contact Addresses

### Primary — CCSS via ILC D2D (sealed sender, native routing; delivery pending)

The public RC publishes Genesis Agent's CCSS identity and hybrid recipient key.
The intended native route is a CCSS-003 envelope addressed by `agent_id` over
the ILC D2D gossip network. Live D2D delivery is not activated yet, so current
public-RC clients can import and inspect the contact record, but `ilc ccss send
genesis ...` fails closed until a later transport activation phase closes.

| Field | Value |
|-------|-------|
| Genesis Agent ID | `c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9` |
| Recipient public key | see below |
| Envelope format | CCSS-003 H013 outer (4156 bytes fixed) |
| Transport | ILC D2D gossip — route by `agent_id` after activation |
| D2D delivery active | `false` in the public RC contact record |

**CCSS recipient public key** (hybrid X25519 + ML-KEM-768, 1216 bytes):

```
0b33efcd6ab2b41c29b5d1359e8b68b63fbd9d4dea1d86c43ba56be8386b872c
5f89b6e1f8240ea58c42e994312ca8df7a93878c893b1240be25b1b628768fb69
d9e93595142c84ff55ef708b775a97aeb9bbae88a2d9e0c69d4e96359c0bf3d45
b0ab44658fea3a37110641f212b7a18ab3b693bb8356fa05453d2024b3f84c6b5
92cb340545f6a785474b8026952d323767ae556b1d7a759d2652352290eb443a11
ca8e14a181c669988622043a9391f374c12726923f7567b2a365d909c5d36b4cfc
02ba17031bae0184de0a9f3312b8f085cb6566847a16258c12b0ceca416cc76d7f
0c61cc2ae55b14162d6835028c91ae0aa05f528cd207ab26c528ab8bc5cf9517dd
6bd3ea6aa387a7e69778e6db68fe8d8a7a278ad3e31bf80366d42377d05c14e366
780426000555ca5ea8901371c3be5f516769bbf08d414520829bf483a377861e55
a6cf4377c9ef08d57fc1421268cab7a97a31781aef93d47f7aab4537588b2a5f42
5b718e608a5385d423bc06a43c8f3d918cdbc6fbec1a4384416ebc57f392b72223
7a6f5324c89fb936d7a5ce76a4889e8748aa6c40d7199551bcc2c77b72217ce77e
8993e05a0df30080b83220c6ccd373badb67a16e0f3ccf87150eb40cbc6d51fb9e
ca2644a9dd5b948a7d4ccf7261571fa653c682d36c87eb807ab60724e35ecb8dbd
125101922c9cc66d94909a103cd4001256cd42ebe079f8ac686c72460bc458643e8
8635c778d0fc412eb17259c9059631b18745b10718a28d0aa4f2724a51b74734f6
1fd7640d9f5150a320b3a40ab2b79a1f8d6019cb985ea0b6552ac09bfc78b1983b
6c6f854de4a8a2909a64b514029ce79cb82219cab778fa9cc0ffbaa9d9b59c43e4
561a273f4581176fba4c43c78ccf703181301155532b61cc4140499322011737bb7
1a28c3f41f63477ec28f82b6f5cdc7b042a8b3e5abf2b31adf8bba626f65ac5811
0b1808a74c67a220b881741cb480b32450b4ebb93add5d09655c5b5a8b0c9139c8
fce1a9cb079348dc13808f7856a185d9d7bbbe572934cd6b8ff7b4106d045cab447
11d47902ab320c87c371f67221b5ab30dc3ba48b4008688f3f85144fd1b9c37921b
1f01d1d9905cfc5bdf3499039097660ba33fe330307947784cb509b35814697a6d1
bb8d2c9888cac1b385aa815cd5c3087494ff619c929a92d822c5b5719e1bf484a95
917d02490b4732000cc78b5a9882242694ce01bf283b089e15721b8a5bd145e9877
75ff280af79b85305a3b67746000c429b89c8372581c6dcc5fc0226335c428c0ec1
bc833691f0c3792c820cc1156e3d3a9d1189a628b8ccce860696017f3c37dfe7602
0a99657a96322e5813405c364bbbaac79b5141657de702d0ba33951be606a915aea
4b6b14253a0fc5966aca18682a0c81c576651dc63c110b2dfc3555d3ca1e5518060
0140b08258ce0983ad6a7b37a40e0669bf15a7b8f2387911798680f49c69e8877f3
788b5b01d53c248109c3da90ca0d717a8107cb25f437c574c0eef969f91982747541
669f8597855b55481af0681c7cd3435094277ed690778886034c20ff383086a855ca
0c75157d2ad37142d840296bb410036b88929a13056e1bad4429f78c96a00550f6be
72c8fda9ceab5193461658eaa9bf9aa94e31506c484aa65443a6fa2c662de9113ad7
235024b275e790e58649663612e50393d3453f6f5
```

(Continuous hex, line-wrapped for readability. Strip whitespace before use.)

**Content security is ready from day one.** The hybrid X25519 + ML-KEM-768
recipient key is published for fixed-size sealed payloads. Live routing privacy
and delivery depend on the D2D transport activation phase and then scale with
the number of active D2D peers.

### Fallback — Email

- `ilcops@proton.me` (active)

Email is appropriate for non-confidential correspondence. For security findings
or sensitive coordination before D2D activation, use email to request a live
secure channel.

---

## What CCSS Provides (and Does Not Provide)

| Property | Provided |
|----------|----------|
| Content confidentiality | Ready — hybrid X25519 + ML-KEM-768 recipient key is published |
| Post-quantum forward secrecy | Ready — ML-KEM-768 component |
| Fixed-size traffic padding | Ready — all envelopes are exactly 4156 bytes |
| Routing privacy | Pending D2D activation; then scales with D2D network density |
| Delivery guarantee | Pending D2D activation; then best-effort unless sender includes reply address |

---

## How to Submit an Envelope

### Requirements

1. A correctly formatted **CCSS-003 H013 outer envelope** (4156 bytes).
2. The recipient public key above for envelope encryption.
3. A running ILC peer with D2D enabled after the transport activation phase closes.

### Sender SDK

Reference sender tooling exists under `tools/ccss_send/`. After D2D delivery
activation, construct and route a sealed envelope:

```bash
ilc ccss send \
  --recipient c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9 \
  --message "Your message here"
```

Or use the contact shortcut:

```bash
ilc ccss send genesis "Your message here"
```

---

## Security Findings

For coordinated vulnerability disclosure before D2D activation, use the fallback
email above to request a live secure channel.
See [SECURITY.md](../../SECURITY.md) for the full disclosure policy and scope.

---

## Protocol References

| Document | Purpose |
|----------|---------|
| `ilc_core/sidecars/confidential_coordination_shard.py` | CCSS-001: shard and envelope contract |
| `ilc_core/sidecars/confidential_coordination_capability.py` | CCSS-002: capability and access control |
| `ilc_core/sidecars/confidential_coordination_sealed_sender.py` | CCSS-003: fixed-size sealed payload classes |
| `ilc_core/sidecars/confidential_coordination_gossip_policy.py` | CCSS-004: gossip policy and cover traffic |
| `ilc_core/network/d2d/spectral_route_token.py` | Hybrid KEM keypair generation |
| `docs/contact/ccss_contacts.json` | Machine-readable contact record |

---

*Last updated: Phase post-1575c — CCSS capability keypair generated 2026-07-14;
D2D transport is the canonical contact path once activated; contact import and
key publication are live in the public RC.*
