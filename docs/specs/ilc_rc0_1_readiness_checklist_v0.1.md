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
| Install shape | A fresh node can be installed into the standard path layout with no hidden local assumptions. | Operator playbook + scripted install flow + successful fresh-host proof | satisfied_for_testbed |
| Config shape | Node config, genesis reference, environment file, and TLS material can be rendered and staged deterministically. | `tools/testbed/render_testbed_configs.py`, `tools/testbed/push_configs.sh`, config artifacts | satisfied_for_testbed |
| Bootstrap inventory | Approved peers are represented in a curated inventory that can be rendered, verified, and distributed. | `testbed/bootstrap_peers.json`, render/verify scripts, bootstrap model spec | satisfied_for_testbed |
| Candidate separation | Candidate peer discovery data is separated from approved bootstrap state. | explicit candidate and override artifacts with documented promotion rules | satisfied_for_testbed |
| Identity posture | Node identity, TLS identity, and peer approval state align deterministically. | exchange checks, TLS generation/rotation path, node config references | satisfied_for_testbed |
| Node lifecycle | Start, stop, restart, and status checks are script-driven for both home and VPS nodes. | `tools/testbed/start_home_node.sh`, remote service scripts, smoke/recovery drills | satisfied_for_testbed |
| Diagnostics | Every significant run emits a self-describing diagnostics bundle. | diagnostics bundle directory + manifest + marker summary | satisfied_for_testbed |
| Recovery | Bad config, bad TLS, oversized or stalled inbound payloads, restart, and one-node-down cases fail clearly and have bounded repair steps. | recovery drill scripts, transport timeout assertions, negative-path assertions, runbook entries | satisfied_for_testbed |
| Repo resync | All nodes can resync to the same pushed repo state and re-enter service cleanly. | `tools/testbed/sync_repo.sh` + post-sync smoke proof | satisfied_for_testbed |
| Three-node exchange | The home node and two VPS nodes exchange real CDL-061 traffic bidirectionally. | `tools/testbed/run_three_node_exchange.sh` + diagnostics bundle | satisfied_for_testbed |
| Economic cycle runtime state | The bounded seven-agent scenario emits persisted graph state, settled balances, replay-safe wallet history, and wallet exports directly from the live scenario run, and the resulting public runtime state is queryable from a durable LMDB-backed store. | scenario `economic-state/manifest.json`, `runtime_store`, `tools/check_rc0_1_economic_state.py`, `tools/run_rc0_1_economic_proof.py`, `tools/testbed/run_economic_replay_drills.py`, release gate evidence | satisfied_for_testbed |
| Benchmark instrumentation | The testbed emits panel latency, quorum visibility, direct-delivery amplification, and graph RSS growth metrics in a machine-readable artifact. | `tools/testbed/run_rc0_1_benchmarks.py` + benchmark manifest | satisfied_for_testbed |
| Machine-legible surface | The core control surface is CLI-first, file-based, and JSON-friendly. | CLI docs, config artifacts, deterministic script outputs | satisfied_for_testbed |
| Harness agnosticism | No harness-specific runtime is required for node correctness. | boundary memo + node docs + absence of harness-only assumptions | satisfied_for_testbed |
| Human auditability | A human operator can inspect what was installed, configured, started, and verified. | playbook, walkthrough, logs, diagnostics evidence | satisfied_for_testbed |
| Packaging surface | The release artifact shape is explicit enough that RC packaging is extraction rather than reinvention. | near-RC node definition + package/install plan + readiness delta analysis | satisfied_for_testbed |
| Release evidence | RC0.1 can cite concrete evidence documents instead of relying on conversation state. | readiness checklist closure record + walkthrough + release notes inputs + release claim manifest | satisfied_for_testbed |

## 4. Interpretation notes

### 4.1 `satisfied_for_testbed`

This means the requirement has been satisfied in the current three-node testbed
but has not yet been converted into a published RC0.1 release. Several rows now
also feed the internal release gate and release claim package directly.

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
1. turn the testbed-satisfied rows into an explicit RC0.1 release claim package,
2. keep the package/bundle builder aligned with the latest evidence bundle,
3. avoid reintroducing harness-specific assumptions into the node substrate,
4. keep the durable graph/settlement/wallet runtime proof green on the committed
   head, including invariant, negative-path, query-surface, and replay checks,
5. keep audited safety fixes in place on the transport, panel tie-break, and
   settlement paths while the economic lane expands,
6. extend the live runtime beyond the bounded seven-agent scenario only when the
   protocol lane is constitutionally clear.

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
- `out/testbed/benchmarks/20260402_1610/manifest.json`
- `out/testbed/seven-agent/20260402_1635/economic-state/manifest.json`
- `out/testbed/rc0_1_substrate/20260402_011353/evidence/manifest.json`
- `out/rc0_1_bundle/20260402_012439/manifest.json`
- `out/rc0_1_release_candidate/20260402_204350/substrate/scenario/economic-state/manifest.json`
- `out/rc0_1_release_candidate/20260402_204350/release/economic-proof/manifest.json`
- `out/rc0_1_release_candidate/20260402_204350/claim/manifest.json`
- `out/rc0_1_release_candidate/20260402_204350/manifest.json`
- `out/rc0_1_release_candidate/20260402_230241/release/economic-proof/manifest.json`
- `out/rc0_1_release_candidate/20260402_230241/claim/manifest.json`
- `out/rc0_1_release_candidate/20260402_230241/manifest.json`
- `out/testbed/economic-replay/20260402_1940`
