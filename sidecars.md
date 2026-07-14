# ILC Sidecars

Sidecars are optional local or network-adjacent components that compose with ILC identity, jury verification, and ECU economics without becoming core protocol code. A sidecar is not a separate authority root — it is a typed local runtime surface that submits signed protocol objects (truth primitives, receipts, CCSS envelopes) through the same graph machinery as any other participant.

The architecture principle is deliberate: keeping application-layer semantics in sidecars lets the protocol core stay minimal and auditable while still supporting an open ecosystem of use cases — private messaging, knowledge marketplaces, graph visualization, wallet projection, prediction markets, and more.

The longer architecture record is
[`docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md`](docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md).

## Public-RC Sidecar Catalog

These sidecar tracks are documented and available at public RC:

| Sidecar | Repo | Purpose |
|---|---|---|
| **OpenClaw local capture** | [`skills/ilc-openclaw-local-capture/`](skills/ilc-openclaw-local-capture/) | Capture, consent-gated ECU estimation, and invite-gated graph contribution via OpenClaw sessions. The primary human+AI participation surface. |
| **CCSS — Confidential Coordination Suite** | [`ilc-ccss-sidecar/`](ilc-ccss-sidecar/) | Sealed-sender private messaging using fixed-size 4156-byte encrypted envelopes. Native transport by agent_id via ILC D2D gossip. |
| **StarMap / Atlas Installer** | Via `ilc atlas` and `ilc bootstrap` | Materializes verified graph slices from the Genesis Atlas: download, hash-verify, and reconstruct a signed public-RC slice locally. |
| **Graph Viz / Graphics Sidecar** | [`ilc-graphics-sidecar/`](ilc-graphics-sidecar/) | Human-readable graph exploration, authority tracing, public/private visibility inspection, and Genesis Atlas visualization. |
| **TimeCapsule Sidecar** | [`ilc-timecapsule-sidecar/`](ilc-timecapsule-sidecar/) | Commit sealed Genesis-era material at genesis time and release it under a ratified release condition. |
| **Wallet Sidecar** | [`ilc-wallet-sidecar/`](ilc-wallet-sidecar/) | Read-only wallet projection surface. Balance display, claimability state, and ECU/ILC balance queries. Write paths remain inactive under current activation gates. |
| **Local graph / verifier sidecars** | [`ilc_core/sidecars/`](ilc_core/sidecars/) | Local graph projection, receipt verification, claimability checks, and sidecar registry/profile surfaces. |

Installing or running a local sidecar does not activate public sidecar serving, public P2P, minting, settlement, wallet actions, or any constitutional gate. Those gates are recorded in [`docs/phases/STATUS.md`](docs/phases/STATUS.md).

## Architecture: how sidecars compose with the protocol

```
  OpenClaw / human terminal / AI agent
         │
         ▼
  ┌─────────────────────────────────────────┐
  │  Sidecar (local runtime surface)        │
  │  - capture / classify / estimate        │
  │  - CCSS envelope construction           │
  │  - graph projection queries             │
  │  - receipt and claimability checks      │
  └───────────────┬─────────────────────────┘
                  │  signed typed protocol objects
                  ▼
  ┌─────────────────────────────────────────┐
  │  ILC node core (ilc_core/)              │
  │  - signature verification               │
  │  - CID anchoring                        │
  │  - graph state management               │
  │  - ECU accounting (gated)               │
  │  - epoch processing (gated)             │
  └───────────────┬─────────────────────────┘
                  │  consensus objects
                  ▼
  ┌─────────────────────────────────────────┐
  │  ilc_consensus/ (Rust)                  │
  │  - BLS12-381 quorum proofs              │
  │  - DAG consensus                        │
  │  - epoch settlement (gated)             │
  └─────────────────────────────────────────┘
```

The sidecar boundary enforces: sidecars send signed typed payloads; the node core verifies signatures, anchors CIDs, and routes economic events through activation-gated paths. Application semantics live in sidecars; the core stays minimal.

