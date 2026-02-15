from __future__ import annotations

import logging

import pytest

import ilc_core.config as config_mod
from ilc_core.exceptions import ConfigNotFoundError


def test_default_missing_path_warns_and_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    missing_path = tmp_path / "missing_governance.yaml"
    monkeypatch.setattr(config_mod, "_default_governance_config_path", lambda: missing_path)

    caplog.set_level(logging.WARNING)
    cfg = config_mod.load_governance_config()

    assert cfg == {}
    assert any(
        "governance_config_default_missing" in record.getMessage()
        for record in caplog.records
    )


def test_yaml_without_loader_warns_and_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    yaml_path = tmp_path / "governance_mvp.yaml"
    yaml_path.write_text("ecu:\n  base_costs:\n    claim.submit: 0.10\n", encoding="utf-8")
    monkeypatch.setattr(config_mod, "yaml", None)

    caplog.set_level(logging.WARNING)
    cfg = config_mod.load_governance_config(str(yaml_path))

    assert cfg == {}
    assert any(
        "governance_config_yaml_loader_missing" in record.getMessage()
        for record in caplog.records
    )


def test_unsupported_extension_warns_and_returns_empty(
    tmp_path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    cfg_path = tmp_path / "governance_mvp.txt"
    cfg_path.write_text("{}", encoding="utf-8")

    caplog.set_level(logging.WARNING)
    cfg = config_mod.load_governance_config(str(cfg_path))

    assert cfg == {}
    assert any(
        "governance_config_unsupported_extension" in record.getMessage()
        for record in caplog.records
    )


def test_user_missing_path_raises_and_logs_token(
    tmp_path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    missing_path = tmp_path / "not_found_governance.json"

    caplog.set_level(logging.ERROR)
    with pytest.raises(ConfigNotFoundError):
        config_mod.load_governance_config(str(missing_path))

    assert any(
        "governance_config_path_not_found" in record.getMessage()
        for record in caplog.records
    )
