# ILC Root Skills Pack Spec GAP-HARNESS-SIDECAR-07 v0.1

> ADVISORY INPUT TO A FUTURE CDL OR RUNTIME LANE; NOT GOVERNING RECIPE AUTHORITY.

**Phase:** GAP-HARNESS-SIDECAR-07
**Date:** 2026-08-14
**Status:** committed advisory spec
**Sensitivity:** NON-SENSITIVE

```text
root_skills_pack_spec_committed_GAP_HARNESS_SIDECAR_07
```

## 1. Advisory Status

This document defines a root skills taxonomy for ILC-native agent harnesses. It
does not ratify a skill dispatch table, grant capability authority, install a
sidecar, clear an activation guard, mutate a CDL, or change runtime behavior.

The controlling boundary is that ILC agents should expose stable, deterministic
CLI/tool/module surfaces that external harnesses can call. A later SENSITIVE CDL
or runtime lane must define governing skill authentication, dispatch, delegation,
and public-serving semantics before any skill pack becomes protocol authority.

## 2. Inputs Read

- `docs/specs/ilc_harness_sidecar_module_registry_GAP_HARNESS_SIDECAR_00_v0.1.md`
- `docs/specs/ilc_cli_json_conformance_matrix_GAP_HARNESS_SIDECAR_01_v0.1.md`
- `docs/research/ilc_web2_service_primitive_trust_recipe_mapping_v0.1.md` Section 6.5
- `ilc_core/sidecars/registry_manifest.py`
- `ilc_core/cli/main.py`
- `ilc_core/cli/d2e_submit_cli.py`
- `ilc_core/graph/sidecar_query_runtime.py`
- `ilc_core/value_action/ilc_transfer_intent.py`
- `ilc_core/ecu/ecu_fast_path_intent.py`
- `tools/testbed/attribution_readback.py`
- `tools/testbed/ilc_transfer_submit.py`
- `tools/testbed/ecu_transfer_submit.py`

MemPalace was queried for sidecar skill, capability, root skill pack, graph
submit, value action, and attribution readback context. Returned paths reinforced
the harness-sidecar roadmap and OpenClaw local-skill history, but did not
authorize public skill dispatch or a live sidecar install surface.

## 3. Tier 1 Root Skills

Tier 1 skills are universal starter capabilities that every ILC agent harness may
present as local, read-oriented commands. Prototype CLI surfaces remain labelled
prototype until later phases replace their compatibility payloads with full
protocol readback.

| skill_id | Description | Backing CLI command | Backing module or surface | Activation gate | Current status | Notes |
|---|---|---|---|---|---|---|
| `graph.query` | Query a local graph projection, including node lookup, local novelty scoring, reuse centrality ranking, and submission receipt lookup. | `ilc query node`; `ilc query receipt` | `ilc_core/graph/sidecar_query_runtime.py` | none | Available as local read-only query surface | SIDECAR-04a added `compute_local_novelty_score`, `rank_nodes_by_reuse_centrality`, and `lookup_submission_receipt`. |
| `identity.show` | Show the local agent identity state. | `ilc identity show` | `ilc_core/cli/main.py` identity surface | none | Available after local identity init | This is local identity display, not hotkey-to-AgentID authorization. |
| `balance.check` | Return local balance report data. | `ilc balance` | `ilc_core/cli/main.py` balance surface | none | Prototype compatibility surface | SIDECAR-01 labels bare `ilc balance` as PROTOTYPE. Full per-agent balance needs richer configured local state. |
| `epoch.status` | Return current epoch status data. | `ilc epoch` | `ilc_core/cli/main.py` epoch surface | none | Prototype compatibility surface | SIDECAR-01 labels `ilc epoch` as PROTOTYPE. Consensus readback remains the stronger operator evidence path. |

## 4. Tier 2 Optional Skills

Tier 2 skills are optional harness capabilities. They are not installed through a
live root-skill runtime in this phase. Each row names the current concrete CLI,
tool, or runtime module that exists today.

