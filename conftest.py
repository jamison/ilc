"""Project-level pytest configuration.

Ensures that subprocess calls within tests (which use bare "python3") resolve
to the active virtual environment's Python rather than the system Python.
Required because test files use subprocess.run(["python3", ...]) directly.
"""

import os
import sys
from pathlib import Path


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
