# ILC Public RC Distribution Profile 1436b v0.1

**Date:** 2026-05-23
**Phase:** 1436b
**Status:** Gap 14 closed at the package-profile specification level
**Sensitivity:** NON-SENSITIVE

```text
gap_14_phase_2_public_rc_profile_complete_phase_1436b
gap_14_closed_phase_1436b
public_rc_distribution_profile_defined_phase_1436b
openclaw_skill_profile_referenced_phase_1436b
gap_14_sequence_lock_addendum_recorded_phase_1436b
public_rc_profile_is_operator_node_equivalent_phase_1436b
openclaw_hosted_profile_excludes_persistence_layer_phase_1436b
adr_0009_non_claim_recorded_phase_1436b
phase_1436_not_activated_phase_1436b
public_rc_not_activated_phase_1436b
```

## 1. Public RC Profile

The `public-rc` profile is the canonical Python installation target for
external operators deploying an ILC node at public RC. It includes the complete
`operator-node` dependency set.

The profile is not a reduced install. It provides the full stack needed for a
production-grade operator node, including sidecar API, gossip transport, gRPC
bridge dependencies, numerical dependencies, and LMDB persistence.

```text
public_rc_profile_is_operator_node_equivalent_phase_1436b
profile=public-rc
equivalent_dependency_set=operator-node
```

Dependency set:

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

External operators should not run a reduced profile at public RC. Reduced
profiles are for hosted skill, lightweight verification, or development use
cases only.

## 2. OpenClaw/NemoClaw Hosted Profile

The `openclaw-hosted` profile is the canonical Python install target for:

- the ClawHub `ilc` skill;
- NemoClaw-hosted ILC integrations;
- skill-layer deployments that use ILC's HTTP/API surface without running a
  full gossip-connected operator node.

Install command:

```bash
pip install 'ilc-core[openclaw-hosted]'
```

The `openclaw-hosted` profile excludes persistence, consensus bridge, and
graph-analytics dependencies:

```text
openclaw_hosted_profile_excludes_persistence_layer_phase_1436b
lmdb_excluded=true
grpcio_excluded=true
protobuf_excluded=true
numpy_excluded=true
```

Skill update disposition:

```text
skill_path=/tmp/ilc-skill/SKILL.md
skill_file_existed=true
skill_install_command_updated=true
openclaw_skill_profile_referenced_phase_1436b
```

The canonical repo record is this spec. `/tmp/ilc-skill/SKILL.md` is an
out-of-repo working copy and is not committed to this repository.

## 3. ADR-0009 Non-Claim

These package profiles are Python packaging profiles only. They are not
ADR-0009 protocol-native distribution layers. Protocol-native bundle layers 0-3
are post-public-RC work per the forward plan §10.4 and Window 1459+.

This phase does not generate, sign, publish, verify, or activate:

```text
Layer 0 Protocol Bundle
Layer 1 Genesis State Bundle
Layer 2 Epoch State Snapshots
Layer 3 Wire Protocol
```

## 4. Relationship To Phase 1436

Gap 14 is now closed at the package-profile specification level by Phase 1436a
and Phase 1436b.

```text
gap_14_closed_phase_1436b
gap_14_sequence_lock_addendum_recorded_phase_1436b
```

Phase 1436 is unblocked by Gap 14, but Phase 1436 remains SENSITIVE and
requires explicit `GO Phase 1436` before execution.

## 5. Non-Activation Boundary

Phase 1436b does not:

- activate public fetch serving;
- activate public P2P;
- activate non-loopback sidecar/projection serving;
- activate public confidential messaging or coordination;
- mutate the CDL register;
- distribute ECU;
- write production graph, ledger, treasury, wallet, or registry state;
- trigger epoch 0-to-1 transition;
- publish public RC artifacts;
- perform ADR-0009 protocol-native bundle layer work.

```text
phase_1436_not_activated_phase_1436b
public_rc_not_activated_phase_1436b
```

## 6. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_public_rc_distribution_profile_1436b_v0.1.md -> distribution/package-profiles
graph_delta=load_bearing_artifact_changed:pyproject.toml -> distribution/package-profiles
graph_delta=load_bearing_artifact_changed:ilc_core/distribution/package_profiles.py -> distribution/package-profiles
```
