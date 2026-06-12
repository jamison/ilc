"""Project-level pytest configuration.

Ensures that subprocess calls within tests (which use bare "python3") resolve
to the active virtual environment's Python rather than the system Python.
Required because test files use subprocess.run(["python3", ...]) directly.
"""

import os
import subprocess
import sys
from pathlib import Path


def _reset_canary_dirty_files() -> None:
    """If the mutation canary left sentinel files, hard-reset affected probe targets.

    The canary writes /tmp/ilc_mutation_canary_dirty_<probe>.lock before mutating a
    file and removes it only after a successful revert.  If the process was killed
    mid-mutation the sentinel survives and we must restore the file before tests run.
    This prevents stale mutation tokens (e.g. v9.9, REMOVED_FOR_MUTATION) from
    poisoning the test session.
    """
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