## The short version:

- `ilc sidecar ...` is the stable namespace for sidecar discovery, inspection,
  recipes, and future package/profile management.
- `ilc ccss ...` is a curated shortcut for the
  [Confidential Coordination Sidecar Suite](docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md)
  because private contact with Genesis is a first public-RC user experience.
- Sidecar recipes bundle multiple sidecar modules into one installable local
  workflow.
- Installing or running a local sidecar does not by itself activate public
  serving, public P2P, mainnet, minting, settlement, or any constitutional gate.

## CLI namespace

Use the general namespace when working with sidecars as a class:

```bash
ilc sidecar list
ilc sidecar inspect confidential_coordination_sealed_sender_local_delivery
ilc sidecar recipe list
ilc sidecar recipe inspect confidential-contact
ilc sidecar recipe apply confidential-contact
```

Use curated aliases for high-value workflows:

```bash
ilc ccss apply-recipe
ilc ccss contacts
ilc ccss send genesis "Hello Genesis"
ilc ccss inbox
ilc ccss read --latest
```

This avoids crowding the top-level CLI with a near-infinite number of future
sidecar names while still allowing important sidecars to have a simple command.

## Modules versus recipes

A sidecar module is one functional component. A recipe is a named bundle of
modules, configuration, local files, and verification checks.

For example, the
[`confidential-contact`](docs/specs/ilc_ccss_001_private_gated_shard_sidecar_contract_1324_v0.1.md)
recipe currently covers:

- `confidential_coordination_private_gated_shard`
- `confidential_coordination_capability_membership_boundary`
- `confidential_coordination_sealed_sender_local_delivery`
- `confidential_coordination_gossip_jitter_cover_policy`

The ergonomic alias for that recipe family is:

```bash
ilc ccss
```

## CCSS bootstrap flow

For a new local user:

```bash
pipx install "ilc-core[public-rc]"
ilc ccss apply-recipe
ilc ccss contacts
ilc ccss send genesis "Hello Genesis"
```

For a development checkout:

```bash
pip install -e ".[dev]"
ilc ccss apply-recipe
ilc ccss contacts
```

The [Genesis contact protocol](docs/contact/genesis_agent_contact_protocol_v0.1.md)
may remain a placeholder until public-RC contact values are
published. If the contact is not configured, `ilc ccss send genesis ...` fails
closed instead of guessing an endpoint.

## Transport model

CCSS messages are fixed-size encrypted envelopes. The transport only carries an
opaque 4156-byte blob.

The canonical transport is **D2D by `agent_id`**: route the sealed envelope
through the ILC peer gossip network to the recipient's agent identity. No IP
address and no auxiliary relay is required. The recipient's CCSS capability public
key (hybrid X25519 + ML-KEM-768) is published at registration and used to seal
the envelope before routing.

Direct `host:port` delivery is available for operator-to-operator deployments
where both endpoints are known and reachable. It is not the Genesis contact path.

## Authority boundary

The sidecar CLI uses local package metadata and local operator files. It does
not authorize:

- public repository publication;
- public confidential coordination serving;
- public P2P activation;
- public sidecar/projection serving;
- wallet actions;
- ECU minting;
- ILC settlement;
- epoch transition;
- mainnet operation.

Avoid using `activate` for local sidecar workflows. Prefer `install`,
`configure`, `run`, `serve`, or `apply recipe`. Reserve `activate` for explicit
protocol or governance gates.

## ADR or CDL status

This CLI naming convention does not require a new CDL. It is not a
constitutional decision and does not mutate protocol authority.

A new ADR may be appropriate later if the recipe registry becomes a
protocol-canonical artifact with external conformance requirements. For now,
this document is a public UX and package-namespace guide layered on top of the
existing [sidecar registry](docs/specs/ilc_graph_native_sidecar_registry_manifest_1307_v0.1.md)
and architecture documents.
