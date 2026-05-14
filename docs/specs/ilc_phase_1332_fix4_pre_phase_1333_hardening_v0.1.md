# ILC Phase 1332 Fix4 Pre-Phase 1333 Hardening v0.1

**Status:** PASS — Fix4 blockers closed before Phase 1333.
**Date:** 2026-05-14.
**Scope:** Pre-Phase 1333 hardening only. This document records the six Fix4
items requested after Phase 1332 and does not execute Phase 1333.

```text
phase_1332_fix4_pre_phase_1333_hardening.v0.1
private_address_endpoint_denial_phase_1332_fix4
cbor_preload_size_cap_phase_1332_fix4
package_profile_integrity_split_phase_1332_fix4
atlas_g_006_gate_split_phase_1332_fix4
source_allowlist_export_rehearsal_split_phase_1332_fix4
transport_principal_admission_params_dataclass_phase_1332_fix4
phase_1333_source_allowlist_export_execution_gate_unblocked_after_fix4
public_rc_remains_blocked_after_phase_1332_fix4
```

## 1. Fix4 Closure

| Fix4 item | Implementation | Evidence |
|-----------|----------------|----------|
| Private-address SSRF denial on outbound HTTP | `validate_peer_endpoint()` now rejects non-global address literals, localhost names, IPv6 loopback, and `inet_aton`-compatible IPv4 shorthands by default; local/private tests require explicit opt-in. `PeerManager` also rejects private peer hosts by default. | `tests/test_phase_1332_fix4_pre_1333_hardening.py` |
| CBOR pre-load size cap | `cbor_loads()` rejects inputs larger than `MAX_CANONICAL_CBOR_INPUT_BYTES` before calling `cbor2.loads`. | Focused monkeypatch test proves oversize input never reaches `cbor2.loads`. |
| Split package-profile integrity validator | `_validate_package_profile_integrity()` is now a dispatcher over per-lane validators. | Function reduced to 32 lines. Registry manifest validation still passes. |
| Split ATLAS-G-006 public-RC graph gate | The gate now delegates profile, reachability, and dependency checks to helpers. | Function reduced to 55 lines; gate output remains pass/non-authorizing. |
| Split source allowlist export rehearsal builder | Candidate preparation, classification, counts, and exclusion recording are helperized. | Function reduced to 103 lines; dry-run report regenerated. |
| TransportPrincipal admission params dataclass | Added `TransportPrincipalAdmissionParams` and retained legacy keyword compatibility while preventing mixed params/legacy calls. Local-only authorization checks moved to helper. | Builder reduced to 135 lines and 2 args. |

## 2. Non-Authorization Boundary

Fix4 does not authorize or execute source allowlist export, clean public tree
materialization, source publication, package publication, release artifact
production, release-key generation, release envelope production, release signing
material generation, signing, public RC publication/claim, public P2P/fetch
serving, public sidecar/projection serving, public confidential coordination
serving, identity bootstrap, wallet-facing actions, ECU minting, ILC settlement,
Genesis/Atlas mutation, ATLAS-G-007 through ATLAS-G-010, CDL mutation, CDL-088
opening, counsel approval, patent filing, CLA approval, trademark-policy
publication, or legal conclusion.

Phase 1333 is unblocked only with respect to the six Fix4 blockers. It remains
a sensitive future phase requiring explicit `GO Phase 1333`.

## 3. Graph Delta

```text
graph_delta=load_bearing_artifact_changed:ilc_core/network/d2d/gossip_peer_registry.py,ilc_core/network/d2d/http_gossip_transport_runtime.py,ilc_core/network/peer.py -> network/outbound-endpoint-validation
graph_delta=load_bearing_artifact_changed:ilc_core/crypto/cbor_canonical.py,ilc_core/crypto/__init__.py -> crypto/canonical-cbor-boundary
graph_delta=load_bearing_artifact_changed:ilc_core/sidecars/registry_manifest.py -> sidecars/package-profile-integrity
graph_delta=load_bearing_artifact_changed:ilc_core/rc/atlas_graph_discipline.py -> atlas-g/public-rc-graph-gate
graph_delta=load_bearing_artifact_changed:ilc_core/rc/source_allowlist_export_rehearsal.py -> rc/source-allowlist-rehearsal
graph_delta=load_bearing_artifact_changed:ilc_core/sidecars/transport_principal_admission.py -> sidecars/transport-principal-admission
graph_delta=support_tests_added:tests/test_phase_1332_fix4_pre_1333_hardening.py -> validation
graph_delta=support_only:docs/specs/ilc_phase_1332_fix4_pre_phase_1333_hardening_v0.1.md,docs/phases/phase_1332_fix4_pre_phase_1333_hardening_walkthrough.md,docs/phases/STATUS.md,docs/PLANNING_INDEX.md,docs/specs/ilc_window_1330_1342_candidate_phase_grouping_v0.1.md -> planning/frontier
```

## 4. Verification

Verification commands executed for Fix4:

```bash
python3 -m py_compile ilc_core/network/d2d/gossip_peer_registry.py ilc_core/network/d2d/http_gossip_transport_runtime.py ilc_core/network/peer.py ilc_core/crypto/cbor_canonical.py ilc_core/crypto/__init__.py ilc_core/sidecars/transport_principal_admission.py ilc_core/sidecars/registry_manifest.py ilc_core/rc/atlas_graph_discipline.py ilc_core/rc/source_allowlist_export_rehearsal.py
python3 -m py_compile tests/test_phase_1332_fix4_pre_1333_hardening.py
./.venv/bin/python -m pytest tests/test_phase_1332_fix4_pre_1333_hardening.py
./.venv/bin/python -m pytest tests/test_phase_1309_transport_principal_admission_sidecar_lifecycle_hardening.py tests/test_phase_1310_revocation_replay_admission_ban_tests.py
python3 tools/check_sensitive_runtime_coding_taboos.py
./.venv/bin/python -m pytest tests/test_sensitive_runtime_coding_taboos.py
```

`CODE_HEALTH_TOP_N=20 ./.venv/bin/python -m pytest tests/test_code_health.py -q`
still reports known carry-forward code-health findings outside the six Fix4
items, including `ConsensusEngine`, public-path preflight builders, and other
sidecar packet builders. The six Fix4 target functions are below their target
thresholds or moved behind a params object.
