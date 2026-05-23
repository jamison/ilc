# ILC Modular Package Profile Definition 1436a v0.1

**Date:** 2026-05-23
**Phase:** 1436a
**Status:** Gap 14 Phase 1 complete; package profile taxonomy defined
**Sensitivity:** NON-SENSITIVE

```text
gap_14_phase_1_package_profile_definition_complete_phase_1436a
modular_package_profiles_defined_phase_1436a
pyproject_extras_aligned_to_profiles_phase_1436a
protocol_core_profile_defined_phase_1436a
operator_node_profile_defined_phase_1436a
openclaw_hosted_profile_defined_phase_1436a
adr_0009_non_claim_recorded_phase_1436a
phase_1436_not_activated_phase_1436a
public_rc_not_activated_phase_1436a
```

## 1. Purpose

Gap 14 Phase 1 defines the canonical Python package profile taxonomy for ILC.
These profiles are installation configurations over Python optional dependency
groups. They are not protocol-native distribution layers and do not activate
public serving.

## 2. Canonical Profile Table

| Profile name | pyproject extras key | Purpose |
|---|---|---|
| `protocol-core` | `protocol-core` | Minimal crypto, identity, serialization, and schema install. Includes `cbor2`, `cryptography`, `PyNaCl`, and `jsonschema`; excludes network stack, DB, and numerical graph analytics. |
| `operator-node` | `operator-node` | Complete node dependency set for operator deployment. Includes server/API, HTTP client, numerical, crypto/serialization, gRPC/protobuf, and LMDB persistence dependencies. |
| `openclaw-hosted` | `openclaw-hosted` | Hosted skill/API-surface profile for OpenClaw, NemoClaw, or equivalent harness deployment. Includes API, HTTP client, crypto/serialization, and schema dependencies; excludes LMDB, gRPC/protobuf, and numerical graph analytics. |
| `dev` | `dev` | Existing full development environment including pytest and the full project dependency stack. Retained for compatibility. |

The existing `consensus-only` extra is retained for backward compatibility. It
is not removed or redefined in Phase 1436a.

The `public-rc` profile is deliberately not defined in Phase 1436a. It is
reserved for Phase 1436b.

## 3. Dependency Sets

### 3.1 `protocol-core`

```text
cbor2>=5.0.0
cryptography>=41.0.0
PyNaCl==1.6.2
jsonschema>=4.0.0
```

### 3.2 `operator-node`

```text
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
requests>=2.31.0
httpx>=0.24.0
numpy>=1.24.0
cbor2>=5.0.0
cryptography>=41.0.0
grpcio>=1.80.0
protobuf>=6.30.0
PyNaCl==1.6.2
jsonschema>=4.0.0
lmdb>=2.2.0
```

### 3.3 `openclaw-hosted`

```text
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
requests>=2.31.0
httpx>=0.24.0
cbor2>=5.0.0
cryptography>=41.0.0
PyNaCl==1.6.2
jsonschema>=4.0.0
```

The `openclaw-hosted` profile intentionally excludes:

```text
lmdb
grpcio
protobuf
numpy
```

## 4. ADR-0009 Non-Claim

These profiles describe Python dependency subsets only. They are not ADR-0009 protocol-native distribution layers.
Protocol-native bundle layers 0-3 are
post-public-RC work per the forward plan §10.4 and Window 1459+ planning.

ADR-0009 remains the authority for the four-layer protocol-native bundle
architecture:

```text
Layer 0: Protocol Bundle
Layer 1: Genesis State Bundle
Layer 2: Epoch State Snapshots
Layer 3: Wire Protocol
```

Phase 1436a does not implement, generate, sign, verify, or publish any ADR-0009
bundle layer.

## 5. Current Implementation Hooks

The machine-readable profile constants are:

```text
ilc_core/distribution/package_profiles.py
PACKAGE_PROFILES_VERSION=package_profiles_1436a.v0.1
DEFINED_PROFILES=protocol-core,operator-node,openclaw-hosted,dev
```

The pre-existing `ilc_core/rc/package_profiles.py` remains the public-RC
component-reachability/profile-integrity surface. Phase 1436a does not replace
that module; it adds a narrower Python packaging profile taxonomy under
`ilc_core.distribution`.

## 6. Non-Activation Boundary

Phase 1436a does not:

- activate public fetch serving;
- activate public P2P;
- activate non-loopback sidecar/projection serving;
- activate public confidential messaging or coordination;
- mutate the CDL register;
- distribute ECU;
- write production graph, ledger, treasury, wallet, or registry state;
- trigger epoch 0-to-1 transition;
- publish public RC artifacts.

Phase 1436 remains SENSITIVE and requires explicit `GO Phase 1436`.

## 7. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_modular_package_profile_definition_1436a_v0.1.md -> distribution/package-profiles
graph_delta=load_bearing_artifact_added:ilc_core/distribution/package_profiles.py -> distribution/package-profiles
graph_delta=load_bearing_artifact_changed:pyproject.toml -> distribution/package-profiles
```
