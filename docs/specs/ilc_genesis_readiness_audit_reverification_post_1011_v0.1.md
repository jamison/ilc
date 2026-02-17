# ILC Genesis Readiness Audit Reverification (Post-1011) v0.1

## Status
Prepared in Phase 1012.

## Source Audit
`/Users/jamstar/Downloads/ILC_Genesis_Readiness_Report.md`

## Purpose

Re-verify the external audit claims after remediation sequence phases 996-1011 and record claim-by-claim closure status with concrete evidence anchors.

## Claim Status Matrix

| Audit ID | Claim | Post-1011 status | Evidence anchors |
| --- | --- | --- | --- |
| P0-1 | `tools/` missing / README and CI broken | Closed (stale claim) | `tools/` exists; `.github/workflows/test.yml`; `tests/test_quickstart_parity_phase_998.py` |
| P0-2 | LICENSE missing | Closed | `LICENSE`; `tests/test_license_presence_phase_997.py` |
| P0-3 | Node ID divergence vs CIDv1 spec | Closed with transitional compatibility fallback | `ilc_core/types.py` (`compute_id`, `compute_canonical_id`, `compute_legacy_id`); `tests/test_node_id_dual_contract_phase_1002.py`; `tests/test_node_id_runtime_bridge_phase_1003.py`; `tests/test_node_id_migration_utility_phase_1004.py` |
| P1-1 | `server.py` module-level app instantiation side effect | Closed | `ilc_core/server.py` (`create_app` factory); `ilc_core/asgi.py`; `run_node.py`; `tests/test_server_app_factory_phase_1001.py` |
| P1-2 | duplicated `_load_key_bytes` | Closed | `ilc_core/cli/_key_utils.py`; `tests/test_cli_key_loader_dedupe_phase_999.py` |
| P1-3 | silent `except Exception: pass` patterns | Closed | `tests/test_no_silent_exception_pass_phase_1000.py` |
| P1-4 | committed `__pycache__` and `.DS_Store` | Closed (stale claim) | tracked-file scan no matches; package hygiene tests |
| P1-5 | orphan files at repo root | Closed | root legacy artifacts moved/relocated in phase 1005; `tests/test_package_hygiene_phase_1005.py` |
| P1-6 | `Z_Past_Chats/` should not ship | Closed for distribution surface (policy retention in repo) | `MANIFEST.in` prune rules; `.gitignore` policy; `tests/test_package_hygiene_phase_1005.py` |
| P1-7 | PyYAML optional divergence | Closed | `ilc_core/config.py`; `ilc_core/hardware.py`; `tests/test_config_dependency_policy_phase_1006.py` |
| P1-8 | README structure stale | Closed | `README.md`; `tests/test_quickstart_parity_phase_998.py` |
| P2-1 | no external getting-started docs | Closed | `docs/GETTING_STARTED.md`; `tests/test_getting_started_docs_phase_1010.py` |
| P2-2 | governance config params undocumented | Closed | `config/README.md`; `tests/test_operator_config_docs_phase_1008.py` |
| P2-3 | broad `except Exception` prevalence | Partially closed, policy-tracked | `docs/specs/ilc_broad_exception_boundary_policy_v0.1.md`; `tests/test_broad_exception_boundary_policy_phase_1011.py`; broad-catch count reduced in `ilc_core` from 56 to 45 |
| P2-4 | two CBOR implementations undocumented | Closed | module headers in `ilc_core/encoding/dag_cbor.py` and `ilc_core/crypto/cbor_canonical.py` |
| P2-5 | Edge/Link duality ambiguity | Closed (documented boundary) | `docs/specs/ilc_edge_link_boundary_contract_v0.1.md`; `tests/test_edge_link_boundary_phase_1007.py` |

## Residual Policy Notes

1. NodeID migration remains canonical-first with deterministic legacy fallback for non-DAG-CBOR-safe payloads; runtime bridge is intentional for compatibility.
2. `Z_Past_Chats/` remains repository-retained for historical traceability but is excluded from distribution surface by manifest policy.
3. Broad exception elimination is not complete codebase-wide; boundary-layer catches remain and are policy-governed.

## Deterministic Reverification Gate

Phase 1012 adds:

- `tools/check_genesis_readiness_audit_reverification_1012.sh`
- `tests/test_genesis_readiness_audit_reverification_gate_phase_1012.py`

The gate executes the consolidated post-remediation subset spanning phases 997-1011 and should be re-run before release tags.

## Conclusion

No unresolved P0 blockers remain under current repository policy. Remaining items are policy-accepted transitional residuals documented above.
