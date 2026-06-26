# ILC Sidecars

Sidecars are optional local or network-adjacent components that use ILC as a
trust substrate without turning every application into core protocol code. The
longer architecture record is
[`docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md`](docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md).

The short version:

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

Current transport ladder:

1. Direct transport: send to a reachable `host:port`.
2. Tor transport: send to a `.onion` hidden service.
3. D2d transport: planned ILC-native routing by `agent_id`.

The D2d option is the intended ILC-native destination, but it requires a live
D2d CCSS message type, recipient CCSS pubkeys in agent INIT records, and routing
through the ILC peer network. Until those gates close, direct and Tor transport
remain bootstrap paths.

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
