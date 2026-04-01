# ILC Near-RC Node Definition v0.1

Status: planning spec
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document defines what a near-RC node means for the current three-node
infrastructure lane.

A node qualifies as near-RC only if it matches the same canonical node model as
its peers and can be operated without hidden machine-specific knowledge.

## 2. Core definition

A near-RC node is an ILC node instance that:
- conforms to the standard install and filesystem shape,
- carries explicit identity, bootstrap, and lifecycle artifacts,
- exposes script-driven operational commands,
- emits inspectable evidence of runtime state,
- supports bounded recovery and reinstallation,
- does not depend on a specific harness for correctness.

## 3. Canonical node model

Every near-RC node should instantiate the same model.

### 3.1 Standard path layout

Required paths:
- repository: `/opt/ilc/current`
- virtualenv: `/opt/ilc/venv`
- config: `/etc/ilc/`
- service: `ilc-node-v1.service`

### 3.2 Required node artifacts

Each node must have:
- `node_config.json`
- `genesis_ref.json`
- `ilc-node-v1.env`
- TLS certificate and key material
- approved peer/bootstrap references
- service unit installation

### 3.3 Required machine roles

The current reference topology uses:
- one home control machine that may also run a node,
- two VPS execution nodes,
- one canonical GitHub remote.

The machine role may differ later, but the node model should not.

## 4. Required contracts

### 4.1 Install contract

A node must be installable through a documented, deterministic sequence that
creates the path layout, runtime environment, and service wrapper.

### 4.2 Identity contract

A node must bind together:
- node identity,
- TLS material,
- approved peer inventory,
- genesis reference,
- runtime bind endpoint.

A mismatch between these elements must fail clearly.

### 4.3 Lifecycle contract

A node must support:
- start,
- stop,
- restart,
- status check,
- log inspection,
- repo resync,
- config re-push.

These operations should be script-driven, not oral tradition.

### 4.4 Diagnostics contract

A node must produce enough evidence for a human or digital operator to answer:
- what code version was running,
- what config was staged,
- what peers were approved,
- what markers were emitted,
- why the node failed or succeeded.

### 4.5 Recovery contract

A near-RC node must be recoverable from at least the following failures:
- service restart or crash,
- config drift,
- repo drift,
- TLS replacement,
- single-node temporary unavailability.

## 5. Anti-snowflake rules

A node is not near-RC if any of the following are required:
- host-local shell edits not represented in the repo or playbook,
- undocumented extra files outside the standard layout,
- unique startup commands for one machine only,
- hidden knowledge about peer identity or bootstrap state,
- ad hoc hand fixes that cannot be replayed.

The three-node lane should converge toward one node model instantiated three
times, not three handcrafted special cases.

## 6. Minimum evidence package

A near-RC node should be able to point to:
- install and operator docs,
- rendered config artifacts,
- bootstrap inventory,
- service unit,
- smoke or exchange proof,
- diagnostics bundle,
- recovery drill proof.

## 7. What this definition excludes

This definition does not require:
- public discovery,
- hostile-internet admission,
- mTLS rollout,
- full seven-agent behavioral integration,
- harness-specific packaging,
- public release publication.

Those belong to later lanes or later RC hardening.

## 8. Immediate implementation implication

When a new testbed or RC task is proposed, the first question should be:

Does this make the canonical node model more reproducible, more legible, more
recoverable, or more packageable?

If the answer is no, it is probably not part of the near-RC node lane.

## 9. Related references

- `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md`
- `docs/specs/ilc_three_machine_testbed_topology_v0.1.md`
- `docs/specs/ilc_remote_control_surface_v0.1.md`
- `docs/ops/ilc_three_machine_operator_playbook_v0.1.md`
- `docs/phases/three_machine_testbed_strike_force_hardening_walkthrough_2026_04_01.md`
