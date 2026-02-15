from __future__ import annotations

from pathlib import Path


def test_run_node_uses_centralized_logging_bootstrap() -> None:
    source = Path("run_node.py").read_text(encoding="utf-8")
    assert "configure_logging()" in source
    assert "logger = logging.getLogger(__name__)" in source
    assert 'logger.info("node_daemon_starting")' in source
    assert "print(" not in source


def test_harness_econ_scenarios_uses_module_logger_only() -> None:
    source = Path("ilc_core/sim/harness_econ_scenarios.py").read_text(encoding="utf-8")
    assert "logger = logging.getLogger(__name__)" in source
    assert "logging.warning(" not in source
    assert "logging.debug(" not in source
