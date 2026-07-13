# ILC OpenClaw Two-VPS Real Execution Fix1 1575b-Fix2e v0.1

**Phase:** 1575b-Fix2e-Fix1
**Window:** 1565-1575
**Status:** retained private VPS execution record
**Sensitivity:** NON-SENSITIVE as executed: private Tailscale/VPS rehearsal, redacted target identities, no public graph writes, no wallet writes, no ECU minting, no ILC settlement, no OpenClaw/ClawHub publication, no guard clearance, and no public-RC activation.

## 1. Purpose

Phase 1575b-Fix2e completed with a correct but incomplete boundary: real VPS mode was implemented fail-closed but not executed because explicit target environment variables were absent.

Fix1 closes that execution gap by running the OpenClaw two-node integration fixture on two reachable private VPS nodes after staging a minimal private rehearsal bundle under `/home/ilcops/block6_rehearsal/`.

## 2. Execution Shape

The local operator created a minimal private bundle containing:

```text
ilc_core/sidecars/openclaw_local_capture.py
ilc_core/sidecars/openclaw_idle_mining.py
ilc_core/sidecars/openclaw_invite_bootstrap.py
tools/openclaw_two_vps_integration_rehearsal.py
```

The bundle was staged under:

```text
/home/ilcops/block6_rehearsal/fix2e_fix1_openclaw_real_vps/current
```

on two private VPS nodes. The retained public repo artifact redacts the node targets.

## 3. Runner Hardening

`tools/openclaw_two_vps_integration_rehearsal.py --real` now requires all four environment variables:

```text
ILC_FIX2E_VPS_A
ILC_FIX2E_VPS_B
ILC_FIX2E_VPS_A_WORKDIR
ILC_FIX2E_VPS_B_WORKDIR
```

The workdirs must live under `/home/ilcops/block6_rehearsal/`, must not contain whitespace, tabs, newlines, carriage returns, or `..`, and must pass a strict path-safe character allowlist before being shell-quoted for the remote `cd` command.

The runner executes the remote fixture on each configured target, retrieves only the remote evidence body, and writes a redacted local summary at:

```text
out/block6_openclaw_two_vps_fix2e_fix1/evidence_records.json
```

## 4. Result

Real VPS mode passed with two nodes:

```text
real_vps_mode.run=true
real_vps_mode.status=passed
real_vps_mode.node_count=2
```

Both remote evidence files had the same SHA-256:

```text
eaf27a98c68a70bb6d77153a45f56eaf5276b9d1e741a80b67a4f32e98ddebd1
```

The retained local Fix1 evidence file SHA-256 is:

```text
0692368adbef848d3a1c4d8c424c0c08cf508914cbc14c982c8ba73d392cb1ff
```

## 5. Remaining Named Gaps

The real VPS execution does not change the architectural gap status:

| Gap | Retained value | Reason |
|---|---|---|
| Cross-node invite replay prevention | `redeemer_key_binding_required` | Per-node nullifier stores still do not provide a shared replay registry or redeemer-key binding. |
| Distributed task reservation | `shared_coordinator_required` | Each VPS executed its local scheduler; no shared reservation substrate was introduced. |
| Semantic duplicate detection | `future_graph_intelligence_required` | Exact byte duplicate detection was rehearsed; semantic equivalence remains future graph-intelligence work. |

## 6. Non-Claims

Fix1 does not publish OpenClaw, create a ClawHub listing, submit public graph nodes, make a public installability claim, mint ECU, write wallets, settle ILC, clear runtime guards, activate public RC, transition epochs, prove cross-node replay prevention, prove distributed task reservation, or solve semantic duplicate detection.
