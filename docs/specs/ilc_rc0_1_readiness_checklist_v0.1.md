# ILC RC0.1 Readiness Checklist v0.1

Status: planning checklist
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document turns the current RC0.1 guidance into a concrete readiness
checklist.

A claim that ILC is ready for RC0.1 should not be made unless every required
row in this checklist is satisfied with cited evidence.

## 2. Readiness rule

RC0.1 is considered ready only when all of the following are true:
- the three-node substrate is reproducible,
- the node model is stable and non-snowflake,
- bootstrap, lifecycle, diagnostics, and recovery are script-driven,
- the agent-facing surfaces are machine-legible and harness-agnostic,
- the resulting package can be audited by a human operator.

## 3. Required checklist

| Area | Requirement | Minimum evidence | Current pre-RC status |
|---|---|---|---|
| Install shape | A fresh node can be installed into the standard path layout with no hidden local assumptions. | Operator playbook + scripted install flow + successful fresh-host proof | in_progress |
| Config shape | Node config, genesis reference, environment file, and TLS material can be rendered and staged deterministically. | `tools/testbed/render_testbed_configs.py`, `tools/testbed/push_configs.sh`, config artifacts | in_progress |
| Bootstrap inventory | Approved peers are represented in a curated inventory that can be rendered, verified, and distributed. | `testbed/bootstrap_peers.json`, render/verify scripts, bootstrap model spec | in_progress |
| Candidate separation | Candidate peer discovery data is separated from approved bootstrap state. | explicit candidate and override artifacts with documented promotion rules | open |
| Identity posture | Node identity, TLS identity, and peer approval state align deterministically. | exchange checks, TLS generation/rotation path, node config references | in_progress |
| Node lifecycle | Start, stop, restart, and status checks are script-driven for both home and VPS nodes. | `tools/testbed/start_home_node.sh`, remote service scripts, smoke/recovery drills | in_progress |
| Diagnostics | Every significant run emits a self-describing diagnostics bundle. | diagnostics bundle directory + manifest + marker summary | open |
| Recovery | Bad config, bad TLS, restart, and one-node-down cases fail clearly and have bounded repair steps. | recovery drill scripts, negative-path assertions, runbook entries | in_progress |
| Repo resync | All nodes can resync to the same pushed repo state and re-enter service cleanly. | `tools/testbed/sync_repo.sh` + post-sync smoke proof | satisfied_for_testbed |
| Three-node exchange | The home node and two VPS nodes exchange real CDL-061 traffic bidirectionally. | `tools/testbed/run_three_node_exchange.sh` + diagnostics bundle | satisfied_for_testbed |
| Machine-legible surface | The core control surface is CLI-first, file-based, and JSON-friendly. | CLI docs, config artifacts, deterministic script outputs | in_progress |
| Harness agnosticism | No harness-specific runtime is required for node correctness. | boundary memo + node docs + absence of harness-only assumptions | in_progress |
| Human auditability | A human operator can inspect what was installed, configured, started, and verified. | playbook, walkthrough, logs, diagnostics evidence | in_progress |
| Packaging surface | The release artifact shape is explicit enough that RC packaging is extraction rather than reinvention. | near-RC node definition + package/install plan + readiness delta analysis | open |
| Release evidence | RC0.1 can cite concrete evidence documents instead of relying on conversation state. | readiness checklist closure record + walkthrough + release notes inputs | open |

## 4. Interpretation notes

### 4.1 `satisfied_for_testbed`

This means the requirement has been satisfied in the current three-node testbed
but has not yet been converted into a formal RC0.1 release claim.

### 4.2 `in_progress`

This means the control surface exists and partial proof is already present, but
one or more of the following are still incomplete:
- negative-path coverage,
- packaging-level proof,
- operator-proof clarity,
- carry-forward evidence locking.

### 4.3 `open`

This means the requirement is still architectural guidance or partial planning,
not a proven operating property.

## 5. Immediate closure targets

The next work should close the following rows first:
1. Candidate separation
2. Diagnostics
3. Packaging surface
4. Release evidence
5. Remaining recovery negative paths

These items have the highest leverage because they reduce the amount of manual
interpretation needed between the testbed and RC0.1.

## 6. Relationship to the three-node lane

The three-node testbed is the proving ground for this checklist.

The goal is not to produce a separate RC architecture after the testbed. The
goal is to use the testbed to satisfy the checklist directly, then package the
result.

## 7. Related references

- `docs/specs/ilc_agent_native_rc0_1_guidance_synthesis_v0.1.md`
- `docs/specs/ilc_three_machine_testbed_topology_v0.1.md`
- `docs/specs/ilc_remote_control_surface_v0.1.md`
- `docs/specs/ilc_bootstrap_peer_source_and_promotion_model_v0.1.md`
- `docs/ops/ilc_three_machine_operator_playbook_v0.1.md`
- `docs/phases/three_machine_testbed_strike_force_hardening_walkthrough_2026_04_01.md`
