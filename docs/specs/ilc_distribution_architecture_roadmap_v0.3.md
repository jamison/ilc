# ILC Distribution Architecture Roadmap v0.3

Status: **non-normative planning artifact** — subject to decision-log ratification
Date: 2026-02-20
Author: Claude Opus 4.6 + Codex integration pass
Supersedes: `ilc_distribution_architecture_roadmap_v0.2.md`
Depends on: `ilc_adm_001_protocol_native_bundle_distribution_v0.2.md`
Amendment reason: Add Agent SDK/CLI phase D2e, expand D3 with OpenClaw skill delivery tasks, expand D2d with epoch lifecycle/subscription tasks, and align CDL routing with post-Phase-233 numbering (`CDL-032`, `CDL-033`).

---

## 1. Strategic summary

The four-layer distribution architecture remains unchanged from v0.2. This v0.3 amendment adds the missing SDK execution lane between wire protocol and OpenClaw integration so CLI-first integration has an explicit implementation path.

---

## 2. Phase map (amended)

Existing phase groups from v0.2 remain active:
- D1 Genesis reproducibility,
- D2 Layer 0 protocol bundle schema/type system,
- D2b Layer 1 genesis state bundle,
- D2c Layer 2 epoch snapshots,
- D2d Layer 3 wire protocol,
- D3 OpenClaw integration,
- D4 Rust kernel,
- D5 Python retirement.

New in v0.3:
- **D2e Agent SDK / CLI** (new phase group, 11 tasks),
- **D3 expansion** from 8 tasks to 13 tasks,
- **D2d expansion** from 9 tasks to 11 tasks.

---

## 3. New Phase D2e: Agent SDK / CLI (11 tasks)

| Task ID | Task | Deliverable | Acceptance criteria |
|---|---|---|---|
| D2e-01 | Ratify CLI command surface | ADM-002 routed as `CDL-032` | Seven primitives + operational commands + JSON I/O contract defined |
| D2e-02 | Define CLI output schemas | Command JSON schema contract | Every command includes success and error schema |
| D2e-03 | Build Python CLI prototype | `ilc` CLI entry point | Core protocol commands functional, JSON outputs deterministic |
| D2e-04 | Build identity subsystem | `ilc identity` commands | Init/export/info works with COSE keypairs |
| D2e-05 | Build query subsystem | `ilc query` command | Shard and status filtering supported with JSON output |
| D2e-06 | Build verify subsystem | `ilc verify` command | Claim cross-check path returns structured confidence output |
| D2e-07 | Build bundle subsystem | `ilc bundle` commands | Bundle CID verification and metadata inspection |
| D2e-08 | Build epoch subsystem | `ilc epoch` commands | Epoch status/history/projection output available |
| D2e-09 | Build balance subsystem | `ilc balance` command | Agent balance, vesting, reward views exposed |
| D2e-10 | End-to-end CLI integration test | Test suite | Identity -> shard -> assert -> validate/refute -> balance full flow |
| D2e-11 | CLI help/man page | CLI docs | `--help` complete across command surface |

Exit criteria: a developer/agent with only the `ilc` CLI can perform protocol operations without framework-specific adapters.

---

## 4. D3 amendments (OpenClaw integration, +5 tasks)

D3 retains D3-01 through D3-08 from v0.2 and adds:

| Task ID | Task | Deliverable | Acceptance criteria |
|---|---|---|---|
| D3-09 | Write ILC SKILL.md for OpenClaw | `skills/ilc/SKILL.md` | Conforms to OpenClaw skill conventions |
| D3-10 | Package ILC CLI as skill binary | `skills/ilc/bins/ilc` | Binary install path and platform instructions validated |
| D3-11 | Write skill.json env config | `skills/ilc/skill.json` | Env vars and dependencies documented (`ILC_KEY_PATH`, `ILC_ENDPOINT`, `ILC_SHARD`) |
| D3-12 | Submit skill PR to OpenClaw skills repo | PR artifact | PR merged after review with working CLI payload |
| D3-13 | Reference multi-agent mining config | OpenClaw workspace/config | Three-role fleet config (asserter/validator/refuter) with heartbeat pattern |

D3 dependency notes:
- `D3-09` depends on `D2e-03`.
- `D3-12` depends on `D3-09` + `D3-10` + working CLI.
- `D3-13` depends on `D3-12`.

---

## 5. D2d amendments (+2 tasks)

D2d retains D2d-01 through D2d-09 from v0.2 and adds:

| Task ID | Task | Deliverable | Acceptance criteria |
|---|---|---|---|
| D2d-10 | Define epoch lifecycle event schema | Wire spec section | Events include epoch-start, claim-finalized, refutation-occurred, reward-vested, epoch-end |
| D2d-11 | Define subscription/notification protocol | Wire spec section | Per-shard/per-claim subscriptions, push/poll semantics, delivery guarantees |

---

## 6. Updated dependency graph

```
D1 -> D2
D2 -> D2b
D2 -> D2d -> D2e -> D3
D2 -> D2c
D2 (+ network maturity) -> D4 -> D5
```

Critical path amendment:
- `D2d -> D2e -> D3` is now explicit and required.

---

## 7. TODO routing summary (v0.3)

- Immediate scope remains D1 complete (already closed in Phase 230).
- Post-Genesis planning backlog now includes D2e tasks and expanded D2d/D3 tasks.
- D3-09+ depends on D2e-03 working CLI prototype.

---

## 8. CDL routing summary (amended)

| CDL | Subject | Layer | Status |
|---|---|---|---|
| CDL-019 | Multiplier-governance surface | 0 | open |
| CDL-020 | Protocol-native bundle schema/type system | 0 | proposed |
| CDL-021 | Rust kernel + WASM | 0 | proposed |
| CDL-022 | Genesis state bundle specification | 1 | proposed |
| CDL-023 | Epoch snapshot mechanism | 2 | proposed |
| CDL-024 | Wire protocol and transport bindings | 3 | proposed |
| CDL-025 through CDL-031 | Issuance/governance queue (Phase 233 mapping) | 0 | proposed |
| CDL-032 | CLI-first Agent SDK interface contract (ADM-002 lane) | 3 | proposed |
| CDL-033 | OpenClaw skill specification and publication contract | 3 | proposed |

---

## 9. Task-count update

Total task count is updated from **73** to **91**.

Count basis:
- prior v0.2 total: 73,
- +11 (D2e),
- +5 (D3 additions),
- +2 (D2d additions).

---

## 10. Carry-forward notes

- CDL-020 through CDL-024 remain routing labels in roadmap state and are not yet entered as formal decision-register rows.
- Decision-register formalization is tracked for integration-doc alignment lanes.

---

End of roadmap v0.3 amendment.
