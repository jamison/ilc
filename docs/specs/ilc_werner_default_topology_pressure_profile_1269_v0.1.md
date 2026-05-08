# ILC Werner Default Topology-Pressure Profile - Phase 1269

**Status:** Phase 1269 complete; simulation/evidence profile recorded
**Scope:** SIM-FETCH Werner profile adapter and public/economic non-authorization
**Date:** 2026-05-08

```text
werner_default_topology_pressure_profile_phase_1269.v0.1
topology_pressure_model_werner_v1_profile_recorded_phase_1269
werner_none_profile_control_preserved_phase_1269
no_werner_ecu_minting_or_ilc_settlement_phase_1269
```

## 1. Verdict

Phase 1269 records the default SIM-FETCH Werner topology-pressure profile as a
simulation/evidence adapter:

```text
ilc_core/sim/sim_fetch_01/werner_topology_pressure_profile.py
topology_pressure_model=werner_v1
```

The adapter maps `topology_pressure_model="werner_v1"` to the existing
SIM-FETCH Werner overlay controls and preserves `topology_pressure_model="none"`
as the explicit comparison profile. It emits canonical JSON evidence with hard
false flags for ECU minting, ILC settlement, public claimability, runtime
economic policy, and CDL-087 authorization.

This phase does not open or prelock a Werner CDL and does not activate runtime
economic policy.

## 2. Discovery Discipline

Exact-token audit:

- `werner_default_topology_pressure_profile_phase_1269.v0.1`
- `topology_pressure_model_werner_v1_profile_recorded_phase_1269`
- `werner_none_profile_control_preserved_phase_1269`
- `no_werner_ecu_minting_or_ilc_settlement_phase_1269`

Concept discovery searched `Werner`, `topology_pressure_model`, `werner_v1`,
`none profile`, `heat`, `pressure`, `Decimal`, `fixed-point`, `canonical JSON`,
`ECU`, `ILC`, `mint`, `settlement`, `routing`, `admission`, `cache`, and
`mirror`.

Contradiction search checked `simulation-only`, `not authorized`, `no ECU
minting`, `no ILC settlement`, `not ratified`, `blocked`, `must not`, `public
claimability`, `runtime policy`, and `CDL`.

Source expansion confirmed these controlling inputs:

- `docs/specs/ilc_werner_flow_governor_overlay_validation_1262_v0.1.md`
- `docs/specs/ilc_werner_flow_governor_cdl_decision_1263_v0.1.md`
- `docs/specs/ilc_network_transport_identity_and_value_path_forward_planning_v0.1.md`
- `ilc_core/sim/sim_fetch_01/sim_fetch_01_harness.py`
- `tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py`
- `docs/sims/sim_fetch_01/sim_fetch_01_werner_overlay_results_1238h_v0.1.json`

## 3. Profile Contract

The Phase 1269 adapter exposes two profiles:

| Profile | Meaning |
|---------|---------|
| `werner_v1` | Enables the existing SIM-FETCH Werner overlay and records the topology-pressure model explicitly. |
| `none` | Disables the Werner overlay and preserves the comparison/control profile. |

The adapter:

- rejects float anywhere in profile config or export payloads;
- preserves Decimal-safe SIM-FETCH pressure arithmetic by using string numeric
  controls and the existing harness Decimal path;
- exports canonical JSON with `sort_keys=True`, `allow_nan=False`, and compact
  separators;
- enforces max-byte export bounds;
- records non-authorization flags at top level and in SIM-FETCH aggregate
  metrics.

## 4. Non-Economic Boundary

Machine-readable boundary:

```text
no_werner_ecu_minting_or_ilc_settlement_phase_1269
```

The profile records Werner as evidence for topology pressure only. Allowed
future evidence interpretation remains limited to:

- routing reputation;
- routing weight;
- admission budget;
- cache priority;
- mirror priority.

The profile does not authorize:

- direct ECU minting from heat;
- ILC settlement from heat;
- public claimability activation;
- wallet withdrawal, transfer, or spend semantics;
- runtime economic policy deployment;
- Werner CDL opening, prelock, ratification, or register mutation;
- CDL-087 ratification or public fetch/projection-serving authorization.

## 5. Relationship to Phase 1263 Closing Conditions

Phase 1263 listed `topology_pressure_model=werner_v1` with a `"none"` comparison
profile as one closing condition for any future Werner CDL opening. Phase 1269
closes that specific profile-recording condition only.

It does not close the remaining future Werner CDL conditions:

- beta/noise decomposition;
- spectral trust threshold packet;
- public-path TransportPrincipal/admission binding;
- non-economic runtime policy skeleton;
- separate productive-credit authorization route.

## 6. Non-Claims

Phase 1269 does not authorize:

- Werner CDL opening/prelock/ratification.
- CDL register mutation.
- CDL-087 ratification.
- Runtime economic policy activation.
- ECU minting.
- ILC settlement.
- Public claimability activation.
- Wallet withdrawal, transfer, or spend semantics.
- Public RC claim.
- Public P2P exposure.
- Public fetch serving.
- Public sidecar/projection serving.
- Release-key generation.
- Release envelope production.
- v0.2 signing.
- Signed Genesis v0.1 mutation.
- Genesis Atlas mutation/regeneration/signing.
- Immutable diagnostic mutation.
- Production `commit.epoch` emission authorization.

## 7. Graph Delta

```text
graph_delta=load_bearing_code_added:ilc_core/sim/sim_fetch_01/werner_topology_pressure_profile.py -> sim_fetch/werner
graph_delta=load_bearing_spec_added:docs/specs/ilc_werner_default_topology_pressure_profile_1269_v0.1.md -> planning/werner
graph_delta=support_tests_added:tests/test_phase_1269_werner_default_topology_pressure_profile.py -> validation
graph_delta=support_only:docs/phases/phase_1269_werner_default_topology_pressure_profile_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier
```

## 8. Verification

Expected verification:

```bash
.venv/bin/python -m pytest tests/test_phase_1269_werner_default_topology_pressure_profile.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/specs ilc_core tests docs/phases/STATUS.md docs/phases/phase_1269_werner_default_topology_pressure_profile_walkthrough.md docs/PLANNING_INDEX.md
```
