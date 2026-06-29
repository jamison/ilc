# ILC Native Sidecar Typed-Subgraph Anchor

**Version:** v0.1
**Phase:** 1568-Fix2h
**Status:** Internal anchor specification. Not public sidecar serving authority.

## Purpose

This document records the minimum graph vocabulary needed to keep native and
future third-party sidecars aligned with the single ILC graph. A sidecar is not
an independent graph. It is a typed subgraph rooted through a creator agent,
Genesis registry receipt, package profile, or equivalent stable receipt, and it
must remain traceable back to Genesis.

## Minimal Vocabulary

```text
sidecar_definition
sidecar_instance_or_registration_receipt
sidecar_recipe
sidecar_module
sidecar_capability_surface
sidecar_install_or_verify_receipt
creator_agent
governing_authority_refs
public_serving_enabled=false
public_rc_exclude_private_agentic_harness=true
model_router_exists=false
gaia_x_adapter_exists=false
werner_credit_exists=false
```

## Stable Identity Rule

Human-readable sidecar names may collide. Stable graph IDs must be scoped by at
least one of:

- creator agent ID;
- registration receipt hash;
- content hash;
- package profile;
- Genesis/native registry receipt.

## v0.4 Boundary

For public-RC/v0.4, sidecar recipe and module membership remain ordinary typed
binary graph data. Sidecar-specific hyperedge activation is not authorized.
Public sidecar serving and third-party installability remain default-off.

## Native Harness Boundary

Native harness modules are currently local/default-off building blocks. The
current repo has local primitives for consent, local capture, immutable local
storage, provider usage records, idle scheduling, and co-attestation receipts.
It does not yet have a public `model-router`, GAIA-X/sovereign adapter, or
Werner-credit module.

Any `ilc-submit` or Werner-credit route is production-path adjacent and requires
separate sensitive GO before it can create live graph or economic effects.

