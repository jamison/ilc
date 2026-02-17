from __future__ import annotations

import json
from pathlib import Path

import pytest

import ilc_core.config as config_mod
import ilc_core.hardware as hardware_mod


def test_default_governance_config_path_is_json_even_with_yaml_loader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DummyYaml:
        @staticmethod
        def safe_load(_text: object) -> object:
            return {}

    monkeypatch.setattr(config_mod, "yaml", DummyYaml())
    assert config_mod._default_governance_config_path().suffix == ".json"


def test_governance_yaml_without_loader_falls_back_to_sibling_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    yaml_path = tmp_path / "governance_mvp.yaml"
    json_path = tmp_path / "governance_mvp.json"
    yaml_path.write_text("ecu:\n  base_costs:\n    claim.submit: 0.10\n", encoding="utf-8")
    json_path.write_text(
        json.dumps({"ecu": {"base_costs": {"claim.submit": 0.25}}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(config_mod, "yaml", None)
    cfg = config_mod.load_governance_config(str(yaml_path))
    assert cfg["ecu"]["base_costs"]["claim.submit"] == 0.25


def test_default_hardware_loader_uses_json_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ExplodingYaml:
        @staticmethod
        def safe_load(_text: object) -> object:
            raise AssertionError("yaml_loader_should_not_be_used_for_default_path")

    monkeypatch.setattr(hardware_mod, "yaml", ExplodingYaml())
    archetypes = hardware_mod.load_hardware_archetypes()
    assert "cpu" in archetypes
    assert "gpu" in archetypes


def test_hardware_yaml_without_loader_falls_back_to_sibling_json(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    yaml_path = tmp_path / "hardware_archetypes_mvp.yaml"
    json_path = tmp_path / "hardware_archetypes_mvp.json"
    yaml_path.write_text("hardware_archetypes: {}\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "hardware_archetypes": {
                    "cpu": {
                        "base_potential": 0.1,
                        "stake_fraction_min": 0.05,
                        "stake_fraction_max": 0.2,
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(hardware_mod, "yaml", None)
    archetypes = hardware_mod.load_hardware_archetypes(str(yaml_path))
    assert "cpu" in archetypes
    assert archetypes["cpu"].base_potential == 0.1