| skill_id | Description | Backing CLI command or tool | Backing module or surface | Activation gate | Current status | Notes |
|---|---|---|---|---|---|---|
| `graph.submit` | Submit a truth primitive through the existing submission surface, optionally signed with a local Ed25519 hotkey. | `ilc submit --primitive ... --payload-json ... --agent-id ... --epoch ... [--signing-key file://...]` | `ilc_core/cli/d2e_submit_cli.py`; `ilc_core/epistemic/truth_primitive_sig_verifier.py` | no transfer guard; graph persistence requires `ILC_TRUTH_GRAPH_STORE_PATH` | Available as local submit surface | Unsigned compatibility remains accepted. A signature proves key possession, not AgentID authorization. |
| `attribution.readback` | Read attribution audit events for an epoch from LMDB or fallback files. | `tools/testbed/attribution_readback.py` | `ilc_core/consensus/attribution_audit_lmdb.py` | none for local readback | Operator-local tool, `PUBLIC_RC_EXCLUDE: phase_soak_tool` | Not a stable end-user CLI command and not public serving. |
| `transfer.ilc` | Submit a bounded agent-id to agent-id ILC transfer in the live-RC path. | `tools/testbed/ilc_transfer_submit.py` | `ilc_core/value_action/ilc_transfer_intent.py`; `ilc_core/value_action/ilc_transfer_ledger.py` | `ILC_TRANSFER_ENABLED = True` | Activated, bounded, operator-local tool surface | No external withdrawal, no generalized wallet adapter, no external address spend path. |
| `transfer.ecu` | Shape and validate a bounded graph-contextual ECU fast-path transfer payload. | `tools/testbed/ecu_transfer_submit.py` | `ilc_core/ecu/ecu_fast_path_intent.py`; `ilc_core/ecu/ecu_transfer_adapter.py` | `ECU_FAST_PATH_TRANSFER_ENABLED = True` | Activated, bounded, operator-local tool surface | No generalized ECU money transfer. Contribution transfers require graph context; payment transfers require express consent. |

## 5. Install Surface Disposition

The root skills pack is not currently installed by `ilc sidecar install`.
Direct read of `ilc_core/cli/main.py` shows `sidecar` and `skills` share local
sidecar discovery and recipe commands such as `list`, `inspect`, and `recipe`.
Atlas sidecar profile validation exists as `atlas sidecar-profile validate`.

There is no active `ilc sidecar install` parser path. The only install-like
branch observed is a fail-closed `ilc skills install` handler that returns
`sidecar_install_requires_clawhub_post_fix2g`; it records that ClawHub-backed
sidecar install was planned for a post-public-RC lane. Therefore this phase
must not claim a live skill installation mechanism.

Current execution model:

- Tier 1 commands are called directly through the existing CLI.
- Tier 2 actions are called through existing CLI, operator-local tools, or
  runtime modules with their own activation guards and non-claims.
- A future root skills runtime may map `skill_id` values to commands, tools, or
  modules after separate authorization.

## 6. Invocation Interface Sketch

The following JSON sketch is advisory only. It is intended to give future
runtime phases a deterministic target without making this document governing.

Request:

```json
{
  "args": {},
  "epoch": 0,
  "skill_id": "graph.query"
}
```

Response:

```json
{
  "ok": true,
  "receipt_token": "optional_sidecar_execution_receipt_token",
  "result": {}
}
```

Future integration should bind this interface to
`SidecarExecutionReceipt` from GAP-HARNESS-SIDECAR-05 so successful and failed
tool actions produce local execution receipts. This phase does not wire that
integration.

## 7. Activation Guard Requirements

- `transfer.ilc` must remain bound to `ILC_TRANSFER_ENABLED = True` and to the
  bounded agent-id transfer scope ratified by the live-RC lane.
- `transfer.ecu` must remain bound to `ECU_FAST_PATH_TRANSFER_ENABLED = True`
  and to bounded graph-contextual ECU movement.
- `graph.submit` must not imply public graph admission or durable graph
  mutation unless the configured graph store and later public graph admission
  surfaces accept the submission.
- `attribution.readback` must remain local/operator-only until a stable public
  readback command or API is separately authorized.

## 8. Non-Claims

This spec does not claim or authorize:

- skill dispatch runtime;
- skill authentication or hotkey-to-AgentID authorization;
- multi-agent skill delegation;
- ClawHub listing, OpenClaw integration, or OpenClaw skill publication;
- `ilc sidecar install` activation;
- public sidecar serving;
- public graph write admission;
- public graph fetch or P2P serving;
- public confidential multi-hop fetch;
- wallet write, spend, withdrawal, or external-address handling;
- generalized ECU money transfer;
- new value action classes;
- new CDL authority;
- activation flag changes;
- public mirror push, public RC, mainnet, or epoch transition.
