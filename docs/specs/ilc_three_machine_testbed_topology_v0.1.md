# ILC Three-Machine Testbed Topology v0.1

Status: planning spec
Date: 2026-04-01
Owner lane: G8 implementation cluster

## 1. Purpose

This document fixes the first practical topology for the ILC three-machine
infrastructure testbed. The goal is to get from local proof to repeatable
multi-machine execution with the smallest safe control surface.

## 2. Selected topology

The selected topology is:
- one home control machine
- two VPS worker nodes
- one canonical private GitHub repository

This is the minimum topology that satisfies the three-machine requirement while
keeping implementation control centralized.

## 3. Machine roles

### 3.1 Home control machine

The home machine is the control plane.

Responsibilities:
- canonical working repository
- Codex implementation lane
- Claude and Gemini audit lanes if used
- SSH fanout to both VPS nodes
- push to the private GitHub origin
- run deploy, smoke, restart, and log-collection scripts

The home machine is the only place where LLM-assisted repository mutation is
allowed by default.

### 3.2 VPS node 1 and VPS node 2

Each VPS is an execution target.

Responsibilities:
- host one ILC node service
- receive config, genesis reference, and deploy updates from the home machine
- expose logs and service state back to the home machine
- stay script-driven rather than agent-driven

No resident LLM agent is required on either VPS for the first release-candidate
path.

### 3.3 GitHub

GitHub remains the canonical remote and future release channel.

Responsibilities:
- authoritative private origin
- backup and audit trail
- eventual RC distribution channel
- issue and milestone coordination

GitHub is not the runtime control plane and is not the peer-discovery plane.

## 4. Network model

The selected network model is:
- SSH for control
- a private overlay network for node-to-node addressing
- HTTPS endpoints for CDL-061 envelope traffic

Recommended overlay choices:
- Tailscale first
- WireGuard if a lower-level manual network is preferred

Public raw-IP operation is not required for the first testbed proof.

## 5. Repository and deployment model

The repository model is:
- one canonical local checkout on the home machine
- one canonical GitHub origin
- no long-lived model-specific forks as authorities
- deploys to VPS nodes from the home machine by deterministic scripts

Recommended per-node paths:
- repository: `/opt/ilc/current`
- virtualenv: `/opt/ilc/venv`
- config: `/etc/ilc/`
- service: `ilc-node-v1.service`

## 6. IDE and plugin stance

Browser-hosted VS Code on the VPS is optional convenience only.
The canonical workflow remains:
- repo scripts
- SSH
- systemd
- structured logs

VS Code or Open VS plugins may accelerate file access, SSH access, or log
inspection, but they do not replace the control surface defined in the repo.

## 7. Explicit exclusions

This topology does not include:
- VPS-resident autonomous LLM agents
- dynamic peer discovery
- DHT bootstrap
- public bulletin-board peer admission
- automatic peer promotion from discovered candidates
- multi-hop routing

## 8. Current control-plane realization

The topology is now realized in-repo through:
1. `testbed/hosts.json` for the home machine and both VPS nodes
2. `testbed/bootstrap_peers.json` as the curated approved-peer inventory
3. `tools/testbed/` orchestration scripts for repo sync, service install,
   config push, exchange checks, recovery drills, and diagnostics
4. `docs/ops/ilc_three_machine_operator_playbook_v0.1.md` for the operator flow
5. `docs/specs/ilc_near_rc_node_definition_v0.1.md` for the canonical node
   shape this topology should instantiate
6. `docs/specs/ilc_rc0_1_readiness_checklist_v0.1.md` for the RC-facing proof
   obligations this topology should satisfy

The next hardening work should stay inside this script-first control surface.
