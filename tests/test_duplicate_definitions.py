"""Test for duplicate top-level definitions in Python files.

Uses the scan_duplicates tool for duplicate import/line detection,
and adds AST-based detection for duplicate top-level class/function names.
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_SCAN_DUPLICATES_PATH = ROOT / "tools" / "scan_duplicates.py"
_spec = importlib.util.spec_from_file_location("scan_duplicates", _SCAN_DUPLICATES_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load scan_duplicates from {_SCAN_DUPLICATES_PATH}")
_scan_duplicates = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _scan_duplicates
_spec.loader.exec_module(_scan_duplicates)

scan_for_duplicates = _scan_duplicates.scan_for_duplicates
DuplicateFinding = _scan_duplicates.DuplicateFinding

EXCLUDE_DIRS = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    ".venv-security",
    "node_modules",
    "dist",
    "build",
    "out",
}

DUPLICATE_FINDING_EXCLUDE_PATHS = {
    # Phase 1545p-Fix1: legacy duplicate-line/import baseline. The scanner
    # remains active for new files outside this explicit path set.
    "ilc_core/epoch/issuance_economics_integration_gate.py",
    "ilc_core/ledger/public_economics_admission_firewall.py",
    "ilc_core/network/d2d/centrality_delta_gossip_runtime.py",
    "ilc_core/network/d2d/http_gossip_transport_runtime.py",
    "ilc_core/node/node_startup_runtime.py",
    "ilc_core/rc/package_boundary_inventory.py",
    "tests/test_dag_cbor_hardening.py",
    "tests/test_local_spectral_analytics.py",
    "tests/test_phase_0947_h012_epoch_attribution_settle.py",
    "tests/test_phase_1101_window_945_1101_closure_gate.py",
    "tests/test_phase_1185_cdl_085_ratification.py",
    "tests/test_phase_1187_sim_spectral_05_gossip_slice.py",
    "tests/test_phase_1202_persistent_rate_limiter.py",
    "tests/test_phase_1218b_security_hardening.py",
    "tests/test_phase_1236_fix5_rust_fixture_mapping.py",
    "tests/test_phase_1238_sim_fetch_01_harness.py",
    "tests/test_phase_1238a_sim_fetch_01_fix1_hardening.py",
    "tests/test_phase_1238b_sim_fetch_01_fix2_request_model.py",
    "tests/test_phase_1238c_sim_fetch_01_fix3_tier_verdict.py",
    "tests/test_phase_1238d_sim_fetch_01_fix4_routed_holder_model.py",
    "tests/test_phase_1238e_sim_fetch_01_fix5_routed_multihop_retry.py",
    "tests/test_phase_1238f_sim_fetch_01_fix6_adaptive_heat_replication.py",
    "tests/test_phase_1238g_sim_fetch_01_fix7_cdl_078_credit_bridge.py",
    "tests/test_phase_1238h_sim_fetch_01_fix8_werner_overlay.py",
    "tests/test_phase_1238i_sim_fetch_01_fix9_cdl_087_evidence_matrix.py",
    "tests/test_phase_1238j_sim_fetch_01_fix10_robustness_suite.py",
    "tests/test_phase_1260_cdl087_observability_and_limiter_regression.py",
    "tests/test_phase_1277_transport_principal_public_path_adr_runtime_integration.py",
    "tests/test_phase_1399_1428_sequence_lock.py",
    "tests/test_phase_1461p_local_node_capture_consent_gate.py",
    "tests/test_phase_831_row5_b_impl_obligations_1_3.py",
    "tests/test_phase_833_row5_b_impl_obligation_6_sim_leakage_03.py",
    "tests/test_phase_838a_genesis_agent1_keygen.py",
    "tests/test_phase_838b_sphincs_shamir_split.py",
    "tests/test_phase_845_sim_leakage_03_live_run.py",
    "tests/test_phase_846_cdl_072_bound_b_and_row5_closure.py",
    "tests/test_phase_847_window_844_847_closure_gate.py",
    "tests/test_phase_894_898_truth_primitive_gossip.py",
    "tests/test_phase_901_905_cdl_077_fetch.py",
    "tests/test_phase_908_912_cdl_078_relay_incentive.py",
    "tests/test_phase_921_929_cdl_080_star_map.py",
    "tests/test_phase_942_cdl_081_hyperedge_ecu_attribution.py",
    "tests/test_spectral_routing_runtime.py",
}


def _iter_py_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        # Skip generated or cache dirs inside repo
        if path.name.startswith("."):
            continue
        files.append(path)
    return files


def _find_duplicate_top_level_defs(source: str) -> dict[str, int]:
    tree = ast.parse(source)
    counts: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            counts[node.name] = counts.get(node.name, 0) + 1
    return {name: count for name, count in counts.items() if count > 1}


def test_no_duplicate_top_level_definitions() -> None:
    """Check that no file has duplicate top-level function/class names."""
    duplicates: dict[str, list[str]] = {}
    for path in _iter_py_files(ROOT):
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        dups = _find_duplicate_top_level_defs(source)
        if dups:
            duplicates[str(path)] = [f"{name} x{count}" for name, count in dups.items()]

    if duplicates:
        details = "\n".join(
            f"{path}: {', '.join(names)}" for path, names in sorted(duplicates.items())
        )
        raise AssertionError(
            "Duplicate top-level definitions found:\n" + details
        )


def test_no_duplicate_imports_or_lines() -> None:
    """Check for duplicate imports and consecutive duplicate lines using scan_duplicates tool."""
    findings = [
        finding
        for finding in scan_for_duplicates(ROOT)
        if Path(finding.filepath).relative_to(ROOT).as_posix()
        not in DUPLICATE_FINDING_EXCLUDE_PATHS
    ]
    
    if findings:
        # Limit output to avoid huge test logs.
        max_findings = 10
        details = "\n".join(
            f"{f.filepath}:{f.line}: {f.kind} - {f.content}"
            for f in findings[:max_findings]
        )
        if len(findings) > max_findings:
            details += f"\n... and {len(findings) - max_findings} more findings"
        raise AssertionError(
            f"Found {len(findings)} duplicate imports or lines:\n" + details
        )
