# SPDX-License-Identifier: AGPL-3.0-only
"""Project-level pytest configuration.

Ensures that subprocess calls within tests (which use bare "python3") resolve
to the active virtual environment's Python rather than the system Python.
Required because test files use subprocess.run(["python3", ...]) directly.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


_HISTORICAL_CLOSURE_GATE_NAME_FRAGMENTS = (
    "accepts_blocked_override",
    "full_gate_run",
    "full_run",
    "gate_accepts_blocked",
    "gate_full_run",
    "gate_rejects_invalid",
    "gate_runs_success",
    "gate_runs_successfully",
    "gate_script_accepts",
    "gate_script_passes",
    "gate_script_rejects",
    "passes_on_valid_state",
    "snapshot_override",
    "success_path",
)

_HISTORICAL_SNAPSHOT_FILE_FRAGMENTS = (
    "test_phase_1243_package_boundary_inventory.py",
    "test_phase_1244_import_boundary_lint_and_protocol_stubs.py",
    "test_phase_1250_gap14_adapter_extraction.py",
    "test_phase_1294_claimability_package_allowlist_rehearsal.py",
    "test_phase_1323_fix3_layered_license_posture.py",
    "test_phase_1332_fix4_pre_1333_hardening.py",
    "test_phase_1388a_cdl_048_self_counsel_clearance.py",
    "test_phase_1545p_fix55_lmdb_graph_projection_classification.py",
    "test_phase_1545p_fix57_public_eligible_fiedler_minority_manual_pass.py",
    "test_phase_1545p_fix59_missing_target_materialization.py",
    "test_phase_1545p_fix59a_deferred_repair_reconcile.py",
    "test_phase_1545p_fix59c_atlas_lmdb_read_cli.py",
    "test_phase_1545p_fix60_edge_id_and_preimage_debt.py",
    "test_phase_1545p_fix62e_false_authority_cleanup.py",
    "test_phase_1545p_fix62f_runtime_source_trace.py",
    "test_phase_1545p_fix62g_governance_spine_closure.py",
    "test_phase_1545p_fix63a_procedural_support_edge_manual_audit.py",
    "test_phase_1545p_fix64_file_ref_content_hash_resolution.py",
    "test_phase_1545p_fix65_package_membership_manifest.py",
    "test_phase_1545p_fix68_orphaned_phase_node_rewiring.py",
    "test_phase_1545p_fix69_orphaned_policy_target_sim_rewiring.py",
    "test_phase_420_d2e_agent_cli.py",
    "test_phase_421_d2e_lifecycle_cli.py",
    "test_window_783_790_closure_gate.py",
    "test_window_791_800_closure_gate.py",
    "test_window_806_810_post805_resynthesis.py",
)


def _is_historical_recursive_closure_gate(item) -> bool:
    """Return True for historical shell-gate tests that recursively run windows."""
    path = Path(str(item.fspath))
    if not path.name.startswith("test_window_") or "closure_gate" not in path.name:
        return False
    if path.name.startswith("test_window_154"):
        return False
    test_name = item.name
    return any(fragment in test_name for fragment in _HISTORICAL_CLOSURE_GATE_NAME_FRAGMENTS)


def _is_historical_snapshot_assertion(item) -> bool:
    """Return True for exact historical snapshot tests invalidated by live state."""
    path = Path(str(item.fspath))
    return path.name in _HISTORICAL_SNAPSHOT_FILE_FRAGMENTS


def pytest_collection_modifyitems(config, items):  # noqa: ARG001
    """Keep historical recursive closure gates opt-in for root pytest hygiene."""
    skip_gate = pytest.mark.skip(
        reason=(
            "historical recursive closure gate; set "
            "ILC_RUN_HISTORICAL_CLOSURE_GATES=1 to run explicitly"
        )
    )
    skip_snapshot = pytest.mark.skip(
        reason=(
            "historical exact snapshot assertion; set "
            "ILC_RUN_HISTORICAL_SNAPSHOT_ASSERTIONS=1 to run explicitly"
        )
    )
    for item in items:
        if (
            os.environ.get("ILC_RUN_HISTORICAL_CLOSURE_GATES") != "1"
            and _is_historical_recursive_closure_gate(item)
        ):
            item.add_marker(skip_gate)
        if (
            os.environ.get("ILC_RUN_HISTORICAL_SNAPSHOT_ASSERTIONS") != "1"
            and _is_historical_snapshot_assertion(item)
        ):
            item.add_marker(skip_snapshot)


def _reset_canary_dirty_files() -> None:
    """If the mutation canary left sentinel files, hard-reset affected probe targets.

    The canary writes /tmp/ilc_mutation_canary_dirty_<probe>.lock before mutating a
    file and removes it only after a successful revert.  If the process was killed
    mid-mutation the sentinel survives and we must restore the file before tests run.
    This prevents stale mutation tokens (e.g. v9.9, REMOVED_FOR_MUTATION) from
    poisoning the test session.
    """
    if os.environ.get("ILC_MUTATION_CANARY_ACTIVE") == "1":
        return

    sentinel_dir = Path("/tmp")
    dirty_sentinels = list(sentinel_dir.glob("ilc_mutation_canary_dirty_*.lock"))
    if not dirty_sentinels:
        return

    # Collect probe target paths from sentinel contents.
    paths_to_reset: set[Path] = set()
    for sentinel in dirty_sentinels:
        try:
            target = Path(sentinel.read_text(encoding="utf-8").strip())
            if target.exists():
                paths_to_reset.add(target)
        except OSError:
            pass

    for target in paths_to_reset:
        result = subprocess.run(
            ["git", "checkout", "HEAD", "--", str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        # Clear all pyc variants for this module.
        cache_dir = target.parent / "__pycache__"
        for pyc in cache_dir.glob(f"{target.stem}.*.pyc"):
            try:
                pyc.unlink()
            except OSError:
                pass
        if result.returncode == 0:
            # Remove the sentinel only after the file is confirmed clean.
            for sentinel in dirty_sentinels:
                try:
                    recorded = Path(sentinel.read_text(encoding="utf-8").strip())
                    if recorded == target:
                        sentinel.unlink()
                except OSError:
                    pass
        else:
            print(
                f"conftest: canary_recovery_warning: git checkout failed for {target}"
                f" rc={result.returncode}",
                file=sys.stderr,
            )


def pytest_configure(config):
    """Prepend the venv bin directory to PATH at session start."""
    venv_bin = Path(sys.executable).parent
    current_path = os.environ.get("PATH", "")
    venv_bin_str = str(venv_bin)
    if venv_bin_str not in current_path.split(os.pathsep):
        os.environ["PATH"] = venv_bin_str + os.pathsep + current_path


def pytest_sessionstart(session):  # noqa: ARG001
    """Pre-warm the gossip module cache before any test runs.

    The mutation canary (test_mutation_canary_phase_297.py) temporarily writes
    mutated versions of centrality_delta_gossip_runtime.py to disk. If those
    modules are first imported *after* the canary writes but before it restores,
    the module-level dependency checks raise RuntimeError and poison all
    downstream gossip imports for the entire session. Pre-importing here ensures
    sys.modules is populated from the correct on-disk state before the canary
    can create a race window.

    Import order matters: gossip_transport has a circular dependency path through
    centrality_delta_gossip_runtime → epistemic → genesis → serving_receipt →
    gossip_peer_registry → gossip_transport. Import gossip and gossip_transport
    *before* centrality_delta_gossip_runtime so that gossip_transport is fully
    initialized in sys.modules when the circular path tries to re-import it.
    """
    # Recover any probe files the mutation canary left dirty (e.g. after SIGKILL).
    # Must run before module pre-warm so dirty source files are reverted first.
    _reset_canary_dirty_files()

    try:
        # Warm up modules that appear in the circular import path first.
        # The chain gossip_transport → centrality_delta_gossip_runtime →
        # epistemic → genesis.__init__ → serving_receipt → gossip_peer_registry
        # → gossip_transport creates a circular dependency.  Pre-loading
        # everything up to and including gossip_peer_registry before
        # gossip_transport ensures the circular back-reference finds a fully
        # initialized module rather than a partial one.
        import ilc_core.network.d2d.gossip                          # noqa: F401
        import ilc_core.network.d2d.interface                       # noqa: F401
        import ilc_core.network.d2d.peer                            # noqa: F401
        import ilc_core.network.d2d.gossip_peer_registry            # noqa: F401
        import ilc_core.network.d2d.gossip_transport                # noqa: F401
        import ilc_core.network.d2d.centrality_delta_gossip_runtime  # noqa: F401
        import ilc_core.network.d2d.http_gossip_transport_runtime   # noqa: F401
        import ilc_core.node.node_startup_runtime                   # noqa: F401
    except Exception:
        # If the imports genuinely fail (e.g. missing dependency) let the
        # individual tests surface the error rather than aborting the session.
        pass
