import logging

from ilc_core.logging_config import configure_logging


def test_configure_logging_idempotent_handler_setup() -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    try:
        root.handlers = []
        configure_logging("INFO")
        first_count = len(root.handlers)
        configure_logging("DEBUG")
        second_count = len(root.handlers)
        assert first_count == 1
        assert second_count == 1
        assert root.level == logging.DEBUG
    finally:
        root.handlers = original_handlers
        root.setLevel(original_level)


def test_configure_logging_uses_env_level_when_not_overridden(monkeypatch) -> None:
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    try:
        monkeypatch.setenv("ILC_LOG_LEVEL", "WARNING")
        root.handlers = []
        configure_logging()
        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
    finally:
        root.handlers = original_handlers
        root.setLevel(original_level)
